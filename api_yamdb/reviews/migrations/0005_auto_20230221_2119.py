# Generated by Django 3.2 on 2023-02-21 19:19

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('reviews', '0004_auto_20230221_2110'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='category',
            options={'verbose_name': 'Категория', 'verbose_name_plural': 'Категории'},
        ),
        migrations.AlterModelOptions(
            name='genres',
            options={'verbose_name': 'Жанр', 'verbose_name_plural': 'Жанры'},
        ),
    ]
