from rest_framework import serializers
from django.contrib.auth import get_user_model
from django.db.models import Sum
from .models import Product, Process, WorkOrder, WorkOrderProcess, WorkReport, ReworkTask

User = get_user_model()


class UserSerializer(serializers.ModelSerializer):
    role_name = serializers.CharField(source='get_role_display', read_only=True)

    class Meta:
        model = User
        fields = ['id', 'username', 'name', 'role', 'role_name']


class ProductSerializer(serializers.ModelSerializer):
    class Meta:
        model = Product
        fields = ['id', 'name', 'code', 'spec', 'created_at']


class ProcessSerializer(serializers.ModelSerializer):
    class Meta:
        model = Process
        fields = ['id', 'name', 'code', 'price', 'created_at']


class WorkOrderProcessSerializer(serializers.ModelSerializer):
    process_name = serializers.CharField(source='process.name', read_only=True)
    process_price = serializers.DecimalField(source='process.price', max_digits=10, decimal_places=2, read_only=True)
    workers_info = UserSerializer(source='workers', many=True, read_only=True)
    worker_ids = serializers.PrimaryKeyRelatedField(
        queryset=User.objects.filter(role='worker'),
        many=True,
        write_only=True,
        source='workers'
    )
    process_id = serializers.PrimaryKeyRelatedField(
        queryset=Process.objects.all(),
        write_only=True,
        source='process'
    )

    class Meta:
        model = WorkOrderProcess
        fields = [
            'id', 'process_id', 'process_name', 'process_price',
            'worker_ids', 'workers_info',
            'reported_quantity', 'passed_quantity', 'created_at'
        ]


class WorkOrderSerializer(serializers.ModelSerializer):
    product_name = serializers.CharField(source='product.name', read_only=True)
    product_spec = serializers.CharField(source='product.spec', read_only=True)
    created_by_name = serializers.CharField(source='created_by.name', read_only=True)
    status_name = serializers.CharField(source='get_status_display', read_only=True)
    processes = WorkOrderProcessSerializer(many=True)
    progress = serializers.SerializerMethodField()
    can_edit_product = serializers.SerializerMethodField()

    class Meta:
        model = WorkOrder
        fields = [
            'id', 'order_no', 'product', 'product_name', 'product_spec',
            'quantity', 'deadline', 'status', 'status_name',
            'created_by', 'created_by_name', 'created_at', 'updated_at',
            'has_report', 'processes', 'progress', 'can_edit_product'
        ]
        read_only_fields = ['order_no', 'status', 'created_by', 'created_at', 'updated_at', 'has_report']

    def get_progress(self, obj):
        return obj.get_progress()

    def get_can_edit_product(self, obj):
        return obj.can_edit_product()

    def validate(self, attrs):
        instance = getattr(self, 'instance', None)
        if instance and instance.has_report:
            if 'product' in attrs or 'quantity' in attrs:
                raise serializers.ValidationError(
                    '工单已有报工记录，不能修改产品和数量'
                )

        processes_data = attrs.get('processes', [])
        if processes_data:
            process_ids = []
            for p_data in processes_data:
                process = p_data.get('process')
                if process:
                    pid = process.id if hasattr(process, 'id') else process
                    if pid in process_ids:
                        raise serializers.ValidationError(
                            {'processes': '不能重复添加相同的工序'}
                        )
                    process_ids.append(pid)

        return attrs

    def create(self, validated_data):
        processes_data = validated_data.pop('processes', [])
        validated_data['created_by'] = self.context['request'].user
        work_order = WorkOrder.objects.create(**validated_data)
        for process_data in processes_data:
            workers = process_data.pop('workers', [])
            wo_process = WorkOrderProcess.objects.create(
                work_order=work_order,
                **process_data
            )
            if workers:
                wo_process.workers.set(workers)
        return work_order

    def update(self, instance, validated_data):
        processes_data = validated_data.pop('processes', None)
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()

        if processes_data is not None:
            existing_process_ids = [p.id for p in instance.processes.all()]
            incoming_process_ids = [
                p.get('id') for p in processes_data if p.get('id')
            ]

            for p_id in existing_process_ids:
                if p_id not in incoming_process_ids:
                    WorkOrderProcess.objects.filter(id=p_id).delete()

            for process_data in processes_data:
                process_id = process_data.get('id')
                workers = process_data.pop('workers', [])
                if process_id:
                    wo_process = WorkOrderProcess.objects.get(id=process_id)
                    if not instance.has_report:
                        wo_process.process = process_data.get('process', wo_process.process)
                    if workers:
                        wo_process.workers.set(workers)
                    wo_process.save()
                else:
                    wo_process = WorkOrderProcess.objects.create(
                        work_order=instance,
                        **process_data
                    )
                    if workers:
                        wo_process.workers.set(workers)

        return instance


