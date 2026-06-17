from rest_framework import status, viewsets
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth import authenticate, get_user_model
from django.utils import timezone
from django.db.models import Sum, Value, CharField, IntegerField, FloatField, Count, Q, F, Max
from django.db.models.functions import Concat, TruncDate
from datetime import timedelta
from decimal import Decimal, ROUND_HALF_UP
from collections import defaultdict
from .models import Product, Process, ProductProcess, WorkOrder, WorkOrderProcess, WorkReport, ReworkTask, SalarySettlement, SalarySettlementDetail
from .serializers import (
    UserSerializer,
    ProductSerializer,
    ProductWithProcessesSerializer,
    ProductProcessSerializer,
    ProcessSerializer,
    WorkOrderSerializer,
    WorkOrderListSerializer,
    WorkReportSerializer,
    WorkerWorkOrderSerializer,
    QualityInspectionSerializer,
    ReworkTaskSerializer,
    InspectorWorkReportSerializer,
    WorkReportTraceSerializer,
    WorkReportTraceChainSerializer,
    SalarySummarySerializer,
    SalarySummaryGroupedSerializer,
    SalarySettlementSerializer,
    SalarySettlementListSerializer,
    CreateSettlementSerializer
)


class LoginView(APIView):
    def post(self, request):
        username = request.data.get('username')
        password = request.data.get('password')

        if not username or not password:
            return Response(
                {'code': 400, 'message': '请提供用户名和密码'},
                status=status.HTTP_400_BAD_REQUEST
            )

        user = authenticate(username=username, password=password)

        if user is None:
            return Response(
                {'code': 401, 'message': '用户名或密码错误'},
                status=status.HTTP_401_UNAUTHORIZED
            )

        refresh = RefreshToken.for_user(user)
        user_data = UserSerializer(user).data
        role_data = {
            'code': user.role,
            'name': user.get_role_display()
        }

        return Response({
            'code': 200,
            'message': '登录成功',
            'data': {
                'token': str(refresh.access_token),
                'refreshToken': str(refresh),
                'userInfo': user_data,
                'roles': [role_data]
            }
        })


class UserInfoView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user_data = UserSerializer(request.user).data
        role_data = {
            'code': request.user.role,
            'name': request.user.get_role_display()
        }
        return Response({
            'code': 200,
            'message': '成功',
            'data': {
                'userInfo': user_data,
                'roles': [role_data]
            }
        })


class ProductViewSet(viewsets.ModelViewSet):
    queryset = Product.objects.all()
    permission_classes = [IsAuthenticated]

    def get_serializer_class(self):
        if self.action == 'retrieve':
            return ProductWithProcessesSerializer
        return ProductSerializer

    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        serializer = ProductWithProcessesSerializer(queryset, many=True)
        return Response({
            'code': 200,
            'message': '成功',
            'data': serializer.data
        })

    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance)
        return Response({
            'code': 200,
            'message': '成功',
            'data': serializer.data
        })

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            self.perform_create(serializer)
            return Response({
                'code': 200,
                'message': '创建成功',
                'data': serializer.data
            })
        return Response({
            'code': 400,
            'message': '数据验证失败',
            'errors': serializer.errors
        }, status=status.HTTP_400_BAD_REQUEST)

    def update(self, request, *args, **kwargs):
        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        if serializer.is_valid():
            self.perform_update(serializer)
            return Response({
                'code': 200,
                'message': '更新成功',
                'data': serializer.data
            })
        return Response({
            'code': 400,
            'message': '数据验证失败',
            'errors': serializer.errors
        }, status=status.HTTP_400_BAD_REQUEST)

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        if WorkOrder.objects.filter(product=instance).exists():
            return Response({
                'code': 400,
                'message': '该产品已有生产工单，不能删除'
            }, status=status.HTTP_400_BAD_REQUEST)
        self.perform_destroy(instance)
        return Response({
            'code': 200,
            'message': '删除成功'
        })


