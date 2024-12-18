# Generated by Django 2.2.13 on 2021-06-08 14:24

import dashboard.mixins.draftables
from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('dashboard', '0035_auto_20210607_2246'),
    ]

    operations = [
        migrations.CreateModel(
            name='ArticleTranslationCredit',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('credit_title', models.CharField(max_length=50)),
                ('credit_title_order', models.IntegerField(default=0)),
                ('credit_user_name', models.CharField(max_length=100)),
                ('is_user', models.BooleanField(default=False)),
                ('created_on', models.DateTimeField(auto_now_add=True)),
                ('updated_on', models.DateTimeField(auto_now=True)),
                ('article', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='translation_credits', to='dashboard.ArticleTranslation')),
                ('user', models.ForeignKey(blank=True, default='', null=True, on_delete=django.db.models.deletion.CASCADE, related_name='article_translation_credits', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'db_table': 'article_translation_credit',
                'ordering': ['credit_title_order'],
            },
        ),
        migrations.AlterField(
            model_name='answertranslationcredit',
            name='answer',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='translation_credits', to='dashboard.AnswerTranslation'),
        ),
    ]
