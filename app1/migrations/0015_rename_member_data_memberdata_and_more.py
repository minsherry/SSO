# Generated by Django 4.0.4 on 2022-05-26 03:50

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('app1', '0014_member_data'),
    ]

    operations = [
        migrations.RenameModel(
            old_name='Member_data',
            new_name='MemberData',
        ),
        migrations.RemoveField(
            model_name='member',
            name='cannot_use',
        ),
    ]
