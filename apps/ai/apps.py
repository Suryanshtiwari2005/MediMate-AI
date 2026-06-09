from django.apps import AppConfig
import sys

class AiConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'apps.ai'
    verbose_name = 'AI Engine'

    def ready(self):
        # Feature #70: Hook scheduler startup safely
        if 'manage.py' in sys.argv and 'runserver' in sys.argv:
            from scheduler.jobs import start_scheduler
            start_scheduler()
        elif 'manage.py' not in sys.argv:
            # Production environment (Gunicorn/WSGI)
            from scheduler.jobs import start_scheduler
            start_scheduler()