class WorkOrderListSerializer(serializers.ModelSerializer):
    product_name = serializers.CharField(source='product.name', read_only=True)
    created_by_name = serializers.CharField(source='created_by.name', read_only=True)
    status_name = serializers.CharField(source='get_status_display', read_only=True)
    progress = serializers.SerializerMethodField()

    class Meta:
        model = WorkOrder
        fields = [
            'id', 'order_no', 'product_name', 'quantity',
            'deadline', 'status', 'status_name',
            'created_by_name', 'created_at', 'progress'
        ]

    def get_progress(self, obj):
        return obj.get_progress()


class WorkReportSerializer(serializers.ModelSerializer):
    work_order_no = serializers.CharField(source='work_order.order_no', read_only=True)
    process_name = serializers.CharField(source='work_order_process.process.name', read_only=True)
    process_price = serializers.SerializerMethodField()
    worker_name = serializers.CharField(source='worker.name', read_only=True)
    status_name = serializers.CharField(source='get_status_display', read_only=True)
    inspector_name = serializers.CharField(source='inspector.name', read_only=True, allow_null=True)
    has_scrap = serializers.SerializerMethodField()
    salary_amount = serializers.SerializerMethodField()

    work_order_id = serializers.PrimaryKeyRelatedField(
        queryset=WorkOrder.objects.all(),
        write_only=True,
        source='work_order'
    )
    work_order_process_id = serializers.PrimaryKeyRelatedField(
        queryset=WorkOrderProcess.objects.all(),
        write_only=True,
        source='work_order_process'
    )
    rework_task_id = serializers.IntegerField(write_only=True, required=False, allow_null=True)

    class Meta:
        model = WorkReport
        fields = [
            'id', 'work_order', 'work_order_id', 'work_order_no',
            'work_order_process', 'work_order_process_id', 'process_name', 'process_price',
            'worker', 'worker_name', 'quantity', 'passed_quantity', 'rework_quantity', 'scrapped_quantity',
            'status', 'status_name', 'is_locked', 'parent_report', 'has_scrap', 'salary_amount',
            'inspector', 'inspector_name', 'inspection_time',
            'inspection_remark', 'remark', 'created_at', 'updated_at', 'rework_task_id'
        ]
        read_only_fields = ['work_order', 'work_order_process', 'worker', 'status', 'inspector', 'inspection_time', 'inspection_remark', 'passed_quantity', 'rework_quantity', 'scrapped_quantity', 'is_locked', 'parent_report']

    def get_process_price(self, obj):
        return float(obj.work_order_process.process.price)

    def get_has_scrap(self, obj):
        return obj.scrapped_quantity > 0

    def get_salary_amount(self, obj):
        if obj.status != 'passed':
            return 0
        return float(obj.passed_quantity * obj.work_order_process.process.price)


class QualityInspectionSerializer(serializers.Serializer):
    passed_quantity = serializers.IntegerField(min_value=0, required=True)
    rework_quantity = serializers.IntegerField(min_value=0, required=True)
    scrapped_quantity = serializers.IntegerField(min_value=0, required=True)
    inspection_remark = serializers.CharField(required=False, allow_blank=True)

    def validate(self, attrs):
        report = self.context.get('work_report')
        if not report:
            raise serializers.ValidationError('报工记录不存在')
        
        if report.status != 'pending' and report.status != 'rework':
            raise serializers.ValidationError('该报工记录不是待质检状态')
        
        total = attrs['passed_quantity'] + attrs['rework_quantity'] + attrs['scrapped_quantity']
        if total != report.quantity:
            raise serializers.ValidationError(f'合格+返工+报废数量({total})必须等于报工数量({report.quantity})')
        
        return attrs


class ReworkTaskSerializer(serializers.ModelSerializer):
    work_order_no = serializers.CharField(source='work_order.order_no', read_only=True)
    process_name = serializers.CharField(source='work_order_process.process.name', read_only=True)
    worker_name = serializers.CharField(source='worker.name', read_only=True)
    status_name = serializers.CharField(source='get_status_display', read_only=True)
    original_quantity = serializers.IntegerField(source='work_report.quantity', read_only=True)
    original_report_id = serializers.IntegerField(source='work_report.id', read_only=True)

    class Meta:
        model = ReworkTask
        fields = [
            'id', 'work_report', 'original_report_id', 'work_order', 'work_order_no',
            'work_order_process', 'process_name', 'worker', 'worker_name',
            'quantity', 'status', 'status_name', 'original_quantity',
            'resubmitted_report', 'created_at', 'updated_at'
        ]
        read_only_fields = ['work_report', 'work_order', 'work_order_process', 'worker', 'quantity', 'status', 'resubmitted_report']


