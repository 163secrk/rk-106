from rest_framework import status, viewsets
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth import authenticate
from django.utils import timezone
from django.db.models import Sum
from .models import Product, Process, WorkOrder, WorkOrderProcess, WorkReport, ReworkTask
from .serializers import (
    UserSerializer,
    ProductSerializer,
    ProcessSerializer,
    WorkOrderSerializer,
    WorkOrderListSerializer,
    WorkReportSerializer,
    WorkerWorkOrderSerializer,
    QualityInspectionSerializer,
    ReworkTaskSerializer,
    InspectorWorkReportSerializer
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
    serializer_class = ProductSerializer
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
