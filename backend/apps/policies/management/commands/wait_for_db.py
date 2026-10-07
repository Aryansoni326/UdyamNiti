"""Wait for database to be ready before starting."""
import time
from django.core.management.base import BaseCommand
from django.db import connections
from django.db.utils import OperationalError


class Command(BaseCommand):
    help = 'Wait for database to be ready'

    def handle(self, *args, **options):
        self.stdout.write('Waiting for database...')
        db_conn = None
        while not db_conn:
            try:
                db_conn = connections['default']
                db_conn.ensure_connection()
            except OperationalError:
                self.stdout.write('Database unavailable, waiting 1 second...')
                time.sleep(1)
        self.stdout.write(self.style.SUCCESS('Database available!'))
        try:
            with db_conn.cursor() as cursor:
                cursor.execute('CREATE EXTENSION IF NOT EXISTS vector;')
            self.stdout.write(self.style.SUCCESS('pgvector extension enabled!'))
        except Exception as e:
            self.stdout.write(self.style.WARNING(f'Note: pgvector extension check: {e}'))

        try:
            from django.core.management import call_command
            apps_to_migrate = [
                'accounts', 'actions', 'business_profiles', 'documents',
                'eligibility', 'observability', 'opportunities', 'policies',
                'policy_monitoring', 'rag', 'relationships', 'strategy'
            ]
            self.stdout.write('Generating schema migrations for all apps...')
            call_command('makemigrations', *apps_to_migrate, interactive=False)
            self.stdout.write('Applying migrations...')
            call_command('migrate', interactive=False)
            self.stdout.write(self.style.SUCCESS('All migrations applied successfully!'))
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'Migration error: {e}'))
