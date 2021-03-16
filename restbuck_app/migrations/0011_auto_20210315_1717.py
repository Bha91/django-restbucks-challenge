# Generated by Django 3.1.7 on 2021-03-15 13:47

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('restbuck_app', '0010_auto_20210315_1506'),
    ]

    operations = [
        migrations.AddField(
            model_name='order',
            name='is_deleted',
            field=models.BooleanField(default=False),
        ),
        migrations.AlterField(
            model_name='order',
            name='previous_state',
            field=models.SmallIntegerField(choices=[(0, 'waiting'), (1, 'preparation'), (2, 'ready'), (3, 'delivered')], default=0, help_text='previous state of order'),
        ),
        migrations.AlterField(
            model_name='order',
            name='state',
            field=models.SmallIntegerField(choices=[(0, 'waiting'), (1, 'preparation'), (2, 'ready'), (3, 'delivered')], default=0, help_text='state of order'),
        ),
    ]