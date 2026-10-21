from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("tutors", "0001_initial"),
    ]

    operations = [
        migrations.AddField(
            model_name="tutorprofile",
            name="photo",
            field=models.ImageField(
                blank=True,
                null=True,
                upload_to="tutor_photos/%Y/%m/",
            ),
        ),
    ]