# Generated by Django 5.0.6 on 2024-08-18 23:41

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('RoadQuestApp', '0008_routeitem_stop1_routeitem_stop2_routeitem_stop3'),
    ]

    operations = [
        migrations.AlterField(
            model_name='routeitem',
            name='stop1',
            field=models.CharField(blank=True, max_length=200),
        ),
        migrations.AlterField(
            model_name='routeitem',
            name='stop2',
            field=models.CharField(blank=True, max_length=200),
        ),
        migrations.AlterField(
            model_name='routeitem',
            name='stop3',
            field=models.CharField(blank=True, max_length=200),
        ),
    ]
