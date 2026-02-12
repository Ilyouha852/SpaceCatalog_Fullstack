from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('observatory', '0003_alter_researcher_picture'),
    ]

    operations = [
        migrations.DeleteModel(
            name='ObservationRecord',
        ),
    ]
