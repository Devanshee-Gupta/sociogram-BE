# Generated by Django 4.1.13 on 2024-05-04 12:29

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ("home", "0004_alter_saveditem_unique_together"),
    ]

    operations = [
        migrations.DeleteModel(
            name="Comment",
        ),
    ]
