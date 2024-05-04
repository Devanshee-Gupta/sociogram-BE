# Generated by Django 4.1.13 on 2024-05-03 21:11

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ("home", "0002_users_bio_users_name"),
    ]

    operations = [
        migrations.CreateModel(
            name="LikedPost",
            fields=[
                ("liked_post_id", models.AutoField(primary_key=True, serialize=False)),
                (
                    "post",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE, to="home.post"
                    ),
                ),
                (
                    "user",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE, to="home.users"
                    ),
                ),
            ],
            options={
                "db_table": "liked_post",
                "unique_together": {("user", "post")},
            },
        ),
    ]
