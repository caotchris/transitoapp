# Generated by Django 2.2.4 on 2020-01-20 01:23

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('Gestionar_Accidente', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='ContadorAccidente',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('CedulaAgente', models.IntegerField()),
                ('CodigoAgente', models.IntegerField()),
                ('ContadorAgente', models.IntegerField()),
            ],
        ),
    ]