class ProductProcessViewSet(viewsets.ModelViewSet):
    queryset = ProductProcess.objects.all()
    serializer_class = ProductProcessSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        queryset = super().get_queryset()
        product_id = self.request.query_params.get('product_id')
        if product_id:
            queryset = queryset.filter(product_id=product_id)
        return queryset

    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        serializer = self.get_serializer(queryset, many=True)
        return Response({
            'code': 200,
            'message': '成功',
            'data': serializer.data
        })

    def create(self, request, *args, **kwargs):
        product_id = request.data.get('product_id')
        if not product_id:
            return Response({
                'code': 400,
                'message': '请提供产品ID'
            }, status=status.HTTP_400_BAD_REQUEST)

        try:
            product = Product.objects.get(id=product_id)
        except Product.DoesNotExist:
            return Response({
                'code': 404,
                'message': '产品不存在'
            }, status=status.HTTP_404_NOT_FOUND)

        data = request.data.copy()
        current_max = ProductProcess.objects.filter(product=product).aggregate(max_order=Max('order_index'))['max_order']
        max_order = current_max + 1 if current_max is not None else 0
        data['order_index'] = request.data.get('order_index', max_order)

        serializer = self.get_serializer(data=data)
        if serializer.is_valid():
            serializer.save(product=product)
            return Response({
                'code': 200,
                'message': '添加工序成功',
                'data': serializer.data
            })
        return Response({
            'code': 400,
            'message': '数据验证失败',
            'errors': serializer.errors
        }, status=status.HTTP_400_BAD_REQUEST)

    def update(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=True)
        if serializer.is_valid():
            self.perform_update(serializer)
            return Response({
                'code': 200,
                'message': '更新成功',
                'data': serializer.data
            })
        return Response({
            'code': 400,
            'message': '数据验证失败',
            'errors': serializer.errors
        }, status=status.HTTP_400_BAD_REQUEST)

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        self.perform_destroy(instance)
        return Response({
            'code': 200,
            'message': '删除成功'
        })


class ProductProcessBatchUpdateView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, product_id):
        try:
            product = Product.objects.get(id=product_id)
        except Product.DoesNotExist:
            return Response({
                'code': 404,
                'message': '产品不存在'
            }, status=status.HTTP_404_NOT_FOUND)

        processes_data = request.data.get('processes', [])
        if not isinstance(processes_data, list):
            return Response({
                'code': 400,
                'message': '工序数据格式错误'
            }, status=status.HTTP_400_BAD_REQUEST)

        for idx, proc_data in enumerate(processes_data):
            pp_id = proc_data.get('id')
            if pp_id:
                try:
                    pp = ProductProcess.objects.get(id=pp_id, product=product)
                    pp.order_index = proc_data.get('order_index', idx)
                    pp.unit_price = proc_data.get('unit_price', pp.unit_price)
                    pp.save()
                except ProductProcess.DoesNotExist:
                    continue

        product.refresh_from_db()
        serializer = ProductWithProcessesSerializer(product)
        return Response({
            'code': 200,
            'message': '工序排序更新成功',
            'data': serializer.data
        })


class ProcessViewSet(viewsets.ModelViewSet):
    queryset = Process.objects.all()
    serializer_class = ProcessSerializer
    permission_classes = [IsAuthenticated]

    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        serializer = self.get_serializer(queryset, many=True)
        return Response({
            'code': 200,
            'message': '成功',
            'data': serializer.data
        })

    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance)
        return Response({
            'code': 200,
            'message': '成功',
            'data': serializer.data
        })

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            self.perform_create(serializer)
            return Response({
                'code': 200,
                'message': '创建成功',
                'data': serializer.data
            })
        return Response({
            'code': 400,
            'message': '数据验证失败',
            'errors': serializer.errors
        }, status=status.HTTP_400_BAD_REQUEST)

    def update(self, request, *args, **kwargs):
        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        if serializer.is_valid():
            self.perform_update(serializer)
            return Response({
                'code': 200,
                'message': '更新成功',
                'data': serializer.data
            })
        return Response({
            'code': 400,
            'message': '数据验证失败',
            'errors': serializer.errors
        }, status=status.HTTP_400_BAD_REQUEST)

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        self.perform_destroy(instance)
        return Response({
            'code': 200,
            'message': '删除成功'
        })


