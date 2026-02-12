from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('observatory', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='researcher',
            name='picture',
            field=models.ImageField(upload_to='researchers', null=True, blank=True),
        ),
    ]
