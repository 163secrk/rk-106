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
    WorkReportViewSet
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
    path('', include(router.urls)),
]
