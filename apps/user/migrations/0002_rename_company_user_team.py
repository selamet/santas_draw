# Generated by Django 5.1.3 on 2024-11-20 20:24

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('user', '0001_initial'),
    ]

    operations = [
        migrations.RenameField(
            model_name='user',
            old_name='company',
            new_name='team',
        ),
    ]
