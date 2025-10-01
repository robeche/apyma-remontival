import csv
import os
from django.core.management.base import BaseCommand, CommandError
from django.contrib.auth.models import User
from django.db import transaction
from django.utils.translation import gettext as _


class Command(BaseCommand):
    help = 'Crea usuarios a partir de un archivo CSV con direcciones de correo'

    def add_arguments(self, parser):
        parser.add_argument(
            'csv_file', 
            type=str, 
            help='Ruta al archivo CSV con los datos de los usuarios'
        )
        parser.add_argument(
            '--password',
            type=str,
            default='1234',
            help='Contraseña por defecto para todos los usuarios (default: 1234)'
        )
        parser.add_argument(
            '--skip-existing',
            action='store_true',
            help='Saltar usuarios que ya existen en lugar de mostrar error'
        )

    def handle(self, *args, **options):
        csv_file = options['csv_file']
        password = options['password']
        skip_existing = options['skip_existing']

        # Verificar que el archivo existe
        if not os.path.exists(csv_file):
            raise CommandError(f'El archivo {csv_file} no existe.')

        self.stdout.write(
            self.style.SUCCESS(f'Iniciando creación de usuarios desde: {csv_file}')
        )
        self.stdout.write(f'Contraseña por defecto: {password}')

        usuarios_creados = 0
        usuarios_existentes = 0
        errores = 0

        try:
            with open(csv_file, 'r', encoding='utf-8') as file:
                # Usar coma como delimitador por defecto
                reader = csv.DictReader(file, delimiter=',')
                
                # Mostrar las columnas detectadas
                self.stdout.write(f'Columnas detectadas: {reader.fieldnames}')
                
                # Verificar que existe una columna de email
                email_column = None
                for field in reader.fieldnames:
                    if 'email' in field.lower() or 'correo' in field.lower() or 'mail' in field.lower():
                        email_column = field
                        break
                
                if not email_column:
                    # Si no encuentra columna de email, usar la primera columna
                    email_column = reader.fieldnames[0]
                    self.stdout.write(
                        self.style.WARNING(
                            f'No se encontró columna de email. Usando la primera columna: {email_column}'
                        )
                    )

                self.stdout.write(f'Usando columna para email: {email_column}')

                with transaction.atomic():
                    for row_num, row in enumerate(reader, start=2):  # start=2 porque la fila 1 son headers
                        email = row.get(email_column, '').strip()
                        
                        if not email:
                            self.stdout.write(
                                self.style.WARNING(f'Fila {row_num}: Email vacío, saltando...')
                            )
                            continue

                        # Validar formato de email básico
                        if '@' not in email or '.' not in email:
                            self.stdout.write(
                                self.style.ERROR(f'Fila {row_num}: Email inválido "{email}", saltando...')
                            )
                            errores += 1
                            continue

                        # Verificar si el usuario ya existe
                        if User.objects.filter(username=email).exists():
                            if skip_existing:
                                self.stdout.write(
                                    self.style.WARNING(f'Usuario {email} ya existe, saltando...')
                                )
                                usuarios_existentes += 1
                                continue
                            else:
                                self.stdout.write(
                                    self.style.ERROR(f'Usuario {email} ya existe!')
                                )
                                errores += 1
                                continue

                        try:
                            # Extraer nombre y apellido del email si es posible
                            nombre_usuario = email.split('@')[0]
                            partes_nombre = nombre_usuario.replace('.', ' ').replace('_', ' ').split()
                            
                            first_name = partes_nombre[0].capitalize() if partes_nombre else ''
                            last_name = ' '.join(partes_nombre[1:]).capitalize() if len(partes_nombre) > 1 else ''

                            # Crear el usuario
                            usuario = User.objects.create_user(
                                username=email,
                                email=email,
                                password=password,
                                first_name=first_name,
                                last_name=last_name,
                                is_active=True
                            )

                            self.stdout.write(
                                self.style.SUCCESS(f'✓ Usuario creado: {email} ({first_name} {last_name})')
                            )
                            usuarios_creados += 1

                        except Exception as e:
                            self.stdout.write(
                                self.style.ERROR(f'Error creando usuario {email}: {str(e)}')
                            )
                            errores += 1

        except Exception as e:
            raise CommandError(f'Error procesando el archivo CSV: {str(e)}')

        # Resumen final
        self.stdout.write('\n' + '='*50)
        self.stdout.write(self.style.SUCCESS(f'RESUMEN:'))
        self.stdout.write(f'Usuarios creados: {usuarios_creados}')
        self.stdout.write(f'Usuarios existentes (saltados): {usuarios_existentes}')
        self.stdout.write(f'Errores: {errores}')
        self.stdout.write('='*50)

        if usuarios_creados > 0:
            self.stdout.write(
                self.style.SUCCESS(f'¡Proceso completado! Se crearon {usuarios_creados} usuarios.')
            )
        else:
            self.stdout.write(
                self.style.WARNING('No se creó ningún usuario nuevo.')
            )