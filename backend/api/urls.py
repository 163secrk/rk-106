from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    LoginView,
    UserInfoView,
    ProductViewSet,
    ProcessViewSet,
    WorkOrderViewSet,
    WorkerListView,
    WorkerWorkOrderListView,
    WorkReportViewSet,
    InspectorPendingListView,
    InspectorHistoryListView,
    QualityInspectionView,
    WorkerReworkTaskListView,
    WorkerReworkTaskDetailView,
    SalarySummaryView,
    WorkReportTraceView,
    SalarySettlementListView,
    SalarySettlementDetailView,
    CreateSettlementView,
    SalaryFilterOptionsView
)

router = DefaultRouter()
router.register(r'products', ProductViewSet)
router.register(r'processes', ProcessViewSet)
router.register(r'workorders', WorkOrderViewSet)
router.register(r'workreports', WorkReportViewSet)

urlpatterns = [
    path('login/', LoginView.as_view(), name='login'),
    path('userinfo/', UserInfoView.as_view(), name='userinfo'),
    path('workers/', WorkerListView.as_view(), name='worker-list'),
    path('worker/workorders/', WorkerWorkOrderListView.as_view(), name='worker-workorder-list'),
    path('inspector/pending/', InspectorPendingListView.as_view(), name='inspector-pending-list'),
    path('inspector/history/', InspectorHistoryListView.as_view(), name='inspector-history-list'),
    path('workreports/<int:pk>/inspect/', QualityInspectionView.as_view(), name='workreport-inspect'),
    path('worker/rework-tasks/', WorkerReworkTaskListView.as_view(), name='worker-rework-task-list'),
    path('worker/rework-tasks/<int:pk>/', WorkerReworkTaskDetailView.as_view(), name='worker-rework-task-detail'),
    path('salary/summary/', SalarySummaryView.as_view(), name='salary-summary'),
    path('salary/filter-options/', SalaryFilterOptionsView.as_view(), name='salary-filter-options'),
    path('salary/settlements/', SalarySettlementListView.as_view(), name='salary-settlement-list'),
    path('salary/settlements/create/', CreateSettlementView.as_view(), name='salary-create-settlement'),
    path('salary/settlements/<int:pk>/', SalarySettlementDetailView.as_view(), name='salary-settlement-detail'),
    path('workreports/<int:pk>/trace/', WorkReportTraceView.as_view(), name='workreport-trace'),
    path('', include(router.urls)),
]
