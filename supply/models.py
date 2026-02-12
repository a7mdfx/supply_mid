# supply/models.py
from django.db import models, transaction
from django.core.exceptions import ValidationError
from django.contrib.auth import get_user_model
User = get_user_model()

class Hospital(models.Model):
    name = models.CharField(max_length=200)
    contact_person = models.CharField(max_length=200, blank=True)
    phone = models.CharField(max_length=50, blank=True)
    def __str__(self): return str(self.name) + " - " 
    
class Analyzer(models.Model):
    name = models.CharField(max_length=100)  # مثال: "Yumizen H500"
    model_code = models.CharField(max_length=50, blank=True, null=True)  # مثال: H500 أو H550E

    def __str__(self):
        
        return self.name
    
class HospitalAnalyzer(models.Model):
    hospital = models.ForeignKey(Hospital, on_delete=models.CASCADE)
    analyzer = models.ForeignKey(Analyzer, on_delete=models.CASCADE)
    serial_number = models.CharField(max_length=100, blank=True, null=True)
    installation_date = models.DateField(blank=True, null=True)

    class Meta:
        unique_together = ('hospital', 'serial_number')

    def __str__(self):
        return f"{self.hospital.name} - {self.analyzer.name} ({self.serial_number})"



class Reagent(models.Model):
    name = models.CharField(max_length=200)
    unit = models.CharField(max_length=20, default='bottle')  # bottle | ml
    pack_volume_ml = models.FloatField(null=True, blank=True)  # e.g. 1000
    def __str__(self): return self.name

class WarehouseStock(models.Model):
    reagent = models.OneToOneField(Reagent, on_delete=models.CASCADE)
    quantity_packs = models.PositiveIntegerField(default=0)
    last_updated = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.reagent.name} - {self.quantity_packs} bottles"

class StockMovement(models.Model):
    IN = "IN"
    OUT = "OUT"

    MOVEMENT_TYPES = [
        (IN, "Stock In"),
        (OUT, "Stock Out"),
    ]

    reagent = models.ForeignKey(Reagent, on_delete=models.CASCADE)
    movement_type = models.CharField(max_length=3, choices=MOVEMENT_TYPES)
    quantity = models.PositiveIntegerField()
    created_at = models.DateTimeField(auto_now_add=True)
    note = models.CharField(max_length=255, blank=True)

    def save(self, *args, **kwargs):
        from django.db import transaction

        with transaction.atomic():
            stock, _ = WarehouseStock.objects.get_or_create(
                reagent=self.reagent
            )

            if self.movement_type == self.IN:
                stock.quantity_packs += self.quantity
            else:
                if stock.quantity_packs < self.quantity:
                    raise ValidationError("Not enough stock")
                stock.quantity_packs -= self.quantity

            stock.save()

            super().save(*args, **kwargs)

    def __str__(self):
        sign = "+" if self.movement_type == self.IN else "-"
        return f"{self.reagent.name} {sign}{self.quantity}"
class HospitalDelivery(models.Model):
    hospital = models.ForeignKey(Hospital, on_delete=models.CASCADE)
    delivered_at = models.DateTimeField(auto_now_add=True)
    note = models.TextField(blank=True)

    def __str__(self):
        return f"Delivery to {self.hospital.name} - {self.delivered_at.date()}"
    
class HospitalDeliveryItem(models.Model):
    delivery = models.ForeignKey(
        HospitalDelivery,
        related_name="items",
        on_delete=models.CASCADE
    )
    reagent = models.ForeignKey(Reagent, on_delete=models.CASCADE)
    quantity_packs = models.PositiveIntegerField()

    def __str__(self):
        return f"{self.reagent.name} - {self.quantity_packs}"
    def save(self, *args, **kwargs):
        with transaction.atomic():

            # لو تعديل
            if self.pk:
                old = HospitalDeliveryItem.objects.select_for_update().get(pk=self.pk)
                old_stock = WarehouseStock.objects.select_for_update().get(
                    reagent=old.reagent
                )
                old_stock.quantity_packs += old.quantity_packs
                old_stock.save()

            # خصم الجديد
            stock = WarehouseStock.objects.select_for_update().get(
                reagent=self.reagent
            )

            if stock.quantity_packs < self.quantity_packs:
                raise ValidationError(
                    f"Not enough stock for {self.reagent.name}. "
                    f"Available: {stock.quantity_packs}"
                )

            stock.quantity_packs -= self.quantity_packs
            stock.save()

            super().save(*args, **kwargs)

    


class ConsumptionRule(models.Model):
    reagent = models.OneToOneField(Reagent, on_delete=models.CASCADE)
    
    ml_per_test = models.FloatField(
        null=True, blank=True,
        help_text="Consumption per blood test (ml)"
    )

    ml_per_wash = models.FloatField(
        null=True, blank=True,
        help_text="Consumption per cleaning wash (ml)"
    )

    washes_per_week = models.PositiveIntegerField(
        default=0,
        help_text="Number of washes per week"
    )

    def monthly_consumption_ml(self, tests_per_day=0):
        """Total monthly consumption in ml"""
        monthly_tests = tests_per_day * 30
        tests_ml = (self.ml_per_test or 0) * monthly_tests
        washes_ml = (self.ml_per_wash or 0) * self.washes_per_week * 4
        return tests_ml + washes_ml

    def monthly_bottles(self, tests_per_day=0):
        """Total bottles needed per month"""
        total_ml = self.monthly_consumption_ml(tests_per_day)
        return total_ml / self.reagent.bottle_volume_ml

    def __str__(self):
        return f"Rule for {self.reagent.name}"



class ConsumptionProfile(models.Model):
    hospital = models.ForeignKey(Hospital, on_delete=models.CASCADE)
    period_months = models.IntegerField(default=3)

    samples_per_day = models.IntegerField()

    diluent_qty = models.FloatField()
    whitediff_qty = models.FloatField()
    cleaner_qty = models.FloatField()
    minoclair_qty = models.FloatField()

    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.hospital.name} - {self.period_months} months"
