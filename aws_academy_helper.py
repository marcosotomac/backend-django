#!/usr/bin/env python3
"""
Utilidades para AWS Academy - Red Social Backend
Script para facilitar el manejo de credenciales de AWS Academy
"""
import os
import sys
import re
import subprocess
from pathlib import Path


class AWSAcademyHelper:
    def __init__(self):
        self.env_file = Path('.env')
        self.backup_file = Path('.env.backup')

    def show_status(self):
        """Mostrar el estado actual de la configuración"""
        print("🔍 Estado actual de AWS Academy")
        print("=" * 50)

        if not self.env_file.exists():
            print("❌ Archivo .env no encontrado")
            print("💡 Copia .env.academy.example como .env")
            return

        with open(self.env_file, 'r') as f:
            content = f.read()

        use_s3 = self._get_env_var(content, 'USE_S3')
        access_key = self._get_env_var(content, 'AWS_ACCESS_KEY_ID')
        bucket_name = self._get_env_var(content, 'AWS_STORAGE_BUCKET_NAME')

        print(f"📊 USE_S3: {use_s3}")
        print(f"🗂️  Bucket: {bucket_name}")

        if access_key:
            if access_key.startswith('ASIA'):
                print(f"🔑 Credenciales: AWS Academy (inician con ASIA)")
                print(f"⏰ Tipo: Temporales (expiran en 3-4 horas)")
            else:
                print(f"🔑 Credenciales: Estándar AWS")
        else:
            print(f"🔑 Credenciales: No configuradas")

        print("\n🛠️  Comandos disponibles:")
        print("  python aws_academy_helper.py status     - Ver estado")
        print("  python aws_academy_helper.py switch     - Cambiar entre S3/Local")
        print("  python aws_academy_helper.py update     - Actualizar credenciales")
        print("  python aws_academy_helper.py test       - Probar conexión S3")

    def _get_env_var(self, content, var_name):
        """Extraer valor de variable de entorno del contenido"""
        pattern = rf'^{var_name}=(.*)$'
        match = re.search(pattern, content, re.MULTILINE)
        if match:
            value = match.group(1).strip()
            # Remover comentarios
            if '#' in value:
                value = value.split('#')[0].strip()
            return value
        return None

    def _update_env_var(self, content, var_name, new_value):
        """Actualizar variable en el contenido"""
        pattern = rf'^({var_name}=).*$'
        replacement = f'{var_name}={new_value}'

        if re.search(pattern, content, re.MULTILINE):
            # Variable existe, reemplazar
            return re.sub(pattern, replacement, content, flags=re.MULTILINE)
        else:
            # Variable no existe, agregar
            return content + f'\n{replacement}\n'

    def switch_storage(self):
        """Cambiar entre almacenamiento S3 y local"""
        if not self.env_file.exists():
            print("❌ Archivo .env no encontrado")
            return

        with open(self.env_file, 'r') as f:
            content = f.read()

        current_use_s3 = self._get_env_var(content, 'USE_S3')

        if current_use_s3 == 'True':
            # Cambiar a local
            content = self._update_env_var(content, 'USE_S3', 'False')
            print("📁 Cambiado a almacenamiento LOCAL")
            print("💡 Reinicia el servidor: python manage.py runserver")
        else:
            # Cambiar a S3
            access_key = self._get_env_var(content, 'AWS_ACCESS_KEY_ID')
            if not access_key or access_key.startswith('#'):
                print("⚠️  No hay credenciales AWS configuradas")
                print("🔧 Ejecuta: python aws_academy_helper.py update")
                return

            content = self._update_env_var(content, 'USE_S3', 'True')
            print("☁️  Cambiado a almacenamiento S3")
            print("💡 Reinicia el servidor: python manage.py runserver")

        # Backup y guardar
        if self.env_file.exists():
            self.env_file.rename(self.backup_file)

        with open(self.env_file, 'w') as f:
            f.write(content)

        print("✅ Configuración actualizada")

    def update_credentials(self):
        """Actualizar credenciales de AWS Academy"""
        print("🔄 Actualización de credenciales AWS Academy")
        print("=" * 50)
        print("1. Ve a AWS Academy Learner Lab")
        print("2. Haz clic en 'AWS Details'")
        print("3. Haz clic en 'Show' en la sección AWS CLI")
        print("4. Copia las credenciales que aparecen")
        print()

        # Solicitar credenciales
        print("Ingresa las nuevas credenciales:")
        access_key = input(
            "AWS_ACCESS_KEY_ID (debe iniciar con ASIA): ").strip()

        if not access_key.startswith('ASIA'):
            print("⚠️  Advertencia: Las credenciales de Academy deben iniciar con 'ASIA'")
            continue_anyway = input(
                "¿Continuar de todas formas? (y/N): ").strip().lower()
            if continue_anyway != 'y':
                print("❌ Operación cancelada")
                return

        secret_key = input("AWS_SECRET_ACCESS_KEY: ").strip()
        session_token = input("AWS_SESSION_TOKEN: ").strip()
        bucket_name = input(
            "Nombre del bucket (ej: red-social-academy-tu-id): ").strip()

        if not all([access_key, secret_key, session_token, bucket_name]):
            print("❌ Faltan datos requeridos")
            return

        # Actualizar archivo .env
        if not self.env_file.exists():
            print("📝 Creando archivo .env desde plantilla")
            if Path('.env.academy.example').exists():
                with open('.env.academy.example', 'r') as f:
                    content = f.read()
            else:
                content = ""
        else:
            with open(self.env_file, 'r') as f:
                content = f.read()

        # Actualizar variables
        content = self._update_env_var(
            content, 'AWS_ACCESS_KEY_ID', access_key)
        content = self._update_env_var(
            content, 'AWS_SECRET_ACCESS_KEY', secret_key)
        content = self._update_env_var(
            content, 'AWS_SESSION_TOKEN', session_token)
        content = self._update_env_var(
            content, 'AWS_STORAGE_BUCKET_NAME', bucket_name)
        content = self._update_env_var(
            content, 'AWS_S3_CUSTOM_DOMAIN', f'{bucket_name}.s3.amazonaws.com')
        content = self._update_env_var(content, 'USE_S3', 'True')

        # Backup y guardar
        if self.env_file.exists():
            self.env_file.rename(self.backup_file)

        with open(self.env_file, 'w') as f:
            f.write(content)

        print("✅ Credenciales actualizadas")
        print("🚀 Reinicia el servidor: python manage.py runserver")
        print("⏰ Recordatorio: Las credenciales expiran en 3-4 horas")

    def test_s3_connection(self):
        """Probar la conexión con S3"""
        print("🧪 Probando conexión con S3...")

        if not self.env_file.exists():
            print("❌ Archivo .env no encontrado")
            return

        # Cargar variables de entorno
        with open(self.env_file, 'r') as f:
            content = f.read()

        use_s3 = self._get_env_var(content, 'USE_S3')
        if use_s3 != 'True':
            print("📁 S3 no está habilitado (USE_S3=False)")
            return

        access_key = self._get_env_var(content, 'AWS_ACCESS_KEY_ID')
        secret_key = self._get_env_var(content, 'AWS_SECRET_ACCESS_KEY')
        session_token = self._get_env_var(content, 'AWS_SESSION_TOKEN')
        bucket_name = self._get_env_var(content, 'AWS_STORAGE_BUCKET_NAME')

        if not all([access_key, secret_key, session_token, bucket_name]):
            print("❌ Faltan credenciales AWS")
            return

        try:
            import boto3
            from botocore.exceptions import ClientError, NoCredentialsError

            # Crear cliente S3
            s3_client = boto3.client(
                's3',
                aws_access_key_id=access_key,
                aws_secret_access_key=secret_key,
                aws_session_token=session_token,
                region_name='us-east-1'
            )

            # Probar acceso al bucket
            s3_client.head_bucket(Bucket=bucket_name)
            print("✅ Conexión S3 exitosa")

            # Listar objetos (primeros 5)
            response = s3_client.list_objects_v2(Bucket=bucket_name, MaxKeys=5)
            if 'Contents' in response:
                print(
                    f"📂 Archivos en bucket ({len(response['Contents'])} mostrados):")
                for obj in response['Contents']:
                    print(f"  - {obj['Key']} ({obj['Size']} bytes)")
            else:
                print("📂 Bucket vacío")

        except ClientError as e:
            error_code = e.response['Error']['Code']
            if error_code == 'NoSuchBucket':
                print(f"❌ Bucket '{bucket_name}' no existe")
                print("💡 Créalo en la consola de AWS Academy")
            elif error_code == 'InvalidAccessKeyId':
                print("❌ Access Key inválida")
                print("🔄 Actualiza credenciales: python aws_academy_helper.py update")
            elif error_code == 'TokenRefreshRequired':
                print("❌ Session token expirado")
                print("🔄 Actualiza credenciales: python aws_academy_helper.py update")
            else:
                print(f"❌ Error S3: {error_code} - {e}")
        except NoCredentialsError:
            print("❌ Credenciales no encontradas")
        except ImportError:
            print("❌ boto3 no está instalado")
            print("💡 Instala con: pip install boto3")
        except Exception as e:
            print(f"❌ Error: {e}")


def main():
    helper = AWSAcademyHelper()

    if len(sys.argv) < 2:
        helper.show_status()
        return

    command = sys.argv[1].lower()

    if command == 'status':
        helper.show_status()
    elif command == 'switch':
        helper.switch_storage()
    elif command == 'update':
        helper.update_credentials()
    elif command == 'test':
        helper.test_s3_connection()
    else:
        print("❌ Comando no reconocido")
        print("📖 Comandos disponibles: status, switch, update, test")


if __name__ == "__main__":
    main()
