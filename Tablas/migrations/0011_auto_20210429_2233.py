# Generated by Django 2.2.3 on 2021-04-30 01:33

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('Tablas', '0010_auto_20210429_2232'),
    ]

    operations = [
        migrations.AlterField(
            model_name='producto',
            name='nombre',
            field=models.CharField(max_length=20, unique=True),
        ),
    ]
