# Generated by Django 4.2.20 on 2025-06-09 16:22

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('PerfectSpot', '0002_interest_customuser_interests'),
    ]

    operations = [
        migrations.AlterField(
            model_name='customuser',
            name='user_type',
            field=models.CharField(choices=[('individual', 'Individual'), ('organization', 'Organization')], default='individual', max_length=20),
        ),
    ]
