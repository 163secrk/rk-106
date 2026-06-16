from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model


class Command(BaseCommand):
    help = '创建初始化用户（管理员和测试用户）'

    def handle(self, *args, **options):
        User = get_user_model()

        users = [
            {'username': 'admin', 'name': '管理员', 'role': 'admin', 'password': '123456', 'is_superuser': True, 'is_staff': True},
            {'username': 'leader01', 'name': '张组长', 'role': 'team_leader', 'password': '123456'},
            {'username': 'worker01', 'name': '李工人', 'role': 'worker', 'password': '123456'},
            {'username': 'inspector01', 'name': '王质检', 'role': 'inspector', 'password': '123456'},
        ]

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
                self.stdout.write(self.style.SUCCESS(f'用户 {username} 创建成功'))
            else:
                self.stdout.write(self.style.WARNING(f'用户 {username} 已存在'))

        self.stdout.write(self.style.SUCCESS('初始化用户完成'))
