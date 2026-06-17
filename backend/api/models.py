from django.db import models
from django.contrib.auth.models import AbstractUser


class User(AbstractUser):
    ROLE_CHOICES = (
        ('admin', '管理员'),
        ('team_leader', '组长'),
        ('worker', '工人'),
        ('inspector', '质检员'),
    )

    name = models.CharField(max_length=50, verbose_name='真实姓名')
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='worker', verbose_name='角色')

    class Meta:
        verbose_name = '用户'
        verbose_name_plural = verbose_name

    def __str__(self):
        return self.name or self.username


class Product(models.Model):
    name = models.CharField(max_length=100, verbose_name='产品名称')
    code = models.CharField(max_length=50, unique=True, verbose_name='产品编号')
    spec = models.CharField(max_length=200, blank=True, verbose_name='规格')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')

    class Meta:
        verbose_name = '产品'
        verbose_name_plural = verbose_name
        ordering = ['-created_at']

    def __str__(self):
        return self.name


class Process(models.Model):
    name = models.CharField(max_length=50, verbose_name='工序名称')
    code = models.CharField(max_length=50, unique=True, verbose_name='工序编号')
    price = models.DecimalField(max_digits=10, decimal_places=2, default=0, verbose_name='默认工价')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')

    class Meta:
        verbose_name = '工序'
        verbose_name_plural = verbose_name
        ordering = ['id']

    def __str__(self):
        return self.name


class ProductProcess(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='product_processes', verbose_name='产品')
    process = models.ForeignKey(Process, on_delete=models.PROTECT, verbose_name='工序')
    order_index = models.IntegerField(default=0, verbose_name='工序顺序')
    unit_price = models.DecimalField(max_digits=10, decimal_places=4, default=0, verbose_name='计件单价')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')

    class Meta:
        verbose_name = '产品工序'
        verbose_name_plural = verbose_name
        ordering = ['product__id', 'order_index']
        unique_together = ('product', 'process')

    def __str__(self):
        return f'{self.product.name} - {self.process.name}'


class WorkOrder(models.Model):
    STATUS_CHOICES = (
        ('pending', '待生产'),
        ('in_progress', '生产中'),
        ('completed', '已完成'),
    )

    order_no = models.CharField(max_length=50, unique=True, verbose_name='工单号')
    product = models.ForeignKey(Product, on_delete=models.PROTECT, verbose_name='产品')
    quantity = models.IntegerField(verbose_name='生产数量')
    deadline = models.DateField(verbose_name='交付截止日期')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending', verbose_name='状态')
    created_by = models.ForeignKey(User, on_delete=models.PROTECT, related_name='created_orders', verbose_name='创建人')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='更新时间')
    has_report = models.BooleanField(default=False, verbose_name='是否已有报工')

    class Meta:
        verbose_name = '生产工单'
        verbose_name_plural = verbose_name
        ordering = ['-created_at']

    def __str__(self):
        return self.order_no

    def update_status(self):
        total_processes = self.processes.count()
        if total_processes == 0:
            self.status = 'pending'
            return

        completed_processes = 0
        for op in self.processes.all():
            if op.reported_quantity >= self.quantity:
                completed_processes += 1

        if self.has_report and completed_processes < total_processes:
            self.status = 'in_progress'
        elif completed_processes == total_processes:
            self.status = 'completed'
        else:
            self.status = 'pending'
        self.save()

    def get_progress(self):
        if self.quantity <= 0:
            return 0
        total_processes = self.processes.count()
        if total_processes == 0:
            return 0
        total_reported = 0
        for op in self.processes.all():
            total_reported += min(op.reported_quantity, self.quantity)
        return int((total_reported / (self.quantity * total_processes)) * 100)

    def can_edit_product(self):
        return not self.has_report


class WorkOrderProcess(models.Model):
    work_order = models.ForeignKey(WorkOrder, on_delete=models.CASCADE, related_name='processes', verbose_name='工单')
    process = models.ForeignKey(Process, on_delete=models.PROTECT, verbose_name='工序')
    workers = models.ManyToManyField(User, related_name='assigned_processes', verbose_name='指派工人')
    reported_quantity = models.IntegerField(default=0, verbose_name='已报工数量')
    passed_quantity = models.IntegerField(default=0, verbose_name='质检合格数量')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')

    class Meta:
        verbose_name = '工单工序'
        verbose_name_plural = verbose_name
        ordering = ['process__id']
        unique_together = ('work_order', 'process')

    def __str__(self):
        return f'{self.work_order.order_no} - {self.process.name}'


class WorkReport(models.Model):
    STATUS_CHOICES = (
        ('pending', '待质检'),
        ('passed', '已通过'),
        ('rejected', '已驳回'),
        ('rework', '待返工'),
    )

    work_order = models.ForeignKey(WorkOrder, on_delete=models.PROTECT, related_name='reports', verbose_name='工单')
    work_order_process = models.ForeignKey(WorkOrderProcess, on_delete=models.PROTECT, related_name='reports', verbose_name='工单工序')
    worker = models.ForeignKey(User, on_delete=models.PROTECT, related_name='work_reports', verbose_name='报工工人')
    quantity = models.IntegerField(verbose_name='报工数量')
    passed_quantity = models.IntegerField(default=0, verbose_name='合格件数')
    rework_quantity = models.IntegerField(default=0, verbose_name='返工件数')
    scrapped_quantity = models.IntegerField(default=0, verbose_name='报废件数')
    is_locked = models.BooleanField(default=False, verbose_name='是否锁定')
    parent_report = models.ForeignKey('self', on_delete=models.PROTECT, related_name='rework_reports', null=True, blank=True, verbose_name='原报工记录')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending', verbose_name='状态')
    inspector = models.ForeignKey(User, on_delete=models.PROTECT, related_name='inspected_reports', null=True, blank=True, verbose_name='质检人')
    inspection_time = models.DateTimeField(null=True, blank=True, verbose_name='质检时间')
    inspection_remark = models.TextField(blank=True, verbose_name='质检备注')
    remark = models.TextField(blank=True, verbose_name='报工备注')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='更新时间')

    class Meta:
        verbose_name = '报工记录'
        verbose_name_plural = verbose_name
        ordering = ['-created_at']

    def __str__(self):
        return f'{self.work_order.order_no} - {self.work_order_process.process.name} - {self.worker.name}'


