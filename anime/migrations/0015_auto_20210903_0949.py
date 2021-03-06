# Generated by Django 3.2.6 on 2021-09-03 04:19

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('anime', '0014_alter_anime_options'),
    ]

    operations = [
        migrations.AddField(
            model_name='anime',
            name='age_rating',
            field=models.CharField(blank=True, max_length=20, null=True),
        ),
        migrations.AddField(
            model_name='anime',
            name='director',
            field=models.CharField(blank=True, max_length=150, null=True),
        ),
        migrations.AddField(
            model_name='anime',
            name='popularity_rank',
            field=models.IntegerField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='character',
            name='voice',
            field=models.CharField(blank=True, max_length=100, null=True),
        ),
    ]