class WorkOrderViewSet(viewsets.ModelViewSet):
    queryset = WorkOrder.objects.all()
    permission_classes = [IsAuthenticated]

    def get_serializer_class(self):
        if self.action == 'list':
            return WorkOrderListSerializer
        return WorkOrderSerializer

    def generate_order_no(self):
        today = timezone.now().strftime('%Y%m%d')
        count = WorkOrder.objects.filter(
            created_at__date=timezone.now().date()
        ).count() + 1
        return f'WO{today}{count:04d}'

    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        serializer = self.get_serializer(queryset, many=True)
        return Response({
            'code': 200,
            'message': '成功',
            'data': serializer.data
        })

    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance)
        return Response({
            'code': 200,
            'message': '成功',
            'data': serializer.data
        })

    def create(self, request, *args, **kwargs):
        data = request.data.copy()
        data['order_no'] = self.generate_order_no()
        serializer = self.get_serializer(data=data, context={'request': request})
        if serializer.is_valid():
            self.perform_create(serializer)
            return Response({
                'code': 200,
                'message': '创建成功',
                'data': serializer.data
            })
        return Response({
            'code': 400,
            'message': '数据验证失败',
            'errors': serializer.errors
        }, status=status.HTTP_400_BAD_REQUEST)

    def update(self, request, *args, **kwargs):
        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=partial, context={'request': request})
        if serializer.is_valid():
            self.perform_update(serializer)
            instance.update_status()
            return Response({
                'code': 200,
                'message': '更新成功',
                'data': serializer.data
            })
        return Response({
            'code': 400,
            'message': '数据验证失败',
            'errors': serializer.errors
        }, status=status.HTTP_400_BAD_REQUEST)

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        if instance.has_report:
            return Response({
                'code': 400,
                'message': '工单已有报工记录，不能删除'
            }, status=status.HTTP_400_BAD_REQUEST)
        self.perform_destroy(instance)
        return Response({
            'code': 200,
            'message': '删除成功'
        })


class WorkerListView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        from django.contrib.auth import get_user_model
        User = get_user_model()
        workers = User.objects.filter(role='worker')
        serializer = UserSerializer(workers, many=True)
        return Response({
            'code': 200,
            'message': '成功',
            'data': serializer.data
        })


class WorkerWorkOrderListView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        worker = request.user
        work_orders = WorkOrder.objects.filter(
            processes__workers=worker,
            status__in=['pending', 'in_progress']
        ).distinct().order_by('-created_at')
        serializer = WorkerWorkOrderSerializer(work_orders, many=True, context={'request': request})
        return Response({
            'code': 200,
            'message': '成功',
            'data': serializer.data
        })


