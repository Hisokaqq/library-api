# Generated by Django 5.0.7 on 2024-07-20 17:46

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('library', '0002_alter_genre_name'),
    ]

    operations = [
        migrations.AlterField(
            model_name='genre',
            name='name',
            field=models.CharField(max_length=100),
        ),
    ]
