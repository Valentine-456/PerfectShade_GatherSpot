# Generated by Django 4.2.20 on 2025-03-30 11:13

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('PerfectSpot', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='OrganizationProxy',
            fields=[
            ],
            options={
                'verbose_name': 'Organization',
                'verbose_name_plural': 'Organizations',
                'proxy': True,
                'indexes': [],
                'constraints': [],
            },
            bases=('PerfectSpot.customuser',),
        ),
    ]