class WorkReportViewSet(viewsets.ModelViewSet):
    queryset = WorkReport.objects.all()
    serializer_class = WorkReportSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        queryset = WorkReport.objects.all()
        worker = self.request.user
        if worker.role == 'worker':
            queryset = queryset.filter(worker=worker)
        elif worker.role == 'inspector':
            pass
        return queryset.order_by('-created_at')

    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        serializer = self.get_serializer(queryset, many=True)
        return Response({
            'code': 200,
            'message': '成功',
            'data': serializer.data
        })

    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance)
        return Response({
            'code': 200,
            'message': '成功',
            'data': serializer.data
        })

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data, context={'request': request})
        if serializer.is_valid():
            self.perform_create(serializer)
            return Response({
                'code': 200,
                'message': '报工成功',
                'data': serializer.data
            })
        error_message = list(serializer.errors.values())[0][0] if serializer.errors else '数据验证失败'
        return Response({
            'code': 400,
            'message': error_message,
            'errors': serializer.errors
        }, status=status.HTTP_400_BAD_REQUEST)

    def update(self, request, *args, **kwargs):
        instance = self.get_object()
        if instance.is_locked:
            return Response({
                'code': 400,
                'message': '该报工记录已锁定，不能修改'
            }, status=status.HTTP_400_BAD_REQUEST)
        if instance.status != 'pending':
            return Response({
                'code': 400,
                'message': '只能修改待质检状态的报工记录'
            }, status=status.HTTP_400_BAD_REQUEST)
        partial = kwargs.pop('partial', False)
        serializer = self.get_serializer(instance, data=request.data, partial=partial, context={'request': request})
        if serializer.is_valid():
            self.perform_update(serializer)
            return Response({
                'code': 200,
                'message': '更新成功',
                'data': serializer.data
            })
        return Response({
            'code': 400,
            'message': '数据验证失败',
            'errors': serializer.errors
        }, status=status.HTTP_400_BAD_REQUEST)

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        if instance.is_locked:
            return Response({
                'code': 400,
                'message': '该报工记录已锁定，不能删除'
            }, status=status.HTTP_400_BAD_REQUEST)
        if instance.status != 'pending':
            return Response({
                'code': 400,
                'message': '只能删除待质检状态的报工记录'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        work_order_process = instance.work_order_process
        work_order = instance.work_order
        
        self.perform_destroy(instance)
        
        total_reported = WorkReport.objects.filter(
            work_order_process=work_order_process,
            status__in=['pending', 'passed', 'rework']
        ).aggregate(total=Sum('quantity'))['total'] or 0
        work_order_process.reported_quantity = total_reported
        work_order_process.save()
        
        has_other_reports = WorkReport.objects.filter(work_order=work_order).exists()
        if not has_other_reports:
            work_order.has_report = False
            work_order.save()
        work_order.update_status()
        
        return Response({
            'code': 200,
            'message': '删除成功'
        })


class InspectorPendingListView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        if request.user.role not in ['inspector', 'admin', 'team_leader']:
            return Response({
                'code': 403,
                'message': '无权限访问'
            }, status=status.HTTP_403_FORBIDDEN)

        pending_reports = WorkReport.objects.filter(
            status__in=['pending', 'rework'],
            is_locked=False
        ).select_related('work_order', 'work_order_process', 'worker', 'work_order__product')

        grouped_data = {}
        for report in pending_reports:
            wo_id = report.work_order.id
            if wo_id not in grouped_data:
                grouped_data[wo_id] = {
                    'work_order_id': wo_id,
                    'work_order_no': report.work_order.order_no,
                    'product_name': report.work_order.product.name,
                    'product_spec': report.work_order.product.spec,
                    'total_quantity': report.work_order.quantity,
                    'reports': []
                }
            report_data = InspectorWorkReportSerializer(report).data
            grouped_data[wo_id]['reports'].append(report_data)

        result = list(grouped_data.values())
        return Response({
            'code': 200,
            'message': '成功',
            'data': result
        })


class InspectorHistoryListView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        if request.user.role not in ['inspector', 'admin', 'team_leader']:
            return Response({
                'code': 403,
                'message': '无权限访问'
            }, status=status.HTTP_403_FORBIDDEN)

        inspected_reports = WorkReport.objects.filter(
            status__in=['passed', 'rejected', 'rework'],
            is_locked=True
        ).select_related('work_order', 'work_order_process', 'worker', 'work_order__product', 'inspector').order_by('-inspection_time')

        serializer = InspectorWorkReportSerializer(inspected_reports, many=True)
        return Response({
            'code': 200,
            'message': '成功',
            'data': serializer.data
        })


class QualityInspectionView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, pk):
        if request.user.role not in ['inspector', 'admin', 'team_leader']:
            return Response({
                'code': 403,
                'message': '无权限操作'
            }, status=status.HTTP_403_FORBIDDEN)

        try:
            work_report = WorkReport.objects.get(pk=pk)
        except WorkReport.DoesNotExist:
            return Response({
                'code': 404,
                'message': '报工记录不存在'
            }, status=status.HTTP_404_NOT_FOUND)

        if work_report.is_locked:
            return Response({
                'code': 400,
                'message': '该报工记录已锁定，不能重复质检'
            }, status=status.HTTP_400_BAD_REQUEST)

        if work_report.status not in ['pending', 'rework']:
            return Response({
                'code': 400,
                'message': '该报工记录不是待质检状态'
            }, status=status.HTTP_400_BAD_REQUEST)

        serializer = QualityInspectionSerializer(data=request.data, context={'work_report': work_report})
        if not serializer.is_valid():
            error_message = list(serializer.errors.values())[0][0] if serializer.errors else '数据验证失败'
            return Response({
                'code': 400,
                'message': error_message,
                'errors': serializer.errors
            }, status=status.HTTP_400_BAD_REQUEST)

        validated_data = serializer.validated_data
        passed_qty = validated_data['passed_quantity']
        rework_qty = validated_data['rework_quantity']
        scrapped_qty = validated_data['scrapped_quantity']
        remark = validated_data.get('inspection_remark', '')

        work_report.passed_quantity = passed_qty
        work_report.rework_quantity = rework_qty
        work_report.scrapped_quantity = scrapped_qty
        work_report.inspection_remark = remark
        work_report.inspector = request.user
        work_report.inspection_time = timezone.now()
        work_report.is_locked = True

        if scrapped_qty > 0 and rework_qty == 0 and passed_qty == 0:
            work_report.status = 'rejected'
        elif rework_qty > 0:
            work_report.status = 'rework'
        else:
            work_report.status = 'passed'

        work_report.save()

        wo_process = work_report.work_order_process
        total_passed = WorkReport.objects.filter(
            work_order_process=wo_process,
            status='passed'
        ).aggregate(total=Sum('passed_quantity'))['total'] or 0
        wo_process.passed_quantity = total_passed
        wo_process.save()

        if rework_qty > 0:
            ReworkTask.objects.create(
                work_report=work_report,
                worker=work_report.worker,
                work_order=work_report.work_order,
                work_order_process=work_report.work_order_process,
                quantity=rework_qty
            )

        if work_report.parent_report:
            try:
                original_rework_task = ReworkTask.objects.get(
                    resubmitted_report=work_report
                )
                if work_report.status == 'passed':
                    original_rework_task.status = 'completed'
                elif work_report.status == 'rework':
                    original_rework_task.status = 'pending'
                original_rework_task.save()
            except ReworkTask.DoesNotExist:
                pass

        work_report.work_order.update_status()

        return Response({
            'code': 200,
            'message': '质检完成',
            'data': WorkReportSerializer(work_report).data
        })


class WorkerReworkTaskListView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        worker = request.user
        if worker.role != 'worker':
            return Response({
                'code': 403,
                'message': '无权限访问'
            }, status=status.HTTP_403_FORBIDDEN)

        status_filter = request.query_params.get('status', None)
        queryset = ReworkTask.objects.filter(worker=worker)
        if status_filter:
            queryset = queryset.filter(status=status_filter)

        queryset = queryset.select_related(
            'work_report', 'work_order', 'work_order_process', 'resubmitted_report'
        ).order_by('-created_at')

        serializer = ReworkTaskSerializer(queryset, many=True)
        return Response({
            'code': 200,
            'message': '成功',
            'data': serializer.data
        })


class WorkerReworkTaskDetailView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, pk):
        worker = request.user
        if worker.role != 'worker':
            return Response({
                'code': 403,
                'message': '无权限访问'
            }, status=status.HTTP_403_FORBIDDEN)

        try:
            rework_task = ReworkTask.objects.get(pk=pk, worker=worker)
        except ReworkTask.DoesNotExist:
            return Response({
                'code': 404,
                'message': '返修任务不存在'
            }, status=status.HTTP_404_NOT_FOUND)

        serializer = ReworkTaskSerializer(rework_task)
        return Response({
            'code': 200,
            'message': '成功',
            'data': serializer.data
        })


