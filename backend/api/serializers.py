from rest_framework import serializers
from django.contrib.auth import get_user_model
from .models import Product, Process, WorkOrder, WorkOrderProcess

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
            'id', 'process', 'process_id', 'process_name', 'process_price',
            'workers', 'worker_ids', 'workers_info',
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
