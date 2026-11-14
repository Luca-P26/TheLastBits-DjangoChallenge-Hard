import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [('units', '0001_initial')]

    operations = [
        migrations.CreateModel(
            name='Fight',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('status', models.CharField(choices=[('complete', 'Complete'), ('stalemate', 'Stalemate')], default='complete', max_length=12)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('unit_one', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='fights_as_first', to='units.unit')),
                ('unit_two', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='fights_as_second', to='units.unit')),
                ('winner', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, related_name='fights_won', to='units.unit')),
            ],
            options={'ordering': ('-created_at', '-id')},
        ),
        migrations.CreateModel(
            name='FightTurn',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('turn_number', models.PositiveIntegerField()),
                ('attack_points', models.PositiveSmallIntegerField(help_text='Random attack value rolled for this turn.')),
                ('attacker_health', models.PositiveSmallIntegerField()),
                ('defender_health', models.PositiveSmallIntegerField()),
                ('attacker', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='attacks_made', to='units.unit')),
                ('defender', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='attacks_received', to='units.unit')),
                ('fight', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='turns', to='units.fight')),
            ],
            options={'ordering': ('turn_number',)},
        ),
        migrations.AddConstraint(
            model_name='fightturn',
            constraint=models.UniqueConstraint(fields=('fight', 'turn_number'), name='unique_fight_turn_number'),
        ),
    ]