class ReworkTask(models.Model):
    STATUS_CHOICES = (
        ('pending', '待返工'),
        ('submitted', '已提交重检'),
        ('completed', '已完成'),
    )

    work_report = models.ForeignKey(WorkReport, on_delete=models.PROTECT, related_name='rework_tasks', verbose_name='原报工记录')
    worker = models.ForeignKey(User, on_delete=models.PROTECT, related_name='rework_tasks', verbose_name='返工工人')
    work_order = models.ForeignKey(WorkOrder, on_delete=models.PROTECT, related_name='rework_tasks', verbose_name='工单')
    work_order_process = models.ForeignKey(WorkOrderProcess, on_delete=models.PROTECT, related_name='rework_tasks', verbose_name='工单工序')
    quantity = models.IntegerField(verbose_name='返工数量')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending', verbose_name='状态')
    resubmitted_report = models.ForeignKey(WorkReport, on_delete=models.PROTECT, related_name='source_rework_tasks', null=True, blank=True, verbose_name='重新提交的报工记录')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='更新时间')

    class Meta:
        verbose_name = '返修任务'
        verbose_name_plural = verbose_name
        ordering = ['-created_at']

    def __str__(self):
        return f'返修-{self.work_report.id}-{self.worker.name}-{self.quantity}件'


class SalarySettlement(models.Model):
    STATUS_CHOICES = (
        ('draft', '草稿'),
        ('settled', '已结算'),
    )

    settlement_month = models.CharField(max_length=7, verbose_name='结算月份(YYYY-MM)')
    created_by = models.ForeignKey(User, on_delete=models.PROTECT, related_name='created_settlements', verbose_name='创建人')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')
    total_amount = models.DecimalField(max_digits=12, decimal_places=2, default=0, verbose_name='总金额')
    total_workers = models.IntegerField(default=0, verbose_name='工人总数')
    total_reports = models.IntegerField(default=0, verbose_name='报工记录总数')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='settled', verbose_name='状态')
    is_final = models.BooleanField(default=True, verbose_name='是否最终结算(锁定数据)')

    class Meta:
        verbose_name = '工资结算单'
        verbose_name_plural = verbose_name
        ordering = ['-created_at']
        unique_together = ('settlement_month', 'is_final')

    def __str__(self):
        return f'{self.settlement_month}工资结算单'

    def get_total_workers(self):
        return self.details.values('worker').distinct().count()

    def get_total_reports(self):
        return self.details.count()

    def get_total_amount(self):
        from django.db.models import Sum
        result = self.details.aggregate(total=Sum('final_amount'))['total']
        return result or 0

    def update_statistics(self):
        self.total_workers = self.get_total_workers()
        self.total_reports = self.get_total_reports()
        self.total_amount = self.get_total_amount()
        self.save()

    def lock_work_reports(self):
        from datetime import datetime
        year, month = map(int, self.settlement_month.split('-'))
        WorkReport.objects.filter(
            created_at__year=year,
            created_at__month=month
        ).update(is_locked=True)


class SalarySettlementDetail(models.Model):
    settlement = models.ForeignKey(SalarySettlement, on_delete=models.CASCADE, related_name='details', verbose_name='结算单')
    work_report = models.ForeignKey(WorkReport, on_delete=models.PROTECT, related_name='settlement_details', verbose_name='报工记录')
    worker = models.ForeignKey(User, on_delete=models.PROTECT, related_name='salary_details', verbose_name='工人')
    work_order = models.ForeignKey(WorkOrder, on_delete=models.PROTECT, related_name='salary_details', verbose_name='工单')
    work_order_process = models.ForeignKey(WorkOrderProcess, on_delete=models.PROTECT, related_name='salary_details', verbose_name='工单工序')
    passed_quantity = models.IntegerField(default=0, verbose_name='合格件数')
    unit_price = models.DecimalField(max_digits=10, decimal_places=4, default=0, verbose_name='单价(4位小数)')
    subtotal = models.DecimalField(max_digits=12, decimal_places=4, default=0, verbose_name='小计(4位小数)')
    final_amount = models.DecimalField(max_digits=12, decimal_places=2, default=0, verbose_name='最终金额(2位小数)')
    report_created_at = models.DateTimeField(verbose_name='报工时间')

    class Meta:
        verbose_name = '工资结算明细'
        verbose_name_plural = verbose_name
        ordering = ['worker__name', '-report_created_at']

    def __str__(self):
        return f'{self.worker.name}-{self.work_order.order_no}-{self.passed_quantity}件-¥{self.final_amount}'

    def calculate(self):
        from decimal import Decimal, ROUND_HALF_UP
        price = Decimal(str(self.work_order_process.process.price))
        quantity = Decimal(str(self.passed_quantity))
        self.unit_price = price
        self.subtotal = (quantity * price).quantize(Decimal('0.0000'))
        self.final_amount = self.subtotal.quantize(Decimal('0.00'), rounding=ROUND_HALF_UP)
