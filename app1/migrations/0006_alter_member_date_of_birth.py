# Generated by Django 4.0.4 on 2022-05-19 07:36

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('app1', '0005_alter_member_date_of_birth'),
    ]

    operations = [
        migrations.AlterField(
            model_name='member',
            name='date_of_birth',
            field=models.DateField(default=None),
        ),
    ]
