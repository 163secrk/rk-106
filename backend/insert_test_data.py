import os, sys, django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'pro_flow.settings')
sys.path.insert(0, os.path.dirname(__file__))
django.setup()

from api.models import User, Product, Process, WorkOrder, WorkOrderProcess, WorkReport
from datetime import date

# 检查现有数据
print('=== 用户 ===')
for u in User.objects.all():
    print(f'  {u.id}: {u.username} ({u.name}) role={u.role}')
print(f'  Worker count: {User.objects.filter(role="worker").count()}')

print('\n=== 产品 ===')
for p in Product.objects.all():
    print(f'  {p.id}: {p.name} code={p.code}')

print('\n=== 工序 ===')
for p in Process.objects.all():
    print(f'  {p.id}: {p.name} code={p.code} price={p.price}')

print('\n=== 工单 ===')
for wo in WorkOrder.objects.all():
    print(f'  {wo.id}: {wo.order_no} product={wo.product.name} qty={wo.quantity} status={wo.status}')
    for wop in wo.processes.all():
        workers = ', '.join([w.name for w in wop.workers.all()])
        print(f'    WOP_{wop.id}: process={wop.process.name} workers=[{workers}] reported={wop.reported_quantity}')

print('\n=== 报工记录 ===')
for wr in WorkReport.objects.all():
    print(f'  {wr.id}: wo={wr.work_order.order_no} wop={wr.work_order_process.process.name} worker={wr.worker.name} qty={wr.quantity} status={wr.status}')
