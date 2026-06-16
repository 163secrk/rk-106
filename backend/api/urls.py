from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    LoginView,
    UserInfoView,
    ProductViewSet,
    ProcessViewSet,
    WorkOrderViewSet,
    WorkerListView
)

router = DefaultRouter()
router.register(r'products', ProductViewSet)
router.register(r'processes', ProcessViewSet)
router.register(r'workorders', WorkOrderViewSet)

urlpatterns = [
    path('login/', LoginView.as_view(), name='login'),
    path('userinfo/', UserInfoView.as_view(), name='userinfo'),
    path('workers/', WorkerListView.as_view(), name='worker-list'),
    path('', include(router.urls)),
]
