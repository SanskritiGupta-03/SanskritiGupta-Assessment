from django.core.management.base import BaseCommand
from core.models_ft import FinancialTransaction as FT
import csv
from datetime import datetime

DATE_FMT = "%Y-%m-%d"
DATETIME_FMT = "%Y-%m-%d %H:%M:%S"

def parse_date(s):
    if not s: return None
    try:
        return datetime.strptime(s[:10], DATE_FMT).date()
    except Exception:
        return None

def parse_dt(s):
    if not s: return None
    for fmt in (DATETIME_FMT, "%Y-%m-%dT%H:%M:%S"):
        try:
            return datetime.strptime(s[:19], fmt)
        except Exception:
            pass
    return None

def to_decimal(s):
    if s in (None, "", "NULL"): return None
    try:
        return float(s)
    except Exception:
        return None

class Command(BaseCommand):
    help = "Load FinancialTransaction rows from a CSV (headers must match model field names)."

    def add_arguments(self, parser):
        parser.add_argument("csv_path", type=str)
        parser.add_argument("--truncate", action="store_true", help="Delete existing rows first")

    def handle(self, *args, **opts):
        path = opts["csv_path"]
        truncate = opts["truncate"]

        if truncate:
            self.stdout.write("Truncating financial_transaction ...")
            FT.objects.all().delete()

        count = 0
        with open(path, newline="", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            for row in reader:
                obj = FT(
                    pkid=int(row["pkid"]),
                    organizationid=int(row["organizationid"]) if row.get("organizationid") else None,
                    dsi=int(row["dsi"]) if row.get("dsi") else None,
                    resort=row.get("resort") or None,
                    locationid=row.get("locationid") or None,
                    trx_no=int(row["trx_no"]) if row.get("trx_no") else None,
                    fintransactionid=int(row["fintransactionid"]) if row.get("fintransactionid") else None,
                    reservationid=int(row["reservationid"]) if row.get("reservationid") else None,
                    parentfintransid=int(row["parentfintransid"]) if row.get("parentfintransid") else None,
                    depositlinkfintransid=int(row["depositlinkfintransid"]) if row.get("depositlinkfintransid") else None,
                    packagelinkfintransid=int(row["packagelinkfintransid"]) if row.get("packagelinkfintransid") else None,
                    profileid=int(row["profileid"]) if row.get("profileid") else None,
                    cashierid=int(row["cashierid"]) if row.get("cashierid") else None,
                    authemployeeid=int(row["authemployeeid"]) if row.get("authemployeeid") else None,
                    accountid=row.get("accountid") or None,
                    room=row.get("room") or None,
                    roomid=row.get("roomid") or None,
                    folio_no=row.get("folio_no") or None,
                    folio_type=row.get("folio_type") or None,
                    org_folio_type=row.get("org_folio_type") or None,
                    business_date=parse_date(row.get("business_date")),
                    trx_date=parse_dt(row.get("trx_date")),
                    posting_date=parse_dt(row.get("posting_date")),
                    transaction_posting_date=parse_date(row.get("transaction_posting_date")),
                    insert_date=parse_dt(row.get("insert_date")),
                    ar_transfer_date=parse_dt(row.get("ar_transfer_date")),
                    jrn_update_dttm=parse_dt(row.get("jrn_update_dttm")),
                    jrn_update_date=parse_date(row.get("jrn_update_date")),
                    trx_code=row.get("trx_code") or None,
                    ft_subtype=row.get("ft_subtype") or None,
                    trx_type=row.get("trx_type") or None,
                    transaction_status=row.get("transaction_status") or None,
                    rate_code=row.get("rate_code") or None,
                    market_code=row.get("market_code") or None,
                    source_code=row.get("source_code") or None,
                    tc_group=row.get("tc_group") or None,
                    tc_subgroup=row.get("tc_subgroup") or None,
                    product=row.get("product") or None,
                    currency=row.get("currency") or None,
                    contract_currency=row.get("contract_currency") or None,
                    parallel_currency=row.get("parallel_currency") or None,
                    exchange_rate=to_decimal(row.get("exchange_rate")),
                    euro_exchange_rate=to_decimal(row.get("euro_exchange_rate")),
                    exchange_date=parse_dt(row.get("exchange_date")),
                    exchange_type=row.get("exchange_type") or None,
                    price_per_unit=to_decimal(row.get("price_per_unit")),
                    quantity=to_decimal(row.get("quantity")),
                    posted_amount=to_decimal(row.get("posted_amount")),
                    trx_amount=to_decimal(row.get("trx_amount")),
                    cc_trx_fee_amount=to_decimal(row.get("cc_trx_fee_amount")),
                    gross_amount=to_decimal(row.get("gross_amount")),
                    net_amount=to_decimal(row.get("net_amount")),
                    revenue_amt=to_decimal(row.get("revenue_amt")),
                    non_revenue_amount=to_decimal(row.get("non_revenue_amount")),
                    vat_amount=to_decimal(row.get("vat_amount")),
                    c_vat_amount=to_decimal(row.get("c_vat_amount")),
                    guest_account_credit=to_decimal(row.get("guest_account_credit")),
                    guest_account_debit=to_decimal(row.get("guest_account_debit")),
                    cashier_credit=to_decimal(row.get("cashier_credit")),
                    cashier_debit=to_decimal(row.get("cashier_debit")),
                    package_credit=to_decimal(row.get("package_credit")),
                    package_debit=to_decimal(row.get("package_debit")),
                    dep_led_credit=to_decimal(row.get("dep_led_credit")),
                    dep_led_debit=to_decimal(row.get("dep_led_debit")),
                    ar_led_credit=to_decimal(row.get("ar_led_credit")),
                    ar_led_debit=to_decimal(row.get("ar_led_debit")),
                    iscreditflag=(row.get("iscreditflag") or None),
                    isdebitflag=(row.get("isdebitflag") or None),
                    taxinclusiveflag=(row.get("taxinclusiveflag") or None),
                    taxgeneratedflag=(row.get("taxgeneratedflag") or None),
                    taxdeferredflag=(row.get("taxdeferredflag") or None),
                    deferred_yn=(row.get("deferred_yn") or None),
                    processed8300flag=(row.get("processed8300flag") or None),
                    fixedchargesflag=(row.get("fixedchargesflag") or None),
                    tacommissionableflag=(row.get("tacommissionableflag") or None),
                    onholdflag=(row.get("onholdflag") or None),
                    adjustmentflag=(row.get("adjustmentflag") or None),
                    displayflag=(row.get("displayflag") or None),
                    archargetransferflag=(row.get("archargetransferflag") or None),
                    deleted_flag=(row.get("deleted_flag") or None),
                    settlement_flag=(row.get("settlement_flag") or None),
                    country_code=row.get("country_code") or None,
                    country=row.get("country") or None,
                    rep_tc_group=row.get("rep_tc_group") or None,
                    tc_group_desc=row.get("tc_group_desc") or None,
                    rep_tc_subgroup=row.get("rep_tc_subgroup") or None,
                    tc_subgroup_desc=row.get("tc_subgroup_desc") or None,
                    rep_trx_code=row.get("rep_trx_code") or None,
                    trx_code_desc=row.get("trx_code_desc") or None,
                    rep_product=row.get("rep_product") or None,
                )
                obj.save()
                count += 1

        self.stdout.write(self.style.SUCCESS(f"Loaded {count} rows into financial_transaction"))
