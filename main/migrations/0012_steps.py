from django.db import migrations, models
import django.db.models.deletion


def create_etapes(apps, schema_editor):
    Etape = apps.get_model('main', 'Etape')
    noms = [
        'Définition',
        'Recherche',
        'Devis',
        'Négociation',
        'Remise des clés',
        'Estimation',
        'Diagnostics',
        'Valorisation',
        'Commercialisation',
        'Post-vente',
    ]
    for ordre, nom in enumerate(noms, start=1):
        Etape.objects.create(nom=nom, ordre=ordre)

class Migration(migrations.Migration):

    dependencies = [
        ('main', '0011_projets'),
    ]

    operations = [
        migrations.AddField(
            model_name='professionnel',
            name='localisation',
            field=models.CharField(blank=True, max_length=100),
        ),
        migrations.AddField(
            model_name='projets',
            name='professionnel',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='projets', to='main.professionnel'),
        ),
        migrations.CreateModel(
            name='Etape',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('nom', models.CharField(max_length=100)),
                ('ordre', models.PositiveIntegerField()),
            ],
            options={'ordering': ['ordre']},
        ),
        migrations.CreateModel(
            name='ProjetEtape',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('terminee', models.BooleanField(default=False)),
                ('etape', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='main.etape')),
                ('projet', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='etapes', to='main.projets')),
            ],
            options={'unique_together': {('projet', 'etape')}},
        ),
        migrations.RunPython(create_etapes),
    ]
