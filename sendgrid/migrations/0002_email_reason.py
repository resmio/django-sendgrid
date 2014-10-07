# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('sendgrid', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='email',
            name='reason',
            field=models.CharField(default=b'', max_length=1024, verbose_name='reason'),
            preserve_default=True,
        ),
    ]
