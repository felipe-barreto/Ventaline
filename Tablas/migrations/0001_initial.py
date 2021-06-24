# Generated by Django 2.2.3 on 2021-06-24 18:54

import Tablas.softdeletion
from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion
import django.utils.timezone


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('auth', '0011_update_proxy_permissions'),
    ]

    operations = [
        migrations.CreateModel(
            name='Chofer',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('is_deleted', models.BooleanField(default=False)),
                ('deleted_at', models.DateTimeField(blank=True, null=True)),
                ('dni', models.CharField(max_length=20, validators=[Tablas.softdeletion.validar_dni_chofer])),
                ('telefono', models.CharField(max_length=15)),
            ],
            options={
                'verbose_name': 'chofer',
                'verbose_name_plural': 'choferes',
            },
        ),
        migrations.CreateModel(
            name='Cliente',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('is_deleted', models.BooleanField(default=False)),
                ('deleted_at', models.DateTimeField(blank=True, null=True)),
                ('dni', models.CharField(max_length=20, validators=[Tablas.softdeletion.validar_dni_cliente])),
                ('cantidad_de_caracteres_de_la_contraseña', models.CharField(blank=True, max_length=50, null=True)),
                ('fecha_nacimiento', models.DateField()),
                ('gold', models.BooleanField(default=False)),
                ('tarjeta_cod_seguridad', models.CharField(blank=True, max_length=3, null=True)),
                ('tarjeta_fecha_vencimiento', models.DateField(blank=True, null=True)),
                ('tarjeta_nombre_titular', models.CharField(blank=True, max_length=40, null=True)),
                ('tarjeta_numero', models.CharField(blank=True, max_length=16, null=True)),
                ('suspendido', models.BooleanField(default=False)),
                ('fecha_suspension', models.DateField(blank=True, null=True)),
                ('tuvo_coronavirus', models.BooleanField(default=False)),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='Combi',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('is_deleted', models.BooleanField(default=False)),
                ('deleted_at', models.DateTimeField(blank=True, null=True)),
                ('modelo', models.CharField(max_length=15)),
                ('patente', models.CharField(max_length=10, validators=[Tablas.softdeletion.validar_patente_combi])),
                ('cant_asientos', models.IntegerField()),
                ('tipo', models.CharField(choices=[('Cómoda', 'Cómoda'), ('Súper-cómoda', 'Súper-cómoda')], max_length=15)),
                ('chofer', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='Tablas.Chofer')),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='Compra',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('is_deleted', models.BooleanField(default=False)),
                ('deleted_at', models.DateTimeField(blank=True, null=True)),
                ('precio', models.IntegerField(blank=True, null=True)),
                ('asientos', models.IntegerField(blank=True, null=True)),
                ('estado', models.TextField(blank=True, max_length=30, null=True)),
                ('cliente', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.DO_NOTHING, related_name='compras', to='Tablas.Cliente')),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='Lugar',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('is_deleted', models.BooleanField(default=False)),
                ('deleted_at', models.DateTimeField(blank=True, null=True)),
                ('provincia', models.CharField(max_length=20)),
                ('nombre_ciudad', models.CharField(max_length=20)),
                ('observaciones', models.CharField(blank=True, max_length=40, null=True)),
            ],
            options={
                'verbose_name': 'lugar',
                'verbose_name_plural': 'lugares',
            },
        ),
        migrations.CreateModel(
            name='Producto',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('is_deleted', models.BooleanField(default=False)),
                ('deleted_at', models.DateTimeField(blank=True, null=True)),
                ('nombre', models.CharField(max_length=20, validators=[Tablas.softdeletion.validar_nombre_producto])),
                ('tipo', models.CharField(max_length=20)),
                ('precio', models.IntegerField()),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='Ruta',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('is_deleted', models.BooleanField(default=False)),
                ('deleted_at', models.DateTimeField(blank=True, null=True)),
                ('datos_adicionales', models.CharField(blank=True, max_length=40, null=True)),
                ('ciudad_destino', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='ciudad_destino', to='Tablas.Lugar')),
                ('ciudad_origen', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='ciudad_origen', to='Tablas.Lugar')),
                ('combi', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='Tablas.Combi')),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='CustomUser',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('password', models.CharField(max_length=128, verbose_name='password')),
                ('last_login', models.DateTimeField(blank=True, null=True, verbose_name='last login')),
                ('is_superuser', models.BooleanField(default=False, help_text='Designates that this user has all permissions without explicitly assigning them.', verbose_name='superuser status')),
                ('first_name', models.CharField(blank=True, max_length=30, verbose_name='first name')),
                ('last_name', models.CharField(blank=True, max_length=150, verbose_name='last name')),
                ('is_staff', models.BooleanField(default=False, help_text='Designates whether the user can log into this admin site.', verbose_name='staff status')),
                ('is_active', models.BooleanField(default=True, help_text='Designates whether this user should be treated as active. Unselect this instead of deleting accounts.', verbose_name='active')),
                ('date_joined', models.DateTimeField(default=django.utils.timezone.now, verbose_name='date joined')),
                ('is_deleted', models.BooleanField(default=False)),
                ('deleted_at', models.DateTimeField(blank=True, null=True)),
                ('email', models.EmailField(max_length=254, unique=True, verbose_name='email address')),
                ('groups', models.ManyToManyField(blank=True, help_text='The groups this user belongs to. A user will get all permissions granted to each of their groups.', related_name='user_set', related_query_name='user', to='auth.Group', verbose_name='groups')),
                ('user_permissions', models.ManyToManyField(blank=True, help_text='Specific permissions for this user.', related_name='user_set', related_query_name='user', to='auth.Permission', verbose_name='user permissions')),
            ],
            options={
                'verbose_name': 'user',
                'verbose_name_plural': 'users',
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='Viaje',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('is_deleted', models.BooleanField(default=False)),
                ('deleted_at', models.DateTimeField(blank=True, null=True)),
                ('fecha_hora', models.DateTimeField()),
                ('precio', models.IntegerField()),
                ('datos_adicionales', models.CharField(blank=True, max_length=40, null=True)),
                ('estado', models.TextField(blank=True, default='Pendiente', max_length=30, null=True)),
                ('ruta', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='Tablas.Ruta')),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='Compra_Producto',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('is_deleted', models.BooleanField(default=False)),
                ('deleted_at', models.DateTimeField(blank=True, null=True)),
                ('cantidad', models.IntegerField(blank=True, null=True)),
                ('compra', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='compra_producto', to='Tablas.Compra')),
                ('producto', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.DO_NOTHING, related_name='compra_producto', to='Tablas.Producto')),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.AddField(
            model_name='compra',
            name='viaje',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, related_name='compras', to='Tablas.Viaje'),
        ),
        migrations.CreateModel(
            name='Comentario',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('is_deleted', models.BooleanField(default=False)),
                ('deleted_at', models.DateTimeField(blank=True, null=True)),
                ('contenido', models.TextField(max_length=400)),
                ('fecha_de_creacion', models.DateTimeField()),
                ('autor', models.ForeignKey(on_delete=django.db.models.deletion.DO_NOTHING, related_name='comentarios', to='Tablas.Cliente')),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.AddField(
            model_name='cliente',
            name='usuario',
            field=models.OneToOneField(on_delete=django.db.models.deletion.DO_NOTHING, related_name='cliente', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='chofer',
            name='usuario',
            field=models.OneToOneField(limit_choices_to={'chofer': None, 'cliente': None, 'is_staff': False}, on_delete=django.db.models.deletion.DO_NOTHING, related_name='chofer', to=settings.AUTH_USER_MODEL),
        ),
    ]