class SalarySummaryView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        if request.user.role not in ['admin', 'team_leader']:
            return Response({
                'code': 403,
                'message': '无权限访问'
            }, status=status.HTTP_403_FORBIDDEN)

        month = request.query_params.get('month', None)
        worker_id = request.query_params.get('worker_id', None)
        work_order_id = request.query_params.get('work_order_id', None)
        process_id = request.query_params.get('process_id', None)

        queryset = WorkReport.objects.filter(
            status='passed'
        ).select_related(
            'worker', 'work_order', 'work_order_process', 'work_order_process__process'
        )

        if month:
            year, month_num = map(int, month.split('-'))
            queryset = queryset.filter(
                created_at__year=year,
                created_at__month=month_num
            )

        if worker_id:
            queryset = queryset.filter(worker_id=worker_id)

        if work_order_id:
            queryset = queryset.filter(work_order_id=work_order_id)

        if process_id:
            queryset = queryset.filter(work_order_process__process_id=process_id)

        grouped = defaultdict(lambda: defaultdict(lambda: {
            'worker_id': None,
            'worker_name': '',
            'settlement_month': month or '',
            'work_order_id': None,
            'work_order_no': '',
            'work_order_process_id': None,
            'process_name': '',
            'total_passed': 0,
            'unit_price': 0.0,
            'subtotal': 0.0,
            'final_amount': 0.0,
            'report_ids': []
        }))

        for report in queryset:
            w_id = report.worker_id
            wo_id = report.work_order_id
            wop_id = report.work_order_process_id
            key = (w_id, wo_id, wop_id)
            entry = grouped[w_id][key]

            process_price = Decimal(str(report.work_order_process.process.price))
            passed_qty = Decimal(str(report.passed_quantity))
            report_subtotal = (passed_qty * process_price).quantize(Decimal('0.0000'))
            report_final = report_subtotal.quantize(Decimal('0.00'), rounding=ROUND_HALF_UP)

            if entry['worker_id'] is None:
                entry['worker_id'] = report.worker.id
                entry['worker_name'] = report.worker.name
                entry['work_order_id'] = report.work_order.id
                entry['work_order_no'] = report.work_order.order_no
                entry['work_order_process_id'] = report.work_order_process.id
                entry['process_name'] = report.work_order_process.process.name
                entry['unit_price'] = float(process_price)

            entry['total_passed'] += report.passed_quantity
            entry['subtotal'] = float((Decimal(str(entry['subtotal'])) + report_subtotal).quantize(Decimal('0.0000')))
            entry['report_ids'].append(report.id)

        result = []
        for w_id, worker_groups in grouped.items():
            worker_total_passed = 0
            worker_total_amount = Decimal('0')
            details = []
            worker_report_count = 0
            worker_values_list = list(worker_groups.values())

            for detail in worker_values_list:
                subtotal_dec = Decimal(str(detail['subtotal']))
                detail['final_amount'] = float(subtotal_dec.quantize(Decimal('0.00'), rounding=ROUND_HALF_UP))
                details.append(detail)
                worker_total_passed += detail['total_passed']
                worker_total_amount += Decimal(str(detail['final_amount']))
                worker_report_count += len(detail['report_ids'])

            worker_entry = {
                'worker_id': worker_values_list[0]['worker_id'],
                'worker_name': worker_values_list[0]['worker_name'],
                'settlement_month': month or '',
                'total_passed': worker_total_passed,
                'total_amount': float(worker_total_amount.quantize(Decimal('0.00'))),
                'report_count': worker_report_count,
                'details': details
            }
            result.append(worker_entry)

        return Response({
            'code': 200,
            'message': '成功',
            'data': result
        })


