# 📱 Ejemplos de Uso de la API - Social Network Backend

Este archivo contiene ejemplos prácticos de cómo usar la API de la red social con soporte para AWS S3.

## 🔑 Autenticación

### Registro de Usuario

```bash
curl -X POST http://127.0.0.1:8000/api/v1/auth/register/ \
  -H "Content-Type: application/json" \
  -d '{
    "username": "johndoe",
    "email": "john@example.com",
    "password": "securepassword123",
    "password_confirm": "securepassword123",
    "first_name": "John",
    "last_name": "Doe"
  }'
```

### Login

```bash
curl -X POST http://127.0.0.1:8000/api/v1/auth/login/ \
  -H "Content-Type: application/json" \
  -d '{
    "email": "john@example.com",
    "password": "securepassword123"
  }'
```

# Activar entorno virtual

source venv/bin/activate

# Ejecutar servidor

python manage.py runserver

````

Base URL: `http://127.0.0.1:8000`

## 1. Autenticación

### Registro de usuario
```bash
curl -X POST http://127.0.0.1:8000/api/v1/auth/register/ \
  -H "Content-Type: application/json" \
  -d '{
    "email": "usuario@example.com",
    "username": "miusuario",
    "first_name": "Mi",
    "last_name": "Usuario",
    "password": "mipassword123",
    "password_confirm": "mipassword123",
    "bio": "¡Hola! Soy nuevo en esta red social"
  }'
````

### Login

```bash
curl -X POST http://127.0.0.1:8000/api/v1/auth/login/ \
  -H "Content-Type: application/json" \
  -d '{
    "email": "usuario@example.com",
    "password": "mipassword123"
  }'
```

**Respuesta:**

```json
{
  "message": "Login exitoso",
  "user": {
    "id": "uuid-del-usuario",
    "username": "miusuario",
    "email": "usuario@example.com",
    "full_name": "Mi Usuario"
  },
  "tokens": {
    "access": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
    "refresh": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9..."
  }
}
```

## 2. Gestión de Posts

### Crear un post

```bash
curl -X POST http://127.0.0.1:8000/api/v1/posts/create/ \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "content": "¡Mi primer post en esta red social! #primerpost #hola",
    "is_public": true,
    "allow_comments": true
  }'
```

### Obtener feed personalizado

```bash
curl -X GET http://127.0.0.1:8000/api/v1/posts/feed/ \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN"
```

### Listar posts públicos

```bash
curl -X GET http://127.0.0.1:8000/api/v1/posts/ \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN"
```

### Ver posts por hashtag

```bash
curl -X GET http://127.0.0.1:8000/api/v1/posts/hashtag/primerpost/ \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN"
```

## 3. Interacciones Sociales

### Seguir a un usuario

```bash
curl -X POST http://127.0.0.1:8000/api/v1/social/follow/otrousuario/ \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN"
```

### Ver seguidores de un usuario

```bash
curl -X GET http://127.0.0.1:8000/api/v1/social/followers/miusuario/ \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN"
```

### Dar like a un post

```bash
curl -X POST http://127.0.0.1:8000/api/v1/social/like/post/POST_UUID/ \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN"
```

### Comentar un post

```bash
curl -X POST http://127.0.0.1:8000/api/v1/social/comment/post/POST_UUID/ \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "content": "¡Excelente post! Me gusta mucho."
  }'
```

### Responder a un comentario

```bash
curl -X POST http://127.0.0.1:8000/api/v1/social/comment/COMMENT_UUID/reply/ \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "content": "Estoy de acuerdo contigo!"
  }'
```

## 4. Gestión de Perfil

### Ver mi perfil

```bash
curl -X GET http://127.0.0.1:8000/api/v1/auth/profile/ \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN"
```

### Actualizar perfil

```bash
curl -X PUT http://127.0.0.1:8000/api/v1/auth/profile/update/ \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "bio": "Nueva biografía actualizada",
    "location": "Madrid, España",
    "website": "https://mi-sitio-web.com"
  }'
```

### Ver perfil de otro usuario

```bash
curl -X GET http://127.0.0.1:8000/api/v1/auth/otrousuario/ \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN"
```

## 5. Notificaciones

### Ver notificaciones

```bash
curl -X GET http://127.0.0.1:8000/api/v1/social/notifications/ \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN"
```

### Marcar notificaciones como leídas

```bash
curl -X POST http://127.0.0.1:8000/api/v1/social/notifications/mark-read/ \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "notification_ids": ["uuid1", "uuid2"]
  }'
