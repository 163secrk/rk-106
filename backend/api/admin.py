from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import User, Product, Process, WorkOrder, WorkOrderProcess, WorkReport, ReworkTask


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


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ('name', 'code', 'spec', 'created_at')
    search_fields = ('name', 'code')


@admin.register(Process)
class ProcessAdmin(admin.ModelAdmin):
    list_display = ('name', 'code', 'price', 'created_at')
    search_fields = ('name', 'code')


@admin.register(WorkOrder)
class WorkOrderAdmin(admin.ModelAdmin):
    list_display = ('order_no', 'product', 'quantity', 'deadline', 'status', 'created_by', 'created_at')
    list_filter = ('status', 'created_at')
    search_fields = ('order_no', 'product__name')


@admin.register(WorkOrderProcess)
class WorkOrderProcessAdmin(admin.ModelAdmin):
    list_display = ('work_order', 'process', 'reported_quantity', 'passed_quantity')
    list_filter = ('work_order__status',)
    search_fields = ('work_order__order_no', 'process__name')


@admin.register(WorkReport)
class WorkReportAdmin(admin.ModelAdmin):
    list_display = ('work_order', 'work_order_process', 'worker', 'quantity', 'passed_quantity', 'rework_quantity', 'scrapped_quantity', 'status', 'is_locked', 'inspector', 'created_at')
    list_filter = ('status', 'is_locked', 'created_at')
    search_fields = ('work_order__order_no', 'worker__name', 'inspector__name')


@admin.register(ReworkTask)
class ReworkTaskAdmin(admin.ModelAdmin):
    list_display = ('work_report', 'worker', 'quantity', 'status', 'created_at')
    list_filter = ('status', 'created_at')
    search_fields = ('worker__name', 'work_report__work_order__order_no')
