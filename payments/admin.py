from django.contrib import admin

from .models import Payment


@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    list_display = ["transaction_id", "provider", "order", "status", "created_at"]
    list_filter = ["provider", "status"]
    search_fields = ["transaction_id"]
    readonly_fields = ["raw_response"]
