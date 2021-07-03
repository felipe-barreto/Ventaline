# Generated by Django 2.2.3 on 2021-07-02 16:43

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('Tablas', '0003_auto_20210630_1723'),
    ]

    operations = [
        migrations.AddField(
            model_name='cliente',
            name='fechas_de_suspension',
            field=models.ManyToManyField(to='Tablas.Suspendido'),
        ),
        migrations.AddField(
            model_name='viaje',
            name='Los_viajes_vendidos',
            field=models.BooleanField(default=False),
        ),
        migrations.RemoveField(
            model_name='cliente',
            name='Los_clientes_que_fueron_sospechosos_de_tener_coronavirus',
        ),
        migrations.AddField(
            model_name='cliente',
            name='Los_clientes_que_fueron_sospechosos_de_tener_coronavirus',
            field=models.BooleanField(default=False),
        ),
    ]
