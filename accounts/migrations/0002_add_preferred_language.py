from django.db import migrations, models

class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0001_initial'),  # depends on your initial migration
    ]

    operations = [
        migrations.AddField(
            model_name='userprofile',
            name='preferred_language',
            field=models.CharField(
                max_length=10,
                choices=[('c', 'C'), ('cpp', 'C++'), ('python', 'Python')],
                default='c'
            ),
        ),
    ]
