"""Minimal Django settings for the smart-home web frontend.

The web view is a thin presentation layer over the client's in-memory storages,
so there is no database, no ORM and no migrations. Only the templating and
static-file machinery is enabled.
"""

from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent

# Demo-only key; this frontend is meant to run locally for a single user.
SECRET_KEY = "smart-home-simulator-demo-key-not-for-production"

DEBUG = True

ALLOWED_HOSTS = ["*"]

INSTALLED_APPS = [
    "django.contrib.staticfiles",
]

MIDDLEWARE = [
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
]

ROOT_URLCONF = "smart_home.client.views.web.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [BASE_DIR / "templates"],
        "APP_DIRS": False,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.request",
            ],
        },
    },
]

# No relational data is used; keep the ORM unconfigured.
DATABASES = {}

STATIC_URL = "static/"
STATICFILES_DIRS = [BASE_DIR / "static"]

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

USE_TZ = True
