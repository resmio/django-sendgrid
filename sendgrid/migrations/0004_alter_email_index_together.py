# Generated by Django 3.2.11 on 2022-01-26 07:53

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('contenttypes', '0002_remove_content_type_name'),
        ('sendgrid', '0003_auto_20190722_1007'),
    ]

    operations = [
        migrations.AlterIndexTogether(
            name='email',
            index_together={('content_type', 'object_id')},
        ),
    ]
