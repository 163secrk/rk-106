from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import User


@admin.register(User)
class CustomUserAdmin(UserAdmin):
    list_display = ('username', 'name', 'role', 'is_staff', 'is_active')
    list_filter = ('role', 'is_staff', 'is_active')
    search_fields = ('username', 'name')

    fieldsets = UserAdmin.fieldsets + (
        ('额外信息', {'fields': ('name', 'role')}),
    )

    add_fieldsets = UserAdmin.add_fieldsets + (
        ('额外信息', {'fields': ('name', 'role')}),
    )
