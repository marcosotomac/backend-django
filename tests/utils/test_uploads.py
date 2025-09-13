"""
Script para probar las funcionalidades de upload de imágenes
"""
import requests
import json
import os

# Configuración
BASE_URL = 'http://127.0.0.1:8000'
API_URL = f'{BASE_URL}/api/v1'


class SocialNetworkAPITester:
    def __init__(self):
        self.session = requests.Session()
        self.access_token = None
        self.user_data = None

    def register_user(self, username, email, password, first_name, last_name):
        """Registrar un nuevo usuario"""
        url = f"{API_URL}/auth/register/"
        data = {
            'username': username,
            'email': email,
            'password': password,
            'password_confirm': password,
            'first_name': first_name,
            'last_name': last_name
        }

        response = self.session.post(url, json=data)
        print(f"Registro: {response.status_code}")
        if response.status_code == 201:
            result = response.json()
            self.access_token = result.get('access')
            self.user_data = result.get('user')
            self.session.headers.update({
                'Authorization': f'Bearer {self.access_token}'
            })
            print(f"Usuario registrado: {self.user_data['username']}")
            return True
        else:
            print(f"Error en registro: {response.json()}")
            return False

    def login_user(self, email, password):
        """Hacer login"""
        url = f"{API_URL}/auth/login/"
        data = {
            'email': email,
            'password': password
        }

        response = self.session.post(url, json=data)
        print(f"Login: {response.status_code}")
        if response.status_code == 200:
            result = response.json()
            self.access_token = result.get('access')
            self.user_data = result.get('user')
            self.session.headers.update({
                'Authorization': f'Bearer {self.access_token}'
            })
            print(f"Login exitoso: {self.user_data['username']}")
            return True
        else:
            print(f"Error en login: {response.json()}")
            return False

    def test_storage_info(self):
        """Probar endpoint de información de almacenamiento"""
        url = f"{API_URL}/upload/info/"
        response = self.session.get(url)
        print(f"\nStorage Info: {response.status_code}")
        if response.status_code == 200:
            info = response.json()
            print(f"Tipo de almacenamiento: {info['storage_type']}")
            print(f"Formatos permitidos: {info['allowed_formats']}")
            print(f"Tamaño máximo: {info['max_file_size']}")
            print(f"Compresión habilitada: {info['compression_enabled']}")
            return info
        return None

    def create_test_image(self, filename="test_image.jpg", size=(300, 300)):
        """Crear una imagen de prueba"""
        try:
            from PIL import Image
            import tempfile

            # Crear imagen de prueba
            img = Image.new('RGB', size, color='red')
            temp_file = tempfile.NamedTemporaryFile(
                suffix='.jpg', delete=False)
            img.save(temp_file.name, 'JPEG')
            temp_file.close()

            return temp_file.name
        except ImportError:
            print("PIL no está disponible. No se puede crear imagen de prueba.")
            return None

    def test_single_image_upload(self, image_path=None):
        """Probar upload de imagen individual"""
        if not image_path:
            image_path = self.create_test_image()

        if not image_path or not os.path.exists(image_path):
            print("No se pudo crear o encontrar imagen de prueba")
            return None

        url = f"{API_URL}/upload/image/"

        with open(image_path, 'rb') as img_file:
            files = {'image': img_file}
            response = self.session.post(url, files=files)

        print(f"\nUpload imagen individual: {response.status_code}")
        if response.status_code == 201:
            result = response.json()
            print(f"Imagen subida exitosamente:")
            print(f"  - Ruta: {result['file_path']}")
            print(f"  - URL: {result['file_url']}")
            print(f"  - Tamaño: {result['file_size']} bytes")

            # Limpiar archivo temporal si lo creamos
            if image_path.startswith('/tmp') or 'temp' in image_path:
                os.unlink(image_path)

            return result
        else:
            print(f"Error en upload: {response.json()}")
            return None

    def test_batch_image_upload(self, num_images=3):
        """Probar upload de múltiples imágenes"""
        url = f"{API_URL}/upload/batch/"

        # Crear múltiples imágenes de prueba
        image_paths = []
        for i in range(num_images):
            path = self.create_test_image(
                f"test_image_{i}.jpg", (200 + i * 50, 200 + i * 50))
            if path:
                image_paths.append(path)

        if not image_paths:
            print("No se pudieron crear imágenes de prueba")
            return None

        try:
            files = []
            for i, path in enumerate(image_paths):
                files.append(('images', open(path, 'rb')))

            response = self.session.post(url, files=files)

            # Cerrar archivos
            for _, file_obj in files:
                file_obj.close()

            print(
                f"\nUpload batch ({num_images} imágenes): {response.status_code}")
            if response.status_code == 201:
                result = response.json()
                print(f"Resultado del batch upload:")
                print(f"  - Archivos subidos: {result['total_uploaded']}")
                print(f"  - Errores: {result['total_errors']}")

                for uploaded in result['uploaded_files']:
                    print(
                        f"  - Imagen {uploaded['index']}: {uploaded['file_path']}")

                # Limpiar archivos temporales
                for path in image_paths:
                    if os.path.exists(path):
                        os.unlink(path)

                return result
            else:
                print(f"Error en batch upload: {response.json()}")
                return None

        except Exception as e:
            print(f"Error en batch upload: {e}")
            # Limpiar archivos temporales en caso de error
            for path in image_paths:
                if os.path.exists(path):
                    os.unlink(path)
            return None

    def test_delete_image(self, file_path):
        """Probar eliminación de imagen"""
        url = f"{API_URL}/upload/delete/"
        data = {'file_path': file_path}

        response = self.session.delete(url, json=data)
        print(f"\nEliminar imagen: {response.status_code}")
        if response.status_code == 200:
            result = response.json()
            print(f"Imagen eliminada: {result['message']}")
            return True
        else:
            print(f"Error al eliminar: {response.json()}")
            return False

    def create_post_with_image(self, content, image_path=None):
        """Crear un post con imagen"""
        if not image_path:
            image_path = self.create_test_image("post_image.jpg")

        if not image_path:
            print("No se pudo crear imagen para el post")
            return None

        url = f"{API_URL}/posts/"

        with open(image_path, 'rb') as img_file:
            files = {'image': img_file}
            data = {'content': content}
            response = self.session.post(url, data=data, files=files)

        print(f"\nCrear post con imagen: {response.status_code}")
        if response.status_code == 201:
            result = response.json()
            print(f"Post creado:")
            print(f"  - ID: {result['id']}")
            print(f"  - Contenido: {result['content']}")
            print(f"  - Imagen: {result['image_url']}")

            # Limpiar archivo temporal
            if image_path.startswith('/tmp') or 'temp' in image_path:
                os.unlink(image_path)

            return result
        else:
            print(f"Error al crear post: {response.json()}")
            return None

    def run_all_tests(self):
        """Ejecutar todas las pruebas"""
        print("=" * 50)
        print("INICIANDO PRUEBAS DE UPLOAD DE IMÁGENES")
        print("=" * 50)

        # 1. Probar información de almacenamiento
        storage_info = self.test_storage_info()

        # 2. Registrar o hacer login
        if not self.login_user('test@example.com', 'testpass123'):
            if not self.register_user('testuser', 'test@example.com', 'testpass123', 'Test', 'User'):
                print("No se pudo autenticar. Terminando pruebas.")
                return

        # 3. Probar upload individual
        upload_result = self.test_single_image_upload()

        # 4. Probar batch upload
        batch_result = self.test_batch_image_upload(3)

        # 5. Crear post con imagen
        post_result = self.create_post_with_image(
            "¡Post de prueba con imagen! #test #upload")

        # 6. Probar eliminación de imagen (si se subió alguna)
        if upload_result and upload_result.get('file_path'):
            self.test_delete_image(upload_result['file_path'])

        print("\n" + "=" * 50)
        print("PRUEBAS COMPLETADAS")
        print("=" * 50)


def main():
    """Función principal para ejecutar las pruebas"""
    print("🧪 Tester de API de Red Social")
    print("Asegúrate de que el servidor esté ejecutándose en http://127.0.0.1:8000")

    try:
        tester = SocialNetworkAPITester()
        tester.run_all_tests()
    except requests.exceptions.ConnectionError:
        print("❌ Error: No se pudo conectar al servidor.")
        print("Asegúrate de ejecutar: python manage.py runserver")
    except Exception as e:
        print(f"❌ Error inesperado: {e}")


if __name__ == "__main__":
    main()
