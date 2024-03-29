# Generated by Django 2.2.4 on 2020-01-23 00:22

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('Gestionar_Infraccion', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='ArticulosBD',
            fields=[
                ('NumeroArticuloBD', models.IntegerField(primary_key=True, serialize=False)),
                ('DescripcionBDA', models.TextField()),
            ],
        ),
        migrations.CreateModel(
            name='IncisosBD',
            fields=[
                ('NumeroIncisoBD', models.IntegerField(primary_key=True, serialize=False)),
                ('DescripcionBDI', models.TextField()),
            ],
        ),
        migrations.CreateModel(
            name='Multa',
            fields=[
                ('NumeroBD', models.IntegerField(primary_key=True, serialize=False)),
                ('Porcentaje', models.DecimalField(decimal_places=20, max_digits=30)),
            ],
        ),
        migrations.CreateModel(
            name='NumeralBD',
            fields=[
                ('NumeroNumeralBD', models.IntegerField(primary_key=True, serialize=False)),
                ('DescripcionBDN', models.TextField()),
            ],
        ),
        migrations.CreateModel(
            name='SBU',
            fields=[
                ('SalarioBD', models.IntegerField(primary_key=True, serialize=False)),
                ('Salario', models.DecimalField(decimal_places=20, max_digits=30)),
            ],
        ),
        migrations.AddField(
            model_name='infraccion_transito',
            name='Valor',
            field=models.DecimalField(blank=True, decimal_places=20, max_digits=30, null=True),
        ),
    ]
