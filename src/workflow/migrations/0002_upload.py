# Generated by Django 3.2.4 on 2021-06-08 23:44

from django.db import migrations, models
import uuid


class Migration(migrations.Migration):

    dependencies = [
        ('workflow', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Upload',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, primary_key=True, serialize=False)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('file', models.FileField(upload_to='workflow/files/')),
                ('success', models.BooleanField(default=False)),
                ('logs', models.JSONField(default=list)),
            ],
            options={
                'abstract': False,
            },
        ),
    ]