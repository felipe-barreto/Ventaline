# Generated by Django 2.2.3 on 2021-04-30 01:35

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('Tablas', '0011_auto_20210429_2233'),
    ]

    operations = [
        migrations.AlterUniqueTogether(
            name='lugar',
            unique_together={('provincia', 'nombre_ciudad')},
        ),
    ]
