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
    price = models.DecimalField(max_digits=10, decimal_places=2, default=0, verbose_name='工价')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')

    class Meta:
        verbose_name = '工序'
        verbose_name_plural = verbose_name
        ordering = ['id']

    def __str__(self):
        return self.name


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
