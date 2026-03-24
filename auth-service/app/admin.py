from django.contrib import admin
from .models import Staff, StaffSession


@admin.register(Staff)
class StaffAdmin(admin.ModelAdmin):
    list_display = ["staff_id", "email", "full_name", "role", "department", "is_active"]
    list_filter = ["role", "department", "is_active"]
    search_fields = ["email", "first_name", "last_name"]


@admin.register(StaffSession)
class StaffSessionAdmin(admin.ModelAdmin):
    list_display = ["session_id", "staff", "created_at", "expires_at", "is_active"]
    list_filter = ["is_active"]
