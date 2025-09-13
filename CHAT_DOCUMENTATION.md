# Sistema de Chat en Tiempo Real

## Descripción General

El sistema de chat implementa mensajería en tiempo real usando Django Channels y WebSockets. Permite chats directos entre usuarios y chats grupales con múltiples participantes.

## Características Principales

### 1. Tipos de Chat

- **Chat Directo**: Conversación entre dos usuarios
- **Chat Grupal**: Conversación con múltiples participantes

### 2. Mensajes

- Mensajes de texto
- Soporte para imágenes y archivos
- Respuestas a mensajes (threading)
- Edición y eliminación de mensajes
- Indicadores de lectura
- Indicadores de escritura (typing)

### 3. Estado Online

- Seguimiento de usuarios conectados
- Última vez visto
- Presencia en tiempo real

## Arquitectura

### Modelos de Datos

1. **ChatRoom**: Salas de chat

   - `name`: Nombre de la sala (opcional para chats directos)
   - `room_type`: 'direct' o 'group'
   - `participants`: Usuarios participantes
   - `created_by`: Usuario que creó la sala
   - `is_active`: Estado de la sala

2. **Message**: Mensajes

   - `room`: Sala de chat
   - `sender`: Usuario que envió el mensaje
   - `content`: Contenido del mensaje
   - `message_type`: 'text', 'image', 'file'
   - `reply_to`: Mensaje al que responde (opcional)
   - `is_deleted`: Soft delete

3. **MessageRead**: Registro de lectura

   - `user`: Usuario que leyó
   - `message`: Mensaje leído
   - `read_at`: Timestamp de lectura

4. **OnlineStatus**: Estado online
   - `user`: Usuario
   - `is_online`: Estado online
   - `last_seen`: Última conexión

### WebSocket Consumer

El `ChatConsumer` maneja las conexiones WebSocket y procesa eventos en tiempo real:

- Conexión/desconexión de usuarios
- Envío de mensajes
- Indicadores de escritura
- Marcado de mensajes como leídos
- Edición y eliminación de mensajes

## APIs REST

### Endpoints de ChatRoom

- `GET /api/v1/chat/rooms/`: Listar salas del usuario
- `POST /api/v1/chat/rooms/`: Crear nueva sala
- `POST /api/v1/chat/rooms/direct_chat/`: Crear/encontrar chat directo
- `GET /api/v1/chat/rooms/{id}/messages/`: Obtener mensajes de la sala
- `POST /api/v1/chat/rooms/{id}/join/`: Unirse a sala
- `POST /api/v1/chat/rooms/{id}/leave/`: Salir de sala
- `POST /api/v1/chat/rooms/{id}/mark_all_read/`: Marcar todos como leídos

### Endpoints de Message

- `GET /api/v1/chat/messages/`: Listar mensajes del usuario
- `POST /api/v1/chat/messages/`: Crear nuevo mensaje
- `PUT /api/v1/chat/messages/{id}/`: Editar mensaje
- `DELETE /api/v1/chat/messages/{id}/`: Eliminar mensaje
- `POST /api/v1/chat/messages/mark_read/`: Marcar mensajes como leídos
- `GET /api/v1/chat/messages/search/`: Buscar mensajes

### Endpoints de OnlineStatus

- `GET /api/v1/chat/online-status/`: Estados online de contactos
- `GET /api/v1/chat/online-status/my_status/`: Mi estado online

## Conexión WebSocket

### URL de Conexión

```
ws://localhost:8000/ws/chat/{room_id}/
```

### Autenticación

El WebSocket requiere autenticación mediante tokens JWT en las cookies o headers.

### Eventos WebSocket

#### Enviar Mensaje

```json
{
  "action": "send_message",
  "content": "Hola mundo!",
  "message_type": "text",
  "reply_to_id": "uuid-optional"
}
```

#### Indicador de Escritura

```json
{
  "action": "typing",
  "is_typing": true
}
```

#### Marcar como Leído

```json
{
  "action": "mark_read",
  "message_ids": ["uuid1", "uuid2"]
}
```

#### Editar Mensaje

```json
{
  "action": "edit_message",
  "message_id": "uuid",
  "content": "Mensaje editado"
}
```

#### Eliminar Mensaje

```json
{
  "action": "delete_message",
  "message_id": "uuid"
}
```

### Eventos Recibidos

#### Nuevo Mensaje

```json
{
    "type": "message",
    "data": {
        "id": "uuid",
        "content": "Hola mundo!",
        "sender": {...},
        "created_at": "2024-01-01T10:00:00Z"
    }
}
```

#### Usuario Escribiendo

```json
{
  "type": "typing",
  "data": {
    "user_id": "uuid",
    "username": "usuario",
    "is_typing": true
  }
}
```

#### Estado de Usuario

```json
{
  "type": "user_status",
  "data": {
    "action": "user_joined",
    "user_id": "uuid",
    "username": "usuario"
  }
}
```

## Configuración

### 1. Channels y Redis

En `settings.py`:

```python
INSTALLED_APPS = [
    'daphne',
    'channels',
    'chat',
    # ...
]

ASGI_APPLICATION = 'social_network_backend.asgi.application'

CHANNEL_LAYERS = {
    'default': {
        'BACKEND': 'channels_redis.core.RedisChannelLayer',
        'CONFIG': {
            "hosts": [('127.0.0.1', 6379)],
        },
    },
}
```

### 2. ASGI Configuration

En `asgi.py`:

```python
from channels.routing import ProtocolTypeRouter, URLRouter
from channels.auth import AuthMiddlewareStack
import chat.routing

application = ProtocolTypeRouter({
    "http": get_asgi_application(),
    "websocket": AuthMiddlewareStack(
        URLRouter(
            chat.routing.websocket_urlpatterns
        )
    ),
})
```

## Uso del Cliente

### 1. Crear Chat Directo

```javascript
// POST /api/v1/chat/rooms/direct_chat/
{
    "user_id": "uuid-del-otro-usuario"
}
```

### 2. Conectar WebSocket

```javascript
const socket = new WebSocket(`ws://localhost:8000/ws/chat/${roomId}/`);

socket.onmessage = function (e) {
  const data = JSON.parse(e.data);
  console.log("Evento recibido:", data);
};

// Enviar mensaje
socket.send(
  JSON.stringify({
    action: "send_message",
    content: "Hola!",
    message_type: "text",
  })
);
```

### 3. Obtener Historial de Mensajes

```javascript
// GET /api/v1/chat/rooms/{room_id}/messages/
```

## Seguridad

- Autenticación requerida para todas las operaciones
- Verificación de participación en salas para WebSockets
- Validación de permisos para editar/eliminar mensajes
- Sanitización de contenido de mensajes

## Consideraciones de Rendimiento

- Paginación en listado de mensajes (50 por página)
- Índices en base de datos para consultas frecuentes
- Soft delete para mensajes (preserva integridad)
- Channel layers con Redis para escalabilidad

## Testing

Ejecutar tests:

```bash
python manage.py test chat
```

Los tests cubren:

- Modelos de datos
- APIs REST
- Creación de chats y mensajes
- Autenticación y permisos
