# Generated by Django 3.1.1 on 2020-09-17 17:03

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('user', '0002_auto_20200917_1938'),
    ]

    operations = [
        migrations.AlterField(
            model_name='customuser',
            name='inn',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='users', to='user.inn'),
        ),
    ]
