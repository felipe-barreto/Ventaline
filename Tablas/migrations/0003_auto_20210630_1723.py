# Generated by Django 2.2.3 on 2021-06-30 20:23

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('Tablas', '0002_auto_20210630_1608'),
    ]

    operations = [
        migrations.RenameField(
            model_name='cliente',
            old_name='fue_suspendido',
            new_name='Los_clientes_que_fueron_sospechosos_de_tener_coronavirus',
        ),
        migrations.RemoveField(
            model_name='cliente',
            name='los_clientes_que_tuvieron_coronavirus',
        ),
    ]
