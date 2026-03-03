# Generated manually

import usuarios.models
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('usuarios', '0017_consejoeducativo_contenido_html'),
    ]

    operations = [
        migrations.CreateModel(
            name='ConsejoImagen',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('imagen', models.ImageField(upload_to=usuarios.models.consejo_imagen_upload_to, verbose_name='Imagen')),
                ('nombre', models.CharField(blank=True, default='', max_length=200, verbose_name='Nombre descriptivo')),
                ('fecha_subida', models.DateTimeField(auto_now_add=True)),
                ('consejo', models.ForeignKey(
                    on_delete=django.db.models.deletion.CASCADE,
                    related_name='imagenes',
                    to='usuarios.consejoeducativo',
                    verbose_name='Consejo'
                )),
            ],
            options={
                'verbose_name': 'Imagen de consejo',
                'verbose_name_plural': 'Imágenes de consejo',
                'ordering': ['fecha_subida'],
            },
        ),
    ]