class InspectorWorkReportSerializer(serializers.ModelSerializer):
    work_order_no = serializers.CharField(source='work_order.order_no', read_only=True)
    process_name = serializers.CharField(source='work_order_process.process.name', read_only=True)
    worker_name = serializers.CharField(source='worker.name', read_only=True)
    status_name = serializers.CharField(source='get_status_display', read_only=True)
    has_scrap = serializers.SerializerMethodField()
    has_passed = serializers.SerializerMethodField()
    product_name = serializers.CharField(source='work_order.product.name', read_only=True)
    work_order_id = serializers.IntegerField(source='work_order.id', read_only=True)

    class Meta:
        model = WorkReport
        fields = [
            'id', 'work_order_id', 'work_order_no', 'product_name',
            'process_name', 'worker', 'worker_name', 'quantity',
            'passed_quantity', 'rework_quantity', 'scrapped_quantity',
            'status', 'status_name', 'is_locked', 'has_scrap', 'has_passed',
            'remark', 'created_at'
        ]

    def get_has_scrap(self, obj):
        return obj.scrapped_quantity > 0

    def get_has_passed(self, obj):
        return obj.status == 'passed'

    def validate(self, attrs):
        work_order = attrs.get('work_order')
        work_order_process = attrs.get('work_order_process')
        quantity = attrs.get('quantity')
        worker = self.context['request'].user

        if work_order_process.work_order != work_order:
            raise serializers.ValidationError('工序不属于该工单')

        if not work_order_process.workers.filter(id=worker.id).exists():
            raise serializers.ValidationError('您没有该工序的报工权限')

        if quantity <= 0:
            raise serializers.ValidationError('报工数量必须大于0')

        total_reported = WorkReport.objects.filter(
            work_order=work_order,
            work_order_process=work_order_process,
            status__in=['pending', 'passed']
        ).aggregate(total=Sum('quantity'))['total'] or 0

        remaining = work_order.quantity - total_reported
        if quantity > remaining:
            raise serializers.ValidationError(
                f'超出工单数量，剩余可报{remaining}件'
            )

        return attrs

    def create(self, validated_data):
        rework_task_id = validated_data.pop('rework_task_id', None)
        validated_data['worker'] = self.context['request'].user
        
        if rework_task_id:
            try:
                rework_task = ReworkTask.objects.get(id=rework_task_id, worker=validated_data['worker'], status='pending')
                validated_data['parent_report'] = rework_task.work_report
                validated_data['status'] = 'rework'
            except ReworkTask.DoesNotExist:
                raise serializers.ValidationError('返修任务不存在或已处理')
        
        work_report = WorkReport.objects.create(**validated_data)

        if rework_task_id:
            rework_task = ReworkTask.objects.get(id=rework_task_id)
            rework_task.status = 'submitted'
            rework_task.resubmitted_report = work_report
            rework_task.save()

        work_order_process = work_report.work_order_process
        total_reported = WorkReport.objects.filter(
            work_order_process=work_order_process,
            status__in=['pending', 'passed', 'rework']
        ).aggregate(total=Sum('quantity'))['total'] or 0
        work_order_process.reported_quantity = total_reported
        work_order_process.save()

        work_order = work_report.work_order
        work_order.has_report = True
        work_order.save()
        work_order.update_status()

        return work_report


class WorkerWorkOrderProcessSerializer(serializers.ModelSerializer):
    process_name = serializers.CharField(source='process.name', read_only=True)
    process_price = serializers.DecimalField(source='process.price', max_digits=10, decimal_places=2, read_only=True)
    total_reported = serializers.SerializerMethodField()
    remaining = serializers.SerializerMethodField()
    progress_percent = serializers.SerializerMethodField()

    class Meta:
        model = WorkOrderProcess
        fields = [
            'id', 'process_name', 'process_price', 'reported_quantity',
            'passed_quantity', 'total_reported', 'remaining', 'progress_percent'
        ]

    def get_total_reported(self, obj):
        return WorkReport.objects.filter(
            work_order_process=obj,
            status__in=['pending', 'passed']
        ).aggregate(total=Sum('quantity'))['total'] or 0

    def get_remaining(self, obj):
        total_reported = self.get_total_reported(obj)
        return max(0, obj.work_order.quantity - total_reported)

    def get_progress_percent(self, obj):
        if obj.work_order.quantity <= 0:
            return 0
        total_reported = self.get_total_reported(obj)
        return int((total_reported / obj.work_order.quantity) * 100)


class WorkerWorkOrderSerializer(serializers.ModelSerializer):
    product_name = serializers.CharField(source='product.name', read_only=True)
    product_spec = serializers.CharField(source='product.spec', read_only=True)
    status_name = serializers.CharField(source='get_status_display', read_only=True)
    processes = serializers.SerializerMethodField()

    class Meta:
        model = WorkOrder
        fields = [
            'id', 'order_no', 'product_name', 'product_spec', 'quantity',
            'deadline', 'status', 'status_name', 'created_at', 'processes'
        ]

    def get_processes(self, obj):
        worker = self.context['request'].user
        worker_processes = obj.processes.filter(workers=worker)
        return WorkerWorkOrderProcessSerializer(worker_processes, many=True, context=self.context).data
