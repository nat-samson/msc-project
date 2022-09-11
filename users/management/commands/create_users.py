import csv

from django.core.management import BaseCommand

from users.models import User


class Command(BaseCommand):
    """Terminal command for creating new users (both students and teachers) in bulk using data from a CSV file."""

    help = 'Create teachers and students from users.csv'

    def handle(self, *args, **kwargs):
        with open('users/management/commands/users.csv', 'r') as users_file:
            reader = csv.DictReader(users_file)
            users_to_create = []

            for row in reader:
                password = row.pop('password')
                is_teacher = bool(row.pop('is_teacher'))
                user = User(**row, is_teacher=is_teacher)
                user.set_password(password)
                users_to_create.append(user)

            User.objects.bulk_create(users_to_create)
