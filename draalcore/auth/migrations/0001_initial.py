# -*- coding: utf-8 -*-
# Generated by Django 1.9.12 on 2017-04-06 18:29
from __future__ import unicode_literals

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion
import draalcore.models.base_model
import draalcore.models.fields


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='UserAccountProfile',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('status', draalcore.models.fields.AppModelCharField(choices=[(b'Active', 'Active'), (b'Deleted', 'Deleted'), (b'Pending', 'Pending')], default=b'Active', help_text=b'Item activity status', max_length=24)),
                ('last_modified', models.DateTimeField(auto_now_add=True, help_text=b'Latest modification timestamp.')),
                ('activation_key', models.CharField(help_text=b'Account activation key', max_length=40)),
                ('modified_by', models.ForeignKey(blank=True, editable=False, help_text=b'User who modified the data.', null=True, on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
                ('user', models.OneToOneField(help_text=b'User', on_delete=django.db.models.deletion.CASCADE, related_name='account_profiles', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'db_table': 'useraccount',
            },
            bases=(draalcore.models.base_model.EventHandlingMixin, models.Model),
        ),
    ]
