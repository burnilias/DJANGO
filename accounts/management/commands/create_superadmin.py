from django.core.management.base import BaseCommand
from django.contrib.auth.hashers import make_password
from accounts.models import CustomUser


class Command(BaseCommand):
    help = 'Create the first admin user (role=admin, status=active)'

    def handle(self, *args, **options):
        self.stdout.write('--- Create Super Admin ---')

        name = input('Name: ').strip()
        email = input('Email: ').strip()
        password = input('Password: ').strip()

        if not name or not email or not password:
            self.stderr.write(self.style.ERROR('All fields are required.'))
            return

        if CustomUser.objects.filter(email=email).exists():
            self.stderr.write(self.style.ERROR(f'A user with email "{email}" already exists.'))
            return

        parts = name.split(' ', 1)
        first_name = parts[0]
        last_name = parts[1] if len(parts) > 1 else ''

        user = CustomUser(
            email=email,
            first_name=first_name,
            last_name=last_name,
            password=make_password(password),
            role='admin',
            status='active',
            is_staff=True,
            is_superuser=True,
        )
        user.save()

        self.stdout.write(self.style.SUCCESS(
            f'Admin user "{email}" created successfully.'
        ))