class WorkReportTraceView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, pk):
        if request.user.role not in ['admin', 'team_leader']:
            return Response({
                'code': 403,
                'message': '无权限访问'
            }, status=status.HTTP_403_FORBIDDEN)

        try:
            report = WorkReport.objects.get(pk=pk)
        except WorkReport.DoesNotExist:
            return Response({
                'code': 404,
                'message': '报工记录不存在'
            }, status=status.HTTP_404_NOT_FOUND)

        chain = []
        current = report
        while current.parent_report is not None:
            current = current.parent_report
            chain.insert(0, current)
        chain.append(report)

        chain_data = []
        for idx, r in enumerate(chain):
            serializer = WorkReportTraceChainSerializer(r, context={'chain_order': idx})
            chain_data.append(serializer.data)

        main_serializer = WorkReportTraceSerializer(report)
        return Response({
            'code': 200,
            'message': '成功',
            'data': {
                'main': main_serializer.data,
                'chain': chain_data
            }
        })


class SalarySettlementListView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        if request.user.role not in ['admin', 'team_leader']:
            return Response({
                'code': 403,
                'message': '无权限访问'
            }, status=status.HTTP_403_FORBIDDEN)

        month = request.query_params.get('month', None)
        queryset = SalarySettlement.objects.all().select_related('created_by')

        if month:
            queryset = queryset.filter(settlement_month=month)

        queryset = queryset.order_by('-created_at')
        serializer = SalarySettlementListSerializer(queryset, many=True)
        return Response({
            'code': 200,
            'message': '成功',
            'data': serializer.data
        })


