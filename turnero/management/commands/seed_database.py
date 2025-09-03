from django.core.management.base import BaseCommand
from turnero.utils import seed_database

class Command(BaseCommand):
    help = 'Seeds the database with a complete set of test data for development.'

    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS('Starting database seeding process...'))
        try:
            seed_database()
            self.stdout.write(self.style.SUCCESS('Successfully seeded the database.'))
        except Exception as e:
            self.stderr.write(self.style.ERROR(f'An error occurred during seeding: {e}'))
