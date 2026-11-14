import django.core.validators
from django.db import migrations, models


class Migration(migrations.Migration):
    initial = True
    dependencies = []
    operations = [
        migrations.CreateModel(
            name='Unit',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100)),
                ('type', models.CharField(choices=[('Infantry', 'Infantry'), ('Cannon', 'Cannon'), ('Cavalry', 'Cavalry'), ('Knight', 'Knight')], max_length=20)),
                ('team', models.CharField(choices=[('Blue', 'Blue'), ('Red', 'Red')], default='Blue', max_length=10)),
                ('health', models.PositiveSmallIntegerField(default=100, validators=[django.core.validators.MinValueValidator(0), django.core.validators.MaxValueValidator(100)])),
                ('attack_points', models.PositiveSmallIntegerField(default=0, validators=[django.core.validators.MinValueValidator(0), django.core.validators.MaxValueValidator(50)])),
                ('profile_image_link', models.URLField(max_length=500)),
            ],
            options={'ordering': ('name', 'id')},
        ),
    ]
