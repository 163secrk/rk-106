import os, sys, django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'pro_flow.settings')
sys.path.insert(0, os.path.dirname(__file__))
django.setup()

from api.models import User, WorkOrder, WorkOrderProcess, WorkReport
from django.contrib.auth import get_user_model

User = get_user_model()

zhangsan = User.objects.get(username='zhangsan')
lisi = User.objects.get(username='lisi')
wangwu = User.objects.get(username='wangwu')
zhaoliu = User.objects.get(username='zhaoliu')

work_orders = WorkOrder.objects.all()

print('创建测试报工记录...')

for wo in work_orders:
    print(f'\n工单: {wo.order_no} ({wo.product.name})')
    for wop in wo.processes.all():
        workers = wop.workers.all()
        if workers.exists() and wo.status in ['pending', 'in_progress']:
            worker = workers.first()
            quantity = min(50, wo.quantity - wop.reported_quantity)
            if quantity > 0 and not WorkReport.objects.filter(
                work_order=wo,
                work_order_process=wop,
                worker=worker,
                status='pending'
            ).exists():
                report = WorkReport.objects.create(
                    work_order=wo,
                    work_order_process=wop,
                    worker=worker,
                    quantity=quantity,
                    status='pending'
                )
                wop.reported_quantity += quantity
                wop.save()
                wo.has_report = True
                wo.save()
                print(f'  ✓ {wop.process.name}: {worker.name} 报工 {quantity} 件')

print('\n测试报工记录创建完成！')
print('\n现有报工记录:')
for wr in WorkReport.objects.all():
    print(f'  {wr.id}: {wr.work_order.order_no} - {wr.process_name} - {wr.worker_name} - {wr.quantity}件 - {wr.status_name}')