class SalarySettlementDetailView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, pk):
        if request.user.role not in ['admin', 'team_leader']:
            return Response({
                'code': 403,
                'message': '无权限访问'
            }, status=status.HTTP_403_FORBIDDEN)

        try:
            settlement = SalarySettlement.objects.select_related('created_by').get(pk=pk)
        except SalarySettlement.DoesNotExist:
            return Response({
                'code': 404,
                'message': '结算单不存在'
            }, status=status.HTTP_404_NOT_FOUND)

        serializer = SalarySettlementSerializer(settlement)
        return Response({
            'code': 200,
            'message': '成功',
            'data': serializer.data
        })


class CreateSettlementView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        if request.user.role not in ['admin', 'team_leader']:
            return Response({
                'code': 403,
                'message': '无权限操作'
            }, status=status.HTTP_403_FORBIDDEN)

        serializer = CreateSettlementSerializer(data=request.data)
        if not serializer.is_valid():
            error_message = list(serializer.errors.values())[0][0] if serializer.errors else '数据验证失败'
            return Response({
                'code': 400,
                'message': error_message,
                'errors': serializer.errors
            }, status=status.HTTP_400_BAD_REQUEST)

        settlement_month = serializer.validated_data['settlement_month']
        year, month_num = map(int, settlement_month.split('-'))

        existing = SalarySettlement.objects.filter(
            settlement_month=settlement_month,
            is_final=True
        ).first()
        if existing:
            return Response({
                'code': 400,
                'message': f'{settlement_month}月已存在结算单，不能重复生成'
            }, status=status.HTTP_400_BAD_REQUEST)

        reports = WorkReport.objects.filter(
            created_at__year=year,
            created_at__month=month_num,
            status='passed'
        ).select_related(
            'worker', 'work_order', 'work_order_process', 'work_order_process__process'
        )

        if not reports.exists():
            return Response({
                'code': 400,
                'message': f'{settlement_month}月没有已通过质检的报工记录'
            }, status=status.HTTP_400_BAD_REQUEST)

        settlement = SalarySettlement.objects.create(
            settlement_month=settlement_month,
            created_by=request.user,
            status='settled',
            is_final=True
        )

        details_to_create = []
        for report in reports:
            detail = SalarySettlementDetail(
                settlement=settlement,
                work_report=report,
                worker=report.worker,
                work_order=report.work_order,
                work_order_process=report.work_order_process,
                passed_quantity=report.passed_quantity,
                report_created_at=report.created_at
            )
            detail.calculate()
            details_to_create.append(detail)

        SalarySettlementDetail.objects.bulk_create(details_to_create)
        settlement.update_statistics()
        settlement.lock_work_reports()

        result_serializer = SalarySettlementSerializer(settlement)
        return Response({
            'code': 200,
            'message': '结算单生成成功，相关报工数据已锁定',
            'data': result_serializer.data
        })


class SalaryFilterOptionsView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        if request.user.role not in ['admin', 'team_leader']:
            return Response({
                'code': 403,
                'message': '无权限访问'
            }, status=status.HTTP_403_FORBIDDEN)

        User = get_user_model()
        workers = User.objects.filter(role='worker').values('id', 'name').order_by('name')
        work_orders = WorkOrder.objects.filter(has_report=True).values('id', 'order_no').order_by('-created_at')
        processes = Process.objects.all().values('id', 'name').order_by('id')

        months = WorkReport.objects.filter(status='passed').dates('created_at', 'month', order='DESC')
        month_list = [m.strftime('%Y-%m') for m in months]

        current_month = timezone.now().strftime('%Y-%m')
        if current_month not in month_list:
            month_list.insert(0, current_month)

        return Response({
            'code': 200,
            'message': '成功',
            'data': {
                'workers': list(workers),
                'work_orders': list(work_orders),
                'processes': list(processes),
                'months': month_list,
                'current_month': current_month
            }
        })


