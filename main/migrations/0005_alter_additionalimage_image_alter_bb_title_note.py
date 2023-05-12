# Generated by Django 4.1.4 on 2023-05-12 11:46

import django.core.validators
from django.db import migrations, models
import django.db.models.deletion
import main.utilities


class Migration(migrations.Migration):

    dependencies = [
        ('contenttypes', '0002_remove_content_type_name'),
        ('main', '0004_comment'),
    ]

    operations = [
        migrations.AlterField(
            model_name='additionalimage',
            name='image',
            field=models.ImageField(help_text='Подгружать надо аккуратно', upload_to=main.utilities.get_timestamp_path, verbose_name='Изображение'),
        ),
        migrations.AlterField(
            model_name='bb',
            name='title',
            field=models.CharField(help_text='Товар должен быть не более 40 символов', max_length=40, validators=[django.core.validators.RegexValidator('')], verbose_name='Товар'),
        ),
        migrations.CreateModel(
            name='Note',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('content', models.TextField()),
                ('object_id', models.PositiveIntegerField()),
                ('contenttype', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='contenttypes.contenttype')),
            ],
        ),
    ]
