# supply/admin.py
from django.contrib import admin
from .models import (
    Hospital,
    Analyzer,
    HospitalAnalyzer,
    Reagent,
    WarehouseStock,
    StockMovement,
    HospitalDelivery,
    HospitalDeliveryItem,
    ConsumptionRule,
    ConsumptionProfile
)

admin.site.register(ConsumptionProfile)

# ---------- Analyzer ----------
@admin.register(Analyzer)
class AnalyzerAdmin(admin.ModelAdmin):
    list_display = ('name', 'model_code')
    search_fields = ('name', 'model_code')


# ---------- HospitalAnalyzer Inline ----------
class HospitalAnalyzerInline(admin.TabularInline):
    model = HospitalAnalyzer
    extra = 1


# ---------- Hospital ----------
@admin.register(Hospital)
class HospitalAdmin(admin.ModelAdmin):
    list_display = ('name','contact_person', 'phone')
    search_fields = ('name',)
    inlines = [HospitalAnalyzerInline]


# ---------- HospitalAnalyzer ----------
@admin.register(HospitalAnalyzer)
class HospitalAnalyzerAdmin(admin.ModelAdmin):
    list_display = (
        'hospital',
        'analyzer',
        'serial_number',
        'installation_date',
    )
    list_filter = ('hospital', 'analyzer')
    search_fields = (
        'hospital__name',
        'analyzer__name',
        'serial_number',
    )


# ---------- Other Models ----------
admin.site.register(Reagent)
admin.site.register(WarehouseStock)
admin.site.register(ConsumptionRule)

@admin.register(StockMovement)
class StockMovementAdmin(admin.ModelAdmin):
    list_display = ('reagent', 'movement_type', 'quantity', 'created_at')
    list_filter = ('movement_type', 'reagent')

# ---------- Delivery ----------
class HospitalDeliveryItemInline(admin.TabularInline):
    model = HospitalDeliveryItem
    extra = 1


@admin.register(HospitalDelivery)
class HospitalDeliveryAdmin(admin.ModelAdmin):
    inlines = [HospitalDeliveryItemInline]
    list_display = ("hospital", "delivered_at")