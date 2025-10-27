from django.db import models

DEC_MAX = 20
DEC_PLACES = 4

class FinancialTransaction(models.Model):
    # Keys
    pkid = models.BigIntegerField(primary_key=True)
    organizationid = models.BigIntegerField(null=True, blank=True)
    dsi = models.BigIntegerField(null=True, blank=True)

    resort = models.CharField(max_length=32, null=True, blank=True)
    locationid = models.CharField(max_length=32, null=True, blank=True)  

    trx_no = models.BigIntegerField(null=True, blank=True)               
    fintransactionid = models.BigIntegerField(null=True, blank=True)     
    reservationid = models.BigIntegerField(null=True, blank=True)        
    parentfintransid = models.BigIntegerField(null=True, blank=True)     
    depositlinkfintransid = models.BigIntegerField(null=True, blank=True)
    packagelinkfintransid = models.BigIntegerField(null=True, blank=True)

    profileid = models.BigIntegerField(null=True, blank=True)            
    cashierid = models.BigIntegerField(null=True, blank=True)
    authemployeeid = models.BigIntegerField(null=True, blank=True)
    accountid = models.CharField(max_length=64, null=True, blank=True)   
    room = models.CharField(max_length=32, null=True, blank=True)
    roomid = models.CharField(max_length=32, null=True, blank=True)
    folio_no = models.CharField(max_length=64, null=True, blank=True)
    folio_type = models.CharField(max_length=32, null=True, blank=True)
    org_folio_type = models.CharField(max_length=32, null=True, blank=True)

    # Times
    business_date = models.DateField(null=True, blank=True)
    trx_date = models.DateTimeField(null=True, blank=True)
    posting_date = models.DateTimeField(null=True, blank=True)
    transaction_posting_date = models.DateField(null=True, blank=True)
    insert_date = models.DateTimeField(null=True, blank=True)
    ar_transfer_date = models.DateTimeField(null=True, blank=True)
    jrn_update_dttm = models.DateTimeField(null=True, blank=True)
    jrn_update_date = models.DateField(null=True, blank=True)

    trx_code = models.CharField(max_length=32, null=True, blank=True)
    ft_subtype = models.CharField(max_length=8, null=True, blank=True)
    trx_type = models.CharField(max_length=16, null=True, blank=True)            
    transaction_status = models.CharField(max_length=16, null=True, blank=True)  

    rate_code = models.CharField(max_length=64, null=True, blank=True)
    market_code = models.CharField(max_length=64, null=True, blank=True)
    source_code = models.CharField(max_length=64, null=True, blank=True)
    tc_group = models.CharField(max_length=64, null=True, blank=True)
    tc_subgroup = models.CharField(max_length=64, null=True, blank=True)
    product = models.CharField(max_length=64, null=True, blank=True)

    # Currency
    currency = models.CharField(max_length=16, null=True, blank=True)
    contract_currency = models.CharField(max_length=16, null=True, blank=True)
    parallel_currency = models.CharField(max_length=16, null=True, blank=True)
    exchange_rate = models.DecimalField(max_digits=DEC_MAX, decimal_places=DEC_PLACES, null=True, blank=True)
    euro_exchange_rate = models.DecimalField(max_digits=DEC_MAX, decimal_places=DEC_PLACES, null=True, blank=True)
    exchange_date = models.DateTimeField(null=True, blank=True)
    exchange_type = models.CharField(max_length=32, null=True, blank=True)

    # Amounts
    price_per_unit = models.DecimalField(max_digits=DEC_MAX, decimal_places=DEC_PLACES, null=True, blank=True)
    quantity = models.DecimalField(max_digits=DEC_MAX, decimal_places=DEC_PLACES, null=True, blank=True)
    posted_amount = models.DecimalField(max_digits=DEC_MAX, decimal_places=DEC_PLACES, null=True, blank=True)
    trx_amount = models.DecimalField(max_digits=DEC_MAX, decimal_places=DEC_PLACES, null=True, blank=True)
    cc_trx_fee_amount = models.DecimalField(max_digits=DEC_MAX, decimal_places=DEC_PLACES, null=True, blank=True)
    gross_amount = models.DecimalField(max_digits=DEC_MAX, decimal_places=DEC_PLACES, null=True, blank=True)
    net_amount = models.DecimalField(max_digits=DEC_MAX, decimal_places=DEC_PLACES, null=True, blank=True)
    revenue_amt = models.DecimalField(max_digits=DEC_MAX, decimal_places=DEC_PLACES, null=True, blank=True)
    non_revenue_amount = models.DecimalField(max_digits=DEC_MAX, decimal_places=DEC_PLACES, null=True, blank=True)

    vat_amount = models.DecimalField(max_digits=DEC_MAX, decimal_places=DEC_PLACES, null=True, blank=True)
    c_vat_amount = models.DecimalField(max_digits=DEC_MAX, decimal_places=DEC_PLACES, null=True, blank=True)

    # Credit/Debit
    guest_account_credit = models.DecimalField(max_digits=DEC_MAX, decimal_places=DEC_PLACES, null=True, blank=True)
    guest_account_debit = models.DecimalField(max_digits=DEC_MAX, decimal_places=DEC_PLACES, null=True, blank=True)
    cashier_credit = models.DecimalField(max_digits=DEC_MAX, decimal_places=DEC_PLACES, null=True, blank=True)
    cashier_debit = models.DecimalField(max_digits=DEC_MAX, decimal_places=DEC_PLACES, null=True, blank=True)
    package_credit = models.DecimalField(max_digits=DEC_MAX, decimal_places=DEC_PLACES, null=True, blank=True)
    package_debit = models.DecimalField(max_digits=DEC_MAX, decimal_places=DEC_PLACES, null=True, blank=True)
    dep_led_credit = models.DecimalField(max_digits=DEC_MAX, decimal_places=DEC_PLACES, null=True, blank=True)
    dep_led_debit = models.DecimalField(max_digits=DEC_MAX, decimal_places=DEC_PLACES, null=True, blank=True)
    ar_led_credit = models.DecimalField(max_digits=DEC_MAX, decimal_places=DEC_PLACES, null=True, blank=True)
    ar_led_debit = models.DecimalField(max_digits=DEC_MAX, decimal_places=DEC_PLACES, null=True, blank=True)

    # Flags (Y/N)
    iscreditflag = models.CharField(max_length=1, null=True, blank=True)
    isdebitflag = models.CharField(max_length=1, null=True, blank=True)
    taxinclusiveflag = models.CharField(max_length=1, null=True, blank=True)
    taxgeneratedflag = models.CharField(max_length=1, null=True, blank=True)
    taxdeferredflag = models.CharField(max_length=1, null=True, blank=True)
    deferred_yn = models.CharField(max_length=1, null=True, blank=True)
    processed8300flag = models.CharField(max_length=1, null=True, blank=True)
    fixedchargesflag = models.CharField(max_length=1, null=True, blank=True)
    tacommissionableflag = models.CharField(max_length=1, null=True, blank=True)
    onholdflag = models.CharField(max_length=1, null=True, blank=True)
    adjustmentflag = models.CharField(max_length=1, null=True, blank=True)
    displayflag = models.CharField(max_length=1, null=True, blank=True)
    archargetransferflag = models.CharField(max_length=1, null=True, blank=True)
    deleted_flag = models.CharField(max_length=1, null=True, blank=True)
    settlement_flag = models.CharField(max_length=1, null=True, blank=True)

    # Country fields
    country_code = models.CharField(max_length=8, null=True, blank=True)
    country = models.CharField(max_length=64, null=True, blank=True)

    rep_tc_group = models.CharField(max_length=64, null=True, blank=True)
    tc_group_desc = models.CharField(max_length=256, null=True, blank=True)
    rep_tc_subgroup = models.CharField(max_length=64, null=True, blank=True)
    tc_subgroup_desc = models.CharField(max_length=256, null=True, blank=True)
    rep_trx_code = models.CharField(max_length=64, null=True, blank=True)
    trx_code_desc = models.CharField(max_length=256, null=True, blank=True)
    rep_product = models.CharField(max_length=64, null=True, blank=True)

    class Meta:
        db_table = "financial_transaction"  
        indexes = [
            models.Index(fields=["business_date"]),
            models.Index(fields=["resort", "business_date"]),
            models.Index(fields=["trx_code"]),
            models.Index(fields=["tc_group"]),
        ]

    def __str__(self):
        return f"FT {self.trx_no} @ {self.business_date} ({self.resort})"
