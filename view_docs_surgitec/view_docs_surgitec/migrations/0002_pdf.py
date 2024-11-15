# Generated by Django 5.1.3 on 2024-11-10 17:59

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('view_docs_surgitec', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='PDF',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('link', models.URLField()),
                ('funcionario', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='view_docs_surgitec.funcionario')),
            ],
        ),
    ]