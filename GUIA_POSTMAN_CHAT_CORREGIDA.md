# 🎯 GUÍA COMPLETA PARA POSTMAN - SISTEMA DE CHAT

## 🚀 PROBLEMA RESUELTO

**El problema de los participantes ya está solucionado.** Los cambios realizados:

✅ **Cambio de `participant_ids` a `participants`**: Ahora usas usernames en lugar de UUIDs  
✅ **Cambio de `user_id` a `username`**: Para chats directos también usas usernames  
✅ **Validación mejorada**: El sistema valida que los usernames existan  
✅ **Tests actualizados**: Todos los 12 tests pasan (100% éxito)

## 📋 ENDPOINTS ACTUALIZADOS PARA POSTMAN

### 1. 🔐 AUTENTICACIÓN (PRIMER PASO)

```http
POST http://127.0.0.1:8000/api/v1/auth/login/
Content-Type: application/json

{
    "username": "tu_usuario",
    "password": "tu_password"
}
```

**Respuesta:**

```json
{
  "access": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
  "refresh": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
  "user": {
    "id": "uuid-aqui",
    "username": "tu_usuario"
  }
}
```

### 2. 🏠 CREAR CHAT GRUPAL (CORREGIDO)

```http
POST http://127.0.0.1:8000/api/v1/chat/rooms/
Authorization: Bearer tu_token_aqui
Content-Type: application/json

{
    "name": "Mi Grupo de Chat",
    "description": "Un grupo para hablar de todo",
    "room_type": "group",
    "participants": ["testuser", "otrouser"]
}
```

**✅ Cambio importante:** Ahora usas `"participants": ["username1", "username2"]` en lugar de IDs.

**Respuesta esperada:**

```json
{
    "id": "uuid-de-la-sala",
    "name": "Mi Grupo de Chat",
    "room_type": "group",
    "participants": [
        {
            "id": "uuid-creador",
            "username": "tu_usuario",
            "first_name": "Tu",
            "last_name": "Nombre"
        },
        {
            "id": "uuid-participante1",
            "username": "testuser",
            "first_name": "Test",
            "last_name": "User"
        },
        {
            "id": "uuid-participante2",
            "username": "otrouser",
            "first_name": "Otro",
            "last_name": "User"
        }
    ],
    "created_by": {...},
    "participant_count": 3,
    "is_active": true
}
```

### 3. 💬 CREAR CHAT DIRECTO (CORREGIDO)

```http
POST http://127.0.0.1:8000/api/v1/chat/rooms/direct_chat/
Authorization: Bearer tu_token_aqui
Content-Type: application/json

{
    "username": "testuser"
}
```

**✅ Cambio importante:** Ahora usas `"username": "testuser"` en lugar de `"user_id": "uuid"`.

### 4. 📝 ENVIAR MENSAJE

```http
POST http://127.0.0.1:8000/api/v1/chat/messages/
Authorization: Bearer tu_token_aqui
Content-Type: application/json

{
    "room": "uuid-de-la-sala",
    "content": "¡Hola a todos en el grupo!"
}
```

### 5. 📜 VER MENSAJES DE UNA SALA

```http
GET http://127.0.0.1:8000/api/v1/chat/rooms/uuid-de-la-sala/messages/
Authorization: Bearer tu_token_aqui
```

### 6. 🏠 LISTAR MIS SALAS

```http
GET http://127.0.0.1:8000/api/v1/chat/rooms/
Authorization: Bearer tu_token_aqui
```

## 🧪 PRUEBA PASO A PASO EN POSTMAN

### Paso 1: Crear usuarios de prueba

1. Registra algunos usuarios desde tu app o admin panel
2. O usa usuarios existentes

### Paso 2: Login y obtener token

```http
POST http://127.0.0.1:8000/api/v1/auth/login/
{
    "username": "usuario1",
    "password": "password123"
}
```

### Paso 3: Crear chat grupal (formato correcto)

```http
POST http://127.0.0.1:8000/api/v1/chat/rooms/
Authorization: Bearer [tu_token]
{
    "name": "Grupo de Trabajo",
    "room_type": "group",
    "participants": ["usuario2", "usuario3"]
}
```

### Paso 4: Verificar participantes

El JSON de respuesta debe mostrar 3 participantes:

- Tu usuario (creador)
- usuario2
- usuario3

## ⚠️ ERRORES COMUNES RESUELTOS

❌ **Error anterior:** `"participants": [2, 3, 4]` (IDs numéricos)  
✅ **Formato correcto:** `"participants": ["usuario2", "usuario3"]` (usernames)

❌ **Error anterior:** `"user_id": "uuid-here"` (para chats directos)  
✅ **Formato correcto:** `"username": "testuser"` (para chats directos)

## 🎯 SERVIDOR ACTIVO

El servidor está corriendo en: **http://127.0.0.1:8000**

Todos los tests pasan (12/12) ✅ y el sistema está completamente funcional.

## 📞 SOPORTE

Si necesitas ayuda adicional:

1. Verifica que uses usernames, no UUIDs
2. Asegúrate que los usuarios existan en la base de datos
3. Incluye siempre el token de autorización
4. Usa Content-Type: application/json
