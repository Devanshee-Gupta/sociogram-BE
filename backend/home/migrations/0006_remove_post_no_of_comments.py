# Generated by Django 4.1.13 on 2024-05-04 15:10

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ("home", "0005_delete_comment"),
    ]

    operations = [
        migrations.RemoveField(
            model_name="post",
            name="no_of_comments",
        ),
    ]