class DashboardStatsView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        if request.user.role not in ['admin', 'team_leader']:
            return Response({
                'code': 403,
                'message': '无权限访问'
            }, status=status.HTTP_403_FORBIDDEN)

        today = timezone.now().date()
        current_month = timezone.now().strftime('%Y-%m')
        year, month_num = timezone.now().year, timezone.now().month

        today_report_count = WorkReport.objects.filter(
            created_at__date=today
        ).count()

        pending_inspection_count = WorkReport.objects.filter(
            status__in=['pending', 'rework'],
            is_locked=False
        ).count()

        in_progress_order_count = WorkOrder.objects.filter(
            status='in_progress'
        ).count()

        month_passed_reports = WorkReport.objects.filter(
            status='passed',
            created_at__year=year,
            created_at__month=month_num
        )
        monthly_salary = month_passed_reports.aggregate(
            total=Sum(F('passed_quantity') * F('work_order_process__process__price'))
        )['total']
        monthly_salary_total = float(monthly_salary or 0)

        process_yield_data = []
        all_processes = Process.objects.all()
        for proc in all_processes:
            reports = WorkReport.objects.filter(
                work_order_process__process=proc,
                status__in=['passed', 'rejected', 'rework']
            )
            total_qty = reports.aggregate(t=Sum('quantity'))['t'] or 0
            passed_qty = reports.aggregate(t=Sum('passed_quantity'))['t'] or 0
            if total_qty > 0:
                yield_rate = round(passed_qty / total_qty * 100, 1)
            else:
                yield_rate = 0
            process_yield_data.append({
                'name': proc.name,
                'total': total_qty,
                'passed': passed_qty,
                'yield_rate': yield_rate
            })
        process_yield_data.sort(key=lambda x: x['yield_rate'], reverse=True)

        product_scrap_data = []
        all_products = Product.objects.all()
        for prod in all_products:
            reports = WorkReport.objects.filter(
                work_order__product=prod,
                status__in=['passed', 'rejected', 'rework']
            )
            total_qty = reports.aggregate(t=Sum('quantity'))['t'] or 0
            scrapped_qty = reports.aggregate(t=Sum('scrapped_quantity'))['t'] or 0
            if total_qty > 0:
                scrap_rate = round(scrapped_qty / total_qty * 100, 1)
            else:
                scrap_rate = 0
            if scrapped_qty > 0:
                product_scrap_data.append({
                    'name': prod.name,
                    'total': total_qty,
                    'scrapped': scrapped_qty,
                    'scrap_rate': scrap_rate
                })
        product_scrap_data.sort(key=lambda x: x['scrap_rate'], reverse=True)

        in_progress_orders = WorkOrder.objects.filter(
            status='in_progress'
        ).select_related('product').prefetch_related('processes')

        order_progress_list = []
        for wo in in_progress_orders:
            is_overdue = wo.deadline < today
            total_reported = 0
            total_target = wo.quantity * wo.processes.count()
            for op in wo.processes.all():
                total_reported += min(op.reported_quantity, wo.quantity)
            progress_pct = int((total_reported / total_target) * 100) if total_target > 0 else 0

            reported_qty = sum(op.reported_quantity for op in wo.processes.all())
            passed_qty = sum(op.passed_quantity for op in wo.processes.all())

            order_progress_list.append({
                'id': wo.id,
                'order_no': wo.order_no,
                'product_name': wo.product.name,
                'quantity': wo.quantity,
                'deadline': wo.deadline.strftime('%Y-%m-%d'),
                'progress': progress_pct,
                'reported_quantity': reported_qty,
                'passed_quantity': passed_qty,
                'is_overdue': is_overdue,
                'process_count': wo.processes.count()
            })

        thirty_days_ago = today - timedelta(days=29)
        daily_reports = WorkReport.objects.filter(
            created_at__date__gte=thirty_days_ago
        ).annotate(day=TruncDate('created_at')).values('day').annotate(
            count=Count('id')
        ).order_by('day')

        daily_trend = []
        date_map = {item['day']: item['count'] for item in daily_reports}
        for i in range(30):
            d = thirty_days_ago + timedelta(days=i)
            daily_trend.append({
                'date': d.strftime('%m-%d'),
                'count': date_map.get(d, 0)
            })

        return Response({
            'code': 200,
            'message': '成功',
            'data': {
                'today_report_count': today_report_count,
                'pending_inspection_count': pending_inspection_count,
                'in_progress_order_count': in_progress_order_count,
                'monthly_salary_total': monthly_salary_total,
                'process_yield': process_yield_data,
                'product_scrap': product_scrap_data,
                'order_progress': order_progress_list,
                'daily_trend': daily_trend
            }
        })
