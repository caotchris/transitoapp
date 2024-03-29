# Generated by Django 2.2.4 on 2020-01-19 23:25

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('Gestionar_Usuarios', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Accidente_Transito',
            fields=[
                ('NumeroAccidente', models.IntegerField(primary_key=True, serialize=False)),
                ('TipoAccidente', models.TextField()),
                ('Descripcion', models.TextField()),
                ('Ubicacion', models.TextField()),
                ('Latitud', models.DecimalField(blank=True, decimal_places=20, max_digits=30, null=True)),
                ('Longitud', models.DecimalField(blank=True, decimal_places=20, max_digits=30, null=True)),
                ('Estado', models.CharField(max_length=12, null=True)),
                ('Fecha', models.DateField()),
                ('Hora_Registro', models.TimeField()),
                ('Hora_Accidente', models.TimeField()),
                ('Agente', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='Gestionar_Usuarios.Agente_Transito')),
            ],
            options={
                'verbose_name': 'Accidente_Transito',
                'verbose_name_plural': 'Accidentes_Transito',
            },
        ),
    ]
