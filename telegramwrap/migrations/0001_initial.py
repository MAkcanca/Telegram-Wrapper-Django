# Generated by Django 3.0.2 on 2020-01-16 21:49

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Account',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('token', models.CharField(max_length=150)),
                ('telegram_api_id', models.CharField(max_length=50)),
                ('telegram_api_hash', models.CharField(max_length=150)),
            ],
        ),
        migrations.CreateModel(
            name='WebhookUrl',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('url', models.CharField(max_length=150)),
            ],
        ),
    ]
