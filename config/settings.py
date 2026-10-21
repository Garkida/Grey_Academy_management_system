"""
Django settings for Grey Academy.

Read through the comments if this is your first time in a Django settings
file — they explain WHY each block is here, not just what it does.
"""

from pathlib import Path

from decouple import Csv, config

BASE_DIR = Path(__file__).resolve().parent.parent

# --------------------------------------------------------------------------
# Core / security
# --------------------------------------------------------------------------
# SECRET_KEY and anything else "secret" lives in a local .env file (see
# .env.example) and is loaded with python-decouple, so real secrets never
# get committed to git.
SECRET_KEY = config("SECRET_KEY", default="dev-insecure-secret-key-change-me")
DEBUG = config("DEBUG", default=True, cast=bool)
ALLOWED_HOSTS = config("ALLOWED_HOSTS", default="127.0.0.1,localhost", cast=Csv())

# --------------------------------------------------------------------------
# Applications
# --------------------------------------------------------------------------
INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "django.contrib.sites",  # required by django-allauth
    # Third-party
    "allauth",
    "allauth.account",
    "allauth.socialaccount",
    "allauth.socialaccount.providers.google",
    "rest_framework",
    # Local apps
    "accounts",
    "core",
    "payments",
    "attendance",
    "tutors",
    "academy_api",
]

REST_FRAMEWORK = {
    "DEFAULT_AUTHENTICATION_CLASSES": [
        "rest_framework.authentication.SessionAuthentication",
    ],
    "DEFAULT_PERMISSION_CLASSES": [
        "rest_framework.permissions.IsAuthenticated",
    ],
}

SITE_ID = 1

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
    "allauth.account.middleware.AccountMiddleware",
]

ROOT_URLCONF = "config.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [BASE_DIR / "templates"],  # project-level templates (base.html lives here)
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ],
        },
    },
]

WSGI_APPLICATION = "config.wsgi.application"

# --------------------------------------------------------------------------
# Database (SQLite for development; swap the ENGINE for Postgres in prod)
# --------------------------------------------------------------------------
DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": BASE_DIR / "db.sqlite3",
    }
}

AUTH_PASSWORD_VALIDATORS = [
    # {"NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator"},
    # {"NAME": "django.contrib.auth.password_validation.MinimumLengthValidator"},
    # {"NAME": "django.contrib.auth.password_validation.CommonPasswordValidator"},
    # {"NAME": "django.contrib.auth.password_validation.NumericPasswordValidator"},
]

# --------------------------------------------------------------------------
# Custom user model
# --------------------------------------------------------------------------
# IMPORTANT: this must be set before your very first `migrate`. Switching to
# a custom user model after tables already exist means starting the
# database over, so we set it up from day one.
AUTH_USER_MODEL = "accounts.User"

# --------------------------------------------------------------------------
# Authentication backends
# --------------------------------------------------------------------------
AUTHENTICATION_BACKENDS = [
    "django.contrib.auth.backends.ModelBackend",  # email/password login
    # "allauth.account.auth_backends.AuthenticationBackend",  # Google login
]

LOGIN_URL = "accounts:login"
LOGIN_REDIRECT_URL = "core:dashboard"
LOGOUT_REDIRECT_URL = "core:home"

# --------------------------------------------------------------------------
# django-allauth — Google sign-in
# --------------------------------------------------------------------------
# Fill in GOOGLE_CLIENT_ID / GOOGLE_CLIENT_SECRET in your .env once you've
# created OAuth credentials in Google Cloud Console. See README.md for the
# step-by-step walkthrough.
ACCOUNT_EMAIL_VERIFICATION = "none"  # we handle verification ourselves (see accounts app)
ACCOUNT_LOGIN_METHODS = {"email"}
ACCOUNT_SIGNUP_FIELDS = ["email*", "password1*", "password2*"]
ACCOUNT_UNIQUE_EMAIL = True
SOCIALACCOUNT_LOGIN_ON_GET = True  # skip allauth's extra confirm screen for Google

SOCIALACCOUNT_PROVIDERS = {
    "google": {
        "APP": {
            "client_id": config("GOOGLE_CLIENT_ID", default=""),
            "secret": config("GOOGLE_CLIENT_SECRET", default=""),
            "key": "",
        },
        "SCOPE": ["profile", "email"],
        "AUTH_PARAMS": {"access_type": "online"},
    }
}

# --------------------------------------------------------------------------
# Internationalisation
# --------------------------------------------------------------------------
LANGUAGE_CODE = "en-us"
TIME_ZONE = "Africa/Lagos"
USE_I18N = True
USE_TZ = True

# --------------------------------------------------------------------------
# Static & media files
# --------------------------------------------------------------------------
STATIC_URL = "static/"
STATICFILES_DIRS = [BASE_DIR / "static"]
STATIC_ROOT = BASE_DIR / "staticfiles"  # used by `collectstatic` in production

MEDIA_URL = "media/"
MEDIA_ROOT = BASE_DIR / "media"

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

# --------------------------------------------------------------------------
# Email
# --------------------------------------------------------------------------
# In development, emails print straight to the terminal (console backend) —
# no real inbox needed while you're building. Switch EMAIL_BACKEND in your
# .env to an SMTP backend (e.g. Gmail, SendGrid, Mailgun) for production.
EMAIL_BACKEND = config(
    "EMAIL_BACKEND", default="django.core.mail.backends.console.EmailBackend"
)
EMAIL_HOST = config("EMAIL_HOST", default="")
EMAIL_PORT = config("EMAIL_PORT", default=587, cast=int)
EMAIL_HOST_USER = config("EMAIL_HOST_USER", default="")
EMAIL_HOST_PASSWORD = config("EMAIL_HOST_PASSWORD", default="")
EMAIL_USE_TLS = config("EMAIL_USE_TLS", default=True, cast=bool)
DEFAULT_FROM_EMAIL = config("DEFAULT_FROM_EMAIL", default="Grey Academy <no-reply@greyacademy.test>")

PAYSTACK_PUBLIC_KEY = config("PAYSTACK_PUBLIC_KEY", default="")
PAYSTACK_SECRET_KEY = config("PAYSTACK_SECRET_KEY", default="")


# --- Attendance settings ---

# Find these by opening Google Maps, right-clicking the academy's exact
# location, and clicking the coordinates that appear at the top of the
# menu (they copy straight to your clipboard).
ACADEMY_LATITUDE =  10.462623  #  replace with your real latitude
ACADEMY_LONGITUDE =  7.423888   # replace with your real longitude
ACADEMY_CHECKIN_RADIUS_METERS = 150
 
# The public IP address of the academy's Wi-Fi router.
# Find it by connecting to that Wi-Fi and visiting https://whatismyip.com
# Leave as an empty string until you have the real value — the IP check
# will simply never match, which is safe (GPS can still work on its own).
ACADEMY_WIFI_PUBLIC_IP = config("ACADEMY_WIFI_PUBLIC_IP", default="")