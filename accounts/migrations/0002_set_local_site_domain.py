"""
Sets the django.contrib.sites default Site row to something sensible for
local development (127.0.0.1:8000) instead of Django's placeholder
'example.com'. django-allauth and the password-reset emails both build
links using this Site's domain, so leaving it as 'example.com' means every
email link would point to the wrong place.

When you deploy this project for real, update the Site's domain again
(Admin -> Sites -> example.com) to your actual production domain — e.g.
greyacademy.com — or add another data migration like this one.
"""

from django.db import migrations


def set_local_site(apps, schema_editor):
    Site = apps.get_model("sites", "Site")
    site, _ = Site.objects.get_or_create(id=1)
    site.domain = "127.0.0.1:8000"
    site.name = "Grey Academy (local)"
    site.save()


def reverse_noop(apps, schema_editor):
    pass  # nothing meaningful to reverse


class Migration(migrations.Migration):

    dependencies = [
        ("accounts", "0001_initial"),
        ("sites", "0001_initial"),
    ]

    operations = [
        migrations.RunPython(set_local_site, reverse_noop),
    ]
