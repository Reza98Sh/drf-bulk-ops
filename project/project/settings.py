from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent

SECRET_KEY = "test-secret-key"

INSTALLED_APPS = [
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "rest_framework",
    "drf_spectacular",
    "drf_bulk_ops",
    "example_app",
]

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        # Use a file-based SQLite database for runserver
        "NAME": BASE_DIR / "db.sqlite3",
    }
}

REST_FRAMEWORK = {
    "DEFAULT_SCHEMA_CLASS": "drf_spectacular.openapi.AutoSchema",
}

ROOT_URLCONF = "project.urls"
DEFAULT_AUTO_FIELD = "django.db.models.AutoField"

DEBUG = True
USE_TZ = True

ALLOWED_HOSTS = ["*"]


TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [],
        },
    },
]

STATIC_URL = "static/"