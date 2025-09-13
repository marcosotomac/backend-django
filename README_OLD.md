# 🌐 Red Social Backend - Django REST API

Una API REST completa para una red social desarrollada con Django y Django REST Framework, con soporte para almacenamiento en AWS S3.

## � Características

### � Autenticación y Usuarios

- ✅ Registro y login con JWT
- ✅ Perfil de usuario personalizable
- ✅ Avatar con upload optimizado
- ✅ Gestión de privacidad (cuentas privadas)
- ✅ Verificación de cuentas

### 📝 Posts y Contenido

- ✅ Crear, editar y eliminar posts
- ✅ Soporte para múltiples imágenes por post
- ✅ Extracción automática de hashtags
- ✅ Configuración de privacidad por post
- ✅ Compresión automática de imágenes

### 👥 Funciones Sociales

- ✅ Seguir/dejar de seguir usuarios
- ✅ Likes en posts
- ✅ Comentarios anidados
- ✅ Sistema de notificaciones
- ✅ Feed personalizado

### � Gestión de Archivos

- ✅ Almacenamiento local para desarrollo
- ✅ Integración con AWS S3 para producción
- ✅ Compresión automática de imágenes
- ✅ Upload en lotes (batch upload)
- ✅ Validación de archivos

### 📚 Documentación

- ✅ Swagger UI interactiva
- ✅ ReDoc documentation
- ✅ API endpoints completamente documentados

## � Instalación

### Prerrequisitos

- Python 3.8+
- pip
- virtualenv (recomendado)

### 1. Clonar y configurar el proyecto

```bash
# Clonar el repositorio
git clone <repository-url>
cd backend-django

# Crear entorno virtual
python -m venv venv

# Activar entorno virtual
# En macOS/Linux:
source venv/bin/activate
# En Windows:
# venv\\Scripts\\activate

# Instalar dependencias
pip install -r requirements.txt
```

### 2. Configurar variables de entorno

Crear archivo `.env` en la raíz del proyecto:

```env
# Configuración de Django
SECRET_KEY=tu_secret_key_aqui
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1

# Base de datos (SQLite por defecto)
DATABASE_URL=sqlite:///db.sqlite3

# Configuración de almacenamiento
USE_S3=False

# Para producción con S3 (cambiar USE_S3=True)
AWS_ACCESS_KEY_ID=tu_access_key
AWS_SECRET_ACCESS_KEY=tu_secret_key
AWS_STORAGE_BUCKET_NAME=tu-bucket-name
AWS_S3_REGION_NAME=us-east-1
AWS_S3_CUSTOM_DOMAIN=tu-bucket-name.s3.amazonaws.com

# JWT Configuration
JWT_SECRET_KEY=tu_jwt_secret_key
```

### 3. Configurar base de datos

```bash
# Hacer migraciones
python manage.py makemigrations

# Aplicar migraciones
python manage.py migrate

# Crear superusuario (opcional)
python manage.py createsuperuser
```

### 4. Iniciar servidor

```bash
python manage.py runserver
```

El servidor estará disponible en: http://127.0.0.1:8000/

## 📖 Documentación de la API

### Swagger UI

- **URL**: http://127.0.0.1:8000/swagger/
- Interfaz interactiva para probar todos los endpoints

### ReDoc

- **URL**: http://127.0.0.1:8000/redoc/
- Documentación más detallada y legible

### JSON Schema

- **URL**: http://127.0.0.1:8000/swagger.json
- Schema OpenAPI en formato JSON

## 🔗 Endpoints Principales

### Autenticación

```
POST /api/v1/auth/register/          - Registro de usuario
POST /api/v1/auth/login/             - Login
POST /api/v1/auth/refresh/           - Renovar token
POST /api/v1/auth/logout/            - Logout
GET  /api/v1/auth/profile/           - Perfil del usuario
PUT  /api/v1/auth/profile/           - Actualizar perfil
```

### Posts

```
GET    /api/v1/posts/                - Listar posts
POST   /api/v1/posts/                - Crear post
GET    /api/v1/posts/{id}/           - Detalle de post
PUT    /api/v1/posts/{id}/           - Actualizar post
DELETE /api/v1/posts/{id}/           - Eliminar post
GET    /api/v1/posts/feed/           - Feed personalizado
```

### Social

```
POST   /api/v1/social/follow/{user_id}/     - Seguir usuario
DELETE /api/v1/social/follow/{user_id}/     - Dejar de seguir
POST   /api/v1/social/like/{post_id}/       - Like a post
DELETE /api/v1/social/like/{post_id}/       - Unlike post
GET    /api/v1/social/followers/            - Mis seguidores
GET    /api/v1/social/following/            - Usuarios que sigo
```

### Upload de Archivos

```
POST   /api/v1/upload/image/        - Subir imagen individual
POST   /api/v1/upload/batch/        - Subir múltiples imágenes
DELETE /api/v1/upload/delete/       - Eliminar imagen
GET    /api/v1/upload/info/         - Info del almacenamiento
```

## 🗂️ Estructura del Proyecto

```
backend-django/
├── users/                  # App de usuarios
│   ├── models.py          # Modelo User personalizado
│   ├── serializers.py     # Serializers para API
│   ├── views.py           # Vistas de autenticación
│   └── urls.py            # URLs de auth
├── posts/                 # App de posts
│   ├── models.py          # Modelos Post, PostImage, Hashtag
│   ├── serializers.py     # Serializers para posts
│   ├── views.py           # CRUD de posts
│   └── urls.py            # URLs de posts
├── social/                # App de interacciones sociales
│   ├── models.py          # Follow, Like, Comment, Notification
│   ├── serializers.py     # Serializers sociales
│   ├── views.py           # Vistas de interacciones
│   └── urls.py            # URLs sociales
├── social_network_backend/ # Configuración principal
│   ├── settings.py        # Configuración Django
│   ├── urls.py            # URLs principales
│   └── wsgi.py            # WSGI config
├── storage_backends.py    # Backends de almacenamiento S3
├── upload_views.py        # Vistas para upload de archivos
├── utils.py               # Utilidades y helpers
├── requirements.txt       # Dependencias
├── AWS_S3_SETUP.md       # Guía de configuración S3
└── README.md             # Este archivo
```

## ☁️ Configuración de AWS S3

### Para Cuentas AWS Academy 🎓

Este proyecto incluye soporte especial para **AWS Academy** con sus limitaciones:

#### 🚀 Configuración rápida para Academy:

1. **Copia el archivo de configuración**:

```bash
cp .env.academy.example .env
```

2. **Usa el helper de Academy**:

```bash
python aws_academy_helper.py status    # Ver estado actual
python aws_academy_helper.py update    # Actualizar credenciales
python aws_academy_helper.py switch    # Cambiar S3/Local
python aws_academy_helper.py test      # Probar conexión
```

#### ⚠️ Limitaciones de AWS Academy:

- **Credenciales temporales**: Expiran cada 3-4 horas
- **Session tokens requeridos**: Además de access key y secret
- **Regiones limitadas**: Generalmente solo us-east-1
- **Labs temporales**: Se reinician periódicamente

#### 📖 Flujo recomendado:

**Para desarrollo diario** (recomendado):

```bash
python aws_academy_helper.py switch  # Cambiar a local
```

**Para demos/pruebas con S3**:

1. Inicia AWS Academy Lab
2. `python aws_academy_helper.py update` # Actualizar credenciales
3. Crear bucket en S3 (nombre: `red-social-academy-tu-id`)
4. `python aws_academy_helper.py test` # Verificar conexión

### Para Cuentas AWS Estándar

Para usar S3 en producción, consulta la guía detallada: [AWS_S3_SETUP.md](AWS_S3_SETUP.md)

# Database settings

DATABASE_URL=sqlite:///db.sqlite3

# JWT settings

JWT_SECRET_KEY=your-jwt-secret-key
JWT_ALGORITHM=HS256
JWT_ACCESS_TOKEN_LIFETIME=15
JWT_REFRESH_TOKEN_LIFETIME=7

````

### 3. Configurar base de datos

```bash
# Crear migraciones
python manage.py makemigrations

# Aplicar migraciones
python manage.py migrate

# Crear superusuario
python manage.py createsuperuser

# Recolectar archivos estáticos
python manage.py collectstatic
````

### 4. Ejecutar servidor

```bash
python manage.py runserver
```

El servidor estará disponible en: `http://127.0.0.1:8000/`

## 📚 Documentación API

### Endpoints disponibles

#### 🔐 Autenticación (`/api/v1/auth/`)

- `POST /register/` - Registro de usuario
- `POST /login/` - Inicio de sesión
- `POST /logout/` - Cerrar sesión
- `POST /token/refresh/` - Renovar token
- `GET /profile/` - Obtener perfil actual
- `PUT /profile/update/` - Actualizar perfil
- `POST /change-password/` - Cambiar contraseña
- `GET /list/` - Listar usuarios
- `GET /<username>/` - Ver perfil específico

#### 📝 Posts (`/api/v1/posts/`)

- `GET /` - Listar posts públicos
- `POST /create/` - Crear post
- `GET /<id>/` - Ver post específico
- `PUT /<id>/update/` - Actualizar post
- `DELETE /<id>/delete/` - Eliminar post
- `GET /feed/` - Feed personalizado
- `GET /my-posts/` - Mis posts
- `GET /user/<username>/` - Posts de usuario
- `GET /hashtag/<name>/` - Posts por hashtag
- `GET /hashtags/trending/` - Hashtags en tendencia

#### 🤝 Social (`/api/v1/social/`)

- `POST /follow/<username>/` - Seguir usuario
- `POST /unfollow/<username>/` - Dejar de seguir
- `GET /followers/<username>/` - Lista de seguidores
- `GET /following/<username>/` - Lista de seguidos
- `GET /check-follow/<username>/` - Verificar seguimiento
- `POST /like/post/<id>/` - Like a post
- `POST /unlike/post/<id>/` - Quitar like a post
- `POST /like/comment/<id>/` - Like a comentario
- `POST /unlike/comment/<id>/` - Quitar like a comentario
- `POST /comment/post/<id>/` - Comentar post
- `POST /comment/<id>/reply/` - Responder comentario
- `GET /comment/<id>/` - Ver comentario
- `PUT /comment/<id>/update/` - Actualizar comentario
- `DELETE /comment/<id>/delete/` - Eliminar comentario
- `GET /post/<id>/comments/` - Comentarios de post
- `GET /notifications/` - Lista de notificaciones
- `POST /notifications/mark-read/` - Marcar como leídas

### 📖 Swagger Documentation

Accede a la documentación interactiva:

- **Swagger UI**: `http://127.0.0.1:8000/swagger/`
- **ReDoc**: `http://127.0.0.1:8000/redoc/`

### 🔑 Autenticación

La API utiliza JWT (JSON Web Tokens). Para autenticarte:

1. **Registro**: `POST /api/v1/auth/register/`
2. **Login**: `POST /api/v1/auth/login/`
3. **Usar token**: Incluir en headers: `Authorization: Bearer <token>`

## 💾 Modelos de Datos

### Usuario (User)

```python
{
    "id": "uuid",
    "username": "string",
    "email": "email",
    "first_name": "string",
    "last_name": "string",
    "bio": "text",
    "avatar": "image",
    "birth_date": "date",
    "location": "string",
    "website": "url",
    "is_verified": "boolean",
    "is_private": "boolean",
    "followers_count": "integer",
    "following_count": "integer",
    "posts_count": "integer"
}
```

### Post

```python
{
    "id": "uuid",
    "author": "User",
    "content": "text",
    "image": "image",
    "images": ["PostImage"],
    "hashtags": ["Hashtag"],
    "likes_count": "integer",
    "comments_count": "integer",
    "is_public": "boolean",
    "allow_comments": "boolean",
    "created_at": "datetime"
}
```

### Comentario (Comment)

```python
{
    "id": "uuid",
    "post": "Post",
    "author": "User",
    "content": "text",
    "parent": "Comment",
    "likes_count": "integer",
    "replies_count": "integer",
    "created_at": "datetime"
}
```

## 🎯 Funcionalidades Principales

### 1. **Feed Inteligente**

- Posts de usuarios seguidos
- Ordenamiento cronológico
- Paginación automática
- Filtros por hashtags

### 2. **Sistema de Notificaciones**

- Likes en posts y comentarios
- Nuevos seguidores
- Comentarios en posts
- Menciones (futuro)

### 3. **Gestión de Imágenes**

- Subida de avatares
- Múltiples imágenes por post
- Redimensionamiento automático
- Validación de formatos

### 4. **Búsqueda y Descubrimiento**

- Búsqueda de usuarios
- Hashtags populares
- Usuarios sugeridos
- Posts trending

## 🛡️ Seguridad

- **Tokens JWT** con expiración
- **Validación de permisos** en cada endpoint
- **Sanitización de datos** de entrada
- **Rate limiting** (configurable)
- **CORS** configurado para desarrollo

## 🚦 Estado del Proyecto

✅ **Completado:**

- Modelos de datos
- Autenticación JWT
- CRUD de posts
- Sistema de seguimiento
- Likes y comentarios
- Notificaciones
- Documentación Swagger
- Panel de administración

🔄 **En desarrollo:**

- Tests unitarios
- Rate limiting
- Optimización de consultas
- Cache Redis

📋 **Roadmap:**

- Mensajería directa
- Stories temporales
- Sistema de reportes
- Recomendaciones ML
- WebSockets para real-time

## 🤝 Contribución

1. Fork el proyecto
2. Crear rama de feature (`git checkout -b feature/AmazingFeature`)
3. Commit cambios (`git commit -m 'Add some AmazingFeature'`)
4. Push a la rama (`git push origin feature/AmazingFeature`)
5. Abrir Pull Request

## 📝 Licencia

Este proyecto está bajo la Licencia MIT - ver el archivo [LICENSE](LICENSE) para detalles.

## 👨‍💻 Autor

**Marco Soto**

- Email: sotomarco013@gmail.com
- GitHub: [@sotomarco]

---

## 🔧 Comandos Útiles

```bash
# Crear nueva migración
python manage.py makemigrations

# Aplicar migraciones
python manage.py migrate

# Crear superusuario
python manage.py createsuperuser

# Ejecutar servidor
python manage.py runserver

# Shell de Django
python manage.py shell

# Verificar proyecto
python manage.py check

# Recolectar estáticos
python manage.py collectstatic
```

## 📊 Métricas del Proyecto

- **Líneas de código**: ~2000+
- **Endpoints**: 25+
- **Modelos**: 8
- **Aplicaciones**: 3
- **Tiempo de desarrollo**: 1 día
- **Cobertura de tests**: En desarrollo

---

_¡Gracias por usar Social Network Backend!_ 🎉
