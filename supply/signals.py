from django.db.models.signals import post_delete, post_save, pre_save
from django.dispatch import receiver
from django.db import transaction
from .models import HospitalDeliveryItem, WarehouseStock


@receiver(post_delete, sender=HospitalDeliveryItem)
def return_stock_on_item_delete(sender, instance, **kwargs):
    """
    يرجع الريجينت للستوك عند حذف أي Item
    """
    if instance.reagent:
        stock = WarehouseStock.objects.select_for_update().get(
            reagent=instance.reagent
        )
        stock.quantity_packs += instance.quantity_packs
        stock.save()
