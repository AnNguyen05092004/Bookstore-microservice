from django.contrib import admin
from .models import Payment, PaymentTransaction, Refund


@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    list_display = [
        "payment_id",
        "order_id",
        "payment_method",
        "amount",
        "status",
        "created_at",
    ]
    list_filter = ["status", "payment_method"]


@admin.register(PaymentTransaction)
class PaymentTransactionAdmin(admin.ModelAdmin):
    list_display = [
        "transaction_id",
        "payment",
        "gateway",
        "response_code",
        "transaction_time",
    ]


@admin.register(Refund)
class RefundAdmin(admin.ModelAdmin):
    list_display = ["refund_id", "payment", "amount", "status", "created_at"]
