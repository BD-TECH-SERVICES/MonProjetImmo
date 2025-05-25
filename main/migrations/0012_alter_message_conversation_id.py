from django.db import migrations, models

class Migration(migrations.Migration):
    dependencies = [
        ('main', '0011_projets'),
    ]

    operations = [
        migrations.AlterField(
            model_name='message',
            name='conversation_id',
            field=models.CharField(max_length=255),
        ),
    ]

