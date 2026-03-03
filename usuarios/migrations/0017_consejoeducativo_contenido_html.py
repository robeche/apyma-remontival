# Generated manually

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('usuarios', '0016_concursodibujo_ganador'),
    ]

    operations = [
        migrations.AddField(
            model_name='consejoeducativo',
            name='contenido_html',
            field=models.TextField(blank=True, default='', help_text='Contenido HTML del consejo (tiene prioridad sobre el archivo externo)', verbose_name='Contenido HTML'),
        ),
        migrations.AddField(
            model_name='consejoeducativo',
            name='contenido_html_eu',
            field=models.TextField(blank=True, default='', help_text='Contenido HTML en euskera', verbose_name='Contenido HTML (Euskera)'),
        ),
        migrations.AlterField(
            model_name='consejoeducativo',
            name='archivo_html',
            field=models.CharField(blank=True, default='', help_text='Ruta relativa desde media/consejos/, ej: habitos-estudio.html', max_length=500, verbose_name='Ruta del archivo HTML'),
        ),
    ]
