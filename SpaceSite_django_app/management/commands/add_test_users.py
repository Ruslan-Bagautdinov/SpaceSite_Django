from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand

from SpaceSite_django_app.models import UserProfile

User = get_user_model()


class Command(BaseCommand):
    help = 'Add test users to the database'

    def handle(self, *args, **kwargs):
        # Create test user
        user, created = User.objects.get_or_create(
            username='user',
            email='user@example.com',
            defaults={'password': '123'}
        )
        if created:
            user.set_password('123')
            user.save()
            UserProfile.objects.create(user=user)
            self.stdout.write(self.style.SUCCESS('Successfully created test user'))

        # Create test admin
        admin, created = User.objects.get_or_create(
            username='admin',
            email='admin@example.com',
            defaults={'password': '123', 'role': 'admin'}
        )
        if created:
            admin.set_password('123')
            admin.save()
            UserProfile.objects.create(user=admin)
            self.stdout.write(self.style.SUCCESS('Successfully created test admin'))
