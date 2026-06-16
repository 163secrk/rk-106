from rest_framework import serializers
from django.contrib.auth import get_user_model
from django.db.models import Sum
from .models import Product, Process, WorkOrder, WorkOrderProcess, WorkReport

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
    worker_name = serializers.CharField(source='worker.name', read_only=True)
    status_name = serializers.CharField(source='get_status_display', read_only=True)
    inspector_name = serializers.CharField(source='inspector.name', read_only=True, allow_null=True)
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

    class Meta:
        model = WorkReport
        fields = [
            'id', 'work_order', 'work_order_id', 'work_order_no',
            'work_order_process', 'work_order_process_id', 'process_name',
            'worker', 'worker_name', 'quantity', 'status', 'status_name',
            'inspector', 'inspector_name', 'inspection_time',
            'inspection_remark', 'remark', 'created_at', 'updated_at'
        ]
        read_only_fields = ['work_order', 'work_order_process', 'worker', 'status', 'inspector', 'inspection_time', 'inspection_remark']

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
        validated_data['worker'] = self.context['request'].user
        work_report = WorkReport.objects.create(**validated_data)

        work_order_process = work_report.work_order_process
        total_reported = WorkReport.objects.filter(
            work_order_process=work_order_process,
            status__in=['pending', 'passed']
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
