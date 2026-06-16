from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from api.models import Product, Process, WorkOrder, WorkOrderProcess
from django.utils import timezone
from datetime import timedelta


class Command(BaseCommand):
    help = '创建完整的初始化数据（用户、产品、工序、测试工单）'

    def handle(self, *args, **options):
        User = get_user_model()

        self.stdout.write(self.style.SUCCESS('=' * 50))
        self.stdout.write(self.style.SUCCESS('开始创建初始化数据'))
        self.stdout.write(self.style.SUCCESS('=' * 50))

        users = [
            {'username': 'admin', 'name': '管理员', 'role': 'admin', 'password': '123456', 'is_superuser': True, 'is_staff': True},
            {'username': 'leader01', 'name': '张组长', 'role': 'team_leader', 'password': '123456'},
            {'username': 'zhangsan', 'name': '张三', 'role': 'worker', 'password': '123456'},
            {'username': 'lisi', 'name': '李四', 'role': 'worker', 'password': '123456'},
            {'username': 'wangwu', 'name': '王五', 'role': 'worker', 'password': '123456'},
            {'username': 'zhaoliu', 'name': '赵六', 'role': 'worker', 'password': '123456'},
            {'username': 'inspector01', 'name': '王质检', 'role': 'inspector', 'password': '123456'},
        ]

        created_users = {}
        for user_data in users:
            username = user_data['username']
            if not User.objects.filter(username=username).exists():
                user = User.objects.create_user(
                    username=username,
                    password=user_data['password'],
                    name=user_data['name'],
                    role=user_data['role'],
                )
                if user_data.get('is_superuser'):
                    user.is_superuser = True
                    user.is_staff = True
                    user.save()
                self.stdout.write(self.style.SUCCESS(f'✓ 用户 {username}({user.name}) 创建成功'))
            else:
                user = User.objects.get(username=username)
                self.stdout.write(self.style.WARNING(f'- 用户 {username} 已存在'))
            created_users[username] = user

        processes = [
            {'name': '裁剪', 'code': 'PROC001', 'price': 2.5},
            {'name': '缝制', 'code': 'PROC002', 'price': 8.0},
            {'name': '锁眼', 'code': 'PROC003', 'price': 1.5},
            {'name': '整烫', 'code': 'PROC004', 'price': 3.0},
            {'name': '包装', 'code': 'PROC005', 'price': 1.0},
        ]

        created_processes = {}
        for proc_data in processes:
            code = proc_data['code']
            if not Process.objects.filter(code=code).exists():
                proc = Process.objects.create(**proc_data)
                self.stdout.write(self.style.SUCCESS(f'✓ 工序 {proc.name} 创建成功'))
            else:
                proc = Process.objects.get(code=code)
                self.stdout.write(self.style.WARNING(f'- 工序 {proc.name} 已存在'))
            created_processes[code] = proc

        products = [
            {'name': '冲锋衣', 'code': 'PROD001', 'spec': 'M/L/XL 三色'},
            {'name': '牛仔裤', 'code': 'PROD002', 'spec': '28-36码'},
            {'name': 'T恤衫', 'code': 'PROD003', 'spec': 'S-XXL 纯棉'},
            {'name': '羽绒服', 'code': 'PROD004', 'spec': '白鸭绒填充'},
        ]

        created_products = {}
        for prod_data in products:
            code = prod_data['code']
            if not Product.objects.filter(code=code).exists():
                prod = Product.objects.create(**prod_data)
                self.stdout.write(self.style.SUCCESS(f'✓ 产品 {prod.name} 创建成功'))
            else:
                prod = Product.objects.get(code=code)
                self.stdout.write(self.style.WARNING(f'- 产品 {prod.name} 已存在'))
            created_products[code] = prod

        if WorkOrder.objects.count() == 0:
            leader = created_users['leader01']
            zhangsan = created_users['zhangsan']
            lisi = created_users['lisi']
            wangwu = created_users['wangwu']
            zhaoliu = created_users['zhaoliu']

            today = timezone.now()

            work_order_data = [
                {
                    'product': created_products['PROD001'],
                    'quantity': 500,
                    'deadline': (today + timedelta(days=7)).date(),
                    'status': 'pending',
                    'has_report': False,
                    'processes': [
                        {'process': created_processes['PROC001'], 'workers': [zhangsan]},
                        {'process': created_processes['PROC002'], 'workers': [lisi, wangwu]},
                        {'process': created_processes['PROC003'], 'workers': [zhaoliu]},
                        {'process': created_processes['PROC004'], 'workers': [zhangsan]},
                        {'process': created_processes['PROC005'], 'workers': [zhaoliu]},
                    ]
                },
                {
                    'product': created_products['PROD002'],
                    'quantity': 300,
                    'deadline': (today + timedelta(days=5)).date(),
                    'status': 'in_progress',
                    'has_report': True,
                    'processes': [
                        {'process': created_processes['PROC001'], 'workers': [zhangsan], 'reported': 300},
                        {'process': created_processes['PROC002'], 'workers': [lisi], 'reported': 200},
                        {'process': created_processes['PROC003'], 'workers': [wangwu], 'reported': 150},
                        {'process': created_processes['PROC004'], 'workers': [zhaoliu], 'reported': 100},
                        {'process': created_processes['PROC005'], 'workers': [zhangsan], 'reported': 0},
                    ]
                },
                {
                    'product': created_products['PROD003'],
                    'quantity': 1000,
                    'deadline': (today + timedelta(days=10)).date(),
                    'status': 'pending',
                    'has_report': False,
                    'processes': [
                        {'process': created_processes['PROC001'], 'workers': [zhangsan, wangwu]},
                        {'process': created_processes['PROC002'], 'workers': [lisi, zhaoliu]},
                        {'process': created_processes['PROC003'], 'workers': [zhangsan]},
                        {'process': created_processes['PROC004'], 'workers': [wangwu]},
                        {'process': created_processes['PROC005'], 'workers': [zhaoliu]},
                    ]
                },
                {
                    'product': created_products['PROD004'],
                    'quantity': 200,
                    'deadline': (today + timedelta(days=3)).date(),
                    'status': 'completed',
                    'has_report': True,
                    'processes': [
                        {'process': created_processes['PROC001'], 'workers': [zhangsan], 'reported': 200},
                        {'process': created_processes['PROC002'], 'workers': [lisi], 'reported': 200},
                        {'process': created_processes['PROC003'], 'workers': [wangwu], 'reported': 200},
                        {'process': created_processes['PROC004'], 'workers': [zhaoliu], 'reported': 200},
                        {'process': created_processes['PROC005'], 'workers': [zhangsan], 'reported': 200},
                    ]
                },
            ]

            for idx, wo_data in enumerate(work_order_data):
                date_str = today.strftime('%Y%m%d')
                order_no = f'WO{date_str}{idx + 1:04d}'

                wo = WorkOrder.objects.create(
                    order_no=order_no,
                    product=wo_data['product'],
                    quantity=wo_data['quantity'],
                    deadline=wo_data['deadline'],
                    status=wo_data['status'],
                    has_report=wo_data['has_report'],
                    created_by=leader,
                )

                for proc_data in wo_data['processes']:
                    wo_proc = WorkOrderProcess.objects.create(
                        work_order=wo,
                        process=proc_data['process'],
                        reported_quantity=proc_data.get('reported', 0),
                        passed_quantity=proc_data.get('reported', 0),
                    )
                    wo_proc.workers.set(proc_data['workers'])

                self.stdout.write(self.style.SUCCESS(f'✓ 工单 {order_no}({wo.product.name}) 创建成功'))
        else:
            self.stdout.write(self.style.WARNING('- 已存在工单数据，跳过创建'))

        self.stdout.write(self.style.SUCCESS('=' * 50))
        self.stdout.write(self.style.SUCCESS('初始化数据创建完成！'))
        self.stdout.write(self.style.SUCCESS('=' * 50))
        self.stdout.write(self.style.SUCCESS(''))
        self.stdout.write(self.style.SUCCESS('测试账号：'))
        self.stdout.write(self.style.SUCCESS('  组长: leader01 / 123456 (张组长)'))
        self.stdout.write(self.style.SUCCESS('  工人: zhangsan / 123456 (张三)'))
        self.stdout.write(self.style.SUCCESS('  工人: lisi / 123456 (李四)'))
        self.stdout.write(self.style.SUCCESS('  工人: wangwu / 123456 (王五)'))
        self.stdout.write(self.style.SUCCESS('  工人: zhaoliu / 123456 (赵六)'))
