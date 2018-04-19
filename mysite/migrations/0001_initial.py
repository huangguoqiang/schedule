# Generated by Django 2.0.4 on 2018-04-19 07:05

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Person',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('team_id', models.PositiveSmallIntegerField()),
                ('team_name', models.CharField(max_length=30)),
                ('name', models.CharField(max_length=30, unique=True)),
                ('tel_num', models.CharField(max_length=20)),
                ('email', models.CharField(max_length=40)),
            ],
        ),
        migrations.CreateModel(
            name='Schedule',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('team_id', models.PositiveSmallIntegerField()),
                ('date', models.DateTimeField()),
                ('person_id', models.PositiveSmallIntegerField()),
                ('person_name', models.CharField(max_length=30)),
                ('shift_id', models.PositiveSmallIntegerField()),
                ('shift_name', models.CharField(max_length=30)),
                ('is_master', models.BooleanField()),
                ('is_base', models.BooleanField()),
            ],
            options={
                'ordering': ('date', 'id'),
            },
        ),
        migrations.CreateModel(
            name='Shift',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=30, unique=True)),
                ('time', models.CharField(max_length=30)),
            ],
        ),
        migrations.CreateModel(
            name='Team',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=30, unique=True)),
                ('description', models.CharField(max_length=200)),
            ],
        ),
    ]
