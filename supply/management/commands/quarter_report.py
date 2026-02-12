# supply/management/commands/quarter_report.py
from django.core.management.base import BaseCommand
from django.db.models import Sum
from datetime import date, timedelta
from supply.models import Hospital, HospitalDelivery, ConsumptionRule, Reagent, WarehouseStock

class Command(BaseCommand):
    help = "Generate quarterly delivered qty per hospital and forecast warehouse needs"

    def add_arguments(self, parser):
        parser.add_argument('--days', type=int, default=90, help='Period in days (default 90)')

    def handle(self, *args, **options):
        days = options['days']
        since = date.today() - timedelta(days=days)
        self.stdout.write(f"Quarterly report since {since}")
        reagents = Reagent.objects.all()
        for hosp in Hospital.objects.all():
            self.stdout.write(f"Hospital: {hosp.name}")
            for reagent in reagents:
                delivered = HospitalDelivery.objects.filter(hospital=hosp, reagent=reagent, date__gte=since).aggregate(Sum('qty_packs'))['qty_packs__sum'] or 0
                self.stdout.write(f"  - {reagent.name}: delivered packs in period = {delivered}")
        # Warehouse forecast simple:
        self.stdout.write("\nWarehouse status and simple demand calc:")
        for stock in WarehouseStock.objects.select_related('reagent'):
            # sum delivered overall period as approximate usage
            used = HospitalDelivery.objects.filter(reagent=stock.reagent, date__gte=since).aggregate(Sum('qty_packs'))['qty_packs__sum'] or 0
            monthly_avg = used / (days/30.0) if days>0 else 0
            packs_left = stock.quantity_packs
            months_remaining = packs_left / monthly_avg if monthly_avg>0 else 'N/A'
            self.stdout.write(f"{stock.reagent.name}: left {packs_left} packs, monthly avg usage={monthly_avg:.1f}, months remaining={months_remaining}")
