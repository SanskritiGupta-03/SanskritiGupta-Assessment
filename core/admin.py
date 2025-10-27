from django.contrib import admin
from .models_ft import FinancialTransaction

@admin.register(FinancialTransaction)
class FinancialTransactionAdmin(admin.ModelAdmin):
    list_display = ("trx_no", "business_date", "resort", "trx_code", "gross_amount", "net_amount", "revenue_amt", "transaction_status")
    list_filter = ("resort", "trx_code", "transaction_status", "business_date")
    search_fields = ("trx_no", "reservationid", "accountid", "profileid", "folio_no")