```

## 6. Búsqueda y Descubrimiento

### Buscar usuarios

```bash
curl -X GET "http://127.0.0.1:8000/api/v1/auth/list/?search=usuario" \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN"
```

### Hashtags en tendencia

```bash
curl -X GET http://127.0.0.1:8000/api/v1/posts/hashtags/trending/ \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN"
```

## 7. JavaScript/Frontend Examples

### Registro con JavaScript

```javascript
const registerUser = async (userData) => {
  try {
    const response = await fetch(
      "http://127.0.0.1:8000/api/v1/auth/register/",
      {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify(userData),
      }
    );

    const data = await response.json();

    if (response.ok) {
      // Guardar tokens
      localStorage.setItem("access_token", data.tokens.access);
      localStorage.setItem("refresh_token", data.tokens.refresh);
      console.log("Usuario registrado:", data.user);
    } else {
      console.error("Error en registro:", data);
    }
  } catch (error) {
    console.error("Error de red:", error);
  }
};
```

### Crear post con JavaScript

```javascript
const createPost = async (content, isPublic = true) => {
  const token = localStorage.getItem("access_token");

  try {
    const response = await fetch("http://127.0.0.1:8000/api/v1/posts/create/", {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        Authorization: `Bearer ${token}`,
      },
      body: JSON.stringify({
        content: content,
        is_public: isPublic,
        allow_comments: true,
      }),
    });

    const data = await response.json();

    if (response.ok) {
      console.log("Post creado:", data.post);
    } else {
      console.error("Error al crear post:", data);
    }
  } catch (error) {
    console.error("Error de red:", error);
  }
};
```

### Obtener feed con JavaScript

```javascript
const getFeed = async (page = 1) => {
  const token = localStorage.getItem("access_token");

  try {
    const response = await fetch(
      `http://127.0.0.1:8000/api/v1/posts/feed/?page=${page}`,
      {
        headers: {
          Authorization: `Bearer ${token}`,
        },
      }
    );

    const data = await response.json();

    if (response.ok) {
      console.log("Posts del feed:", data.results);
      return data.results;
    } else {
      console.error("Error al obtener feed:", data);
    }
  } catch (error) {
    console.error("Error de red:", error);
  }
};
```

## 8. Subida de archivos (Multipart)

### Actualizar avatar

```bash
curl -X PUT http://127.0.0.1:8000/api/v1/auth/profile/update/ \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN" \
  -F "avatar=@/path/to/image.jpg" \
  -F "bio=Nueva bio con avatar"
```

### Crear post con imagen

```bash
curl -X POST http://127.0.0.1:8000/api/v1/posts/create/ \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN" \
  -F "content=Post con imagen #photo" \
  -F "image=@/path/to/photo.jpg" \
  -F "is_public=true"
```

## 9. Códigos de respuesta HTTP

- `200 OK` - Operación exitosa
- `201 Created` - Recurso creado exitosamente
- `400 Bad Request` - Datos inválidos
- `401 Unauthorized` - Token inválido o faltante
- `403 Forbidden` - Sin permisos para esta acción
- `404 Not Found` - Recurso no encontrado
- `500 Internal Server Error` - Error del servidor

## 10. Paginación

La mayoría de endpoints que devuelven listas incluyen paginación:

```json
{
  "count": 50,
  "next": "http://127.0.0.1:8000/api/v1/posts/?page=3",
  "previous": "http://127.0.0.1:8000/api/v1/posts/?page=1",
  "results": [...]
}
```

## 11. Filtros y búsqueda

### Buscar posts por contenido

```bash
curl -X GET "http://127.0.0.1:8000/api/v1/posts/?search=javascript" \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN"
```

### Ordenar posts por likes

```bash
curl -X GET "http://127.0.0.1:8000/api/v1/posts/?ordering=-likes_count" \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN"
```

## 12. Manejo de errores

### Ejemplo de error de validación

```json
{
  "content": ["Este campo no puede estar vacío."],
  "password": ["Los campos de contraseña no coinciden."]
}
```

### Ejemplo de error de autenticación

```json
{
  "detail": "Token inválido.",
  "code": "token_not_valid"
}
```

---

## Documentación Completa

Para ver todos los endpoints disponibles y probarlos interactivamente:

- **Swagger UI**: http://127.0.0.1:8000/swagger/
- **ReDoc**: http://127.0.0.1:8000/redoc/

## Panel de Administración

Accede al panel de admin de Django:

- **URL**: http://127.0.0.1:8000/admin/
- **Credenciales**: Las que creaste con `python manage.py createsuperuser`
