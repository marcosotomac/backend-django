# Sistema de Notificaciones - Documentación

## Resumen

Sistema completo de notificaciones en tiempo real implementado con Django Channels, WebSockets y REST API.

## Características Principales

### 📱 Tipos de Notificaciones

- **LIKE**: Cuando alguien da like a un post
- **COMMENT**: Cuando alguien comenta en un post
- **FOLLOW**: Cuando alguien sigue al usuario
- **MESSAGE**: Mensajes de chat en tiempo real
- **MENTION**: Menciones (@usuario) en posts y comentarios
- **POST_UPLOAD**: Cuando usuarios seguidos suben posts
- **CHAT_INVITE**: Invitaciones a chats grupales
- **SYSTEM**: Notificaciones del sistema

### 🎯 Funcionalidades Clave

- ✅ Notificaciones en tiempo real vía WebSockets
- ✅ API REST completa para gestión de notificaciones
- ✅ Configuración personalizable por usuario
- ✅ Generación automática vía señales de Django
- ✅ Filtrado por tipo y estado de lectura
- ✅ Paginación y estadísticas de usuario
- ✅ Soporte para push notifications (estructura)
- ✅ Limpieza automática de notificaciones antiguas
- ✅ Sistema de lotes para notificaciones masivas

## Modelos

### UserNotification

- **recipient**: Usuario que recibe la notificación
- **actor**: Usuario que genera la acción (opcional)
- **title**: Título de la notificación
- **message**: Mensaje descriptivo
- **notification_type**: Tipo de notificación
- **content_object**: Objeto relacionado (post, comentario, etc.)
- **is_read**: Estado de lectura
- **extra_data**: Datos adicionales en JSON

### NotificationSettings

Configuración personalizable por usuario:

- **likes_enabled**: Notificaciones de likes
- **comments_enabled**: Notificaciones de comentarios
- **follows_enabled**: Notificaciones de seguimientos
- **messages_enabled**: Notificaciones de mensajes
- **mentions_enabled**: Notificaciones de menciones
- **posts_enabled**: Notificaciones de posts de usuarios seguidos
- **push_notifications**: Habilitar push notifications
- **email_notifications**: Habilitar notificaciones por email
- **quiet_hours**: Configuración de horarios silenciosos

### DeviceToken

Soporte para push notifications:

- **user**: Usuario propietario
- **token**: Token del dispositivo
- **platform**: Plataforma (iOS/Android/Web)
- **is_active**: Estado del token

## API Endpoints

### Notificaciones

```
GET /api/notifications/                    # Listar notificaciones
GET /api/notifications/{id}/               # Detalle de notificación
POST /api/notifications/{id}/mark_read/    # Marcar como leída
POST /api/notifications/mark_all_read/     # Marcar todas como leídas
POST /api/notifications/mark_selected_read/ # Marcar seleccionadas como leídas
GET /api/notifications/unread_count/       # Conteo de no leídas
GET /api/notifications/stats/              # Estadísticas del usuario
GET /api/notifications/types/              # Tipos disponibles
DELETE /api/notifications/clear_all/       # Limpiar notificaciones leídas
```

### Configuración

```
GET /api/notifications/settings/           # Obtener configuración
PUT /api/notifications/settings/           # Actualizar configuración
PATCH /api/notifications/settings/         # Actualización parcial
```

### Device Tokens

```
GET /api/notifications/devices/            # Listar tokens
POST /api/notifications/devices/           # Registrar token
POST /api/notifications/devices/{id}/deactivate/ # Desactivar token
POST /api/notifications/devices/cleanup_inactive/ # Limpiar tokens
```

## WebSocket

### Conexión

```javascript
const socket = new WebSocket("ws://localhost:8000/ws/notifications/");
```

### Eventos Soportados

- **notification.new**: Nueva notificación recibida
- **notification.read**: Notificación marcada como leída
- **notification.count**: Actualización de conteo
- **get_unread**: Solicitar notificaciones no leídas
- **mark_read**: Marcar notificaciones como leídas
- **get_notifications**: Obtener página de notificaciones

### Ejemplo de Uso

```javascript
// Escuchar nuevas notificaciones
socket.onmessage = function (e) {
  const data = JSON.parse(e.data);

  if (data.type === "notification.new") {
    console.log("Nueva notificación:", data.notification);
    updateNotificationCounter(data.unread_count);
  }
};

// Marcar notificación como leída
socket.send(
  JSON.stringify({
    type: "mark_read",
    notification_ids: ["uuid-de-notificacion"],
  })
);
```

## Señales Automáticas

El sistema genera automáticamente notificaciones para:

### Interacciones Sociales

- **Likes en Posts**: Cuando alguien da like a un post
- **Comentarios**: Cuando alguien comenta en un post
- **Seguimientos**: Cuando alguien sigue al usuario

### Menciones

- **En Posts**: Detección automática de @usuario en posts
- **En Comentarios**: Detección automática de @usuario en comentarios

### Chat

- **Mensajes Directos**: Notificación de nuevos mensajes
- **Mensajes Grupales**: Notificación en chats grupales
- **Invitaciones**: Cuando se agrega a un chat grupal

### Posts

- **Nuevos Posts**: Notificación a seguidores cuando se sube un post

## Configuración

### Settings.py

```python
INSTALLED_APPS = [
    # ...
    'notifications',
    'channels',
]

# WebSocket Configuration
ASGI_APPLICATION = 'social_network_backend.asgi.application'

CHANNEL_LAYERS = {
    'default': {
        'BACKEND': 'channels.layers.InMemoryChannelLayer',
    },
}
```

### URL Configuration

```python
# urls.py
path('api/notifications/', include('notifications.urls')),

# routing.py (WebSocket)
path('ws/notifications/', NotificationConsumer.as_asgi()),
```

## Servicios

### NotificationService

Servicio central para gestión de notificaciones:

```python
from notifications.services import notification_service

# Crear notificación
notification = notification_service.create_notification(
    recipient=user,
    actor=actor_user,
    notification_type=NotificationType.LIKE,
    title="Nuevo like",
    message="Alguien le gustó tu post",
    content_object=post,
    extra_data={'post_id': str(post.id)}
)

# Obtener estadísticas
stats = notification_service.get_user_stats(user)

# Marcar como leídas
count = notification_service.mark_notifications_read(
    user=user,
    mark_all=True
)
```

## Testing

### Ejecutar Tests

```bash
python manage.py test notifications
```

### Cobertura de Tests

- ✅ Modelos y métodos
- ✅ Servicios de notificaciones
- ✅ Señales automáticas
- ✅ APIs REST
- ✅ Filtros y paginación

## Rendimiento

### Optimizaciones Implementadas

- **Índices de Base de Datos**: En campos clave para consultas rápidas
- **Select Related**: Para evitar N+1 queries
- **Paginación**: Para listas grandes de notificaciones
- **Filtrado Eficiente**: Por tipo y estado de lectura
- **Limpieza Automática**: Eliminación de notificaciones antiguas

### Límites de Rendimiento

- **Seguidores por Notificación**: Máximo 50 para evitar spam
- **WebSocket Concurrente**: Soporte para múltiples conexiones
- **Notificaciones por Página**: 20 por defecto, máximo 100

## Integración con el Sistema

### Compatibilidad

- ✅ Sistema de Posts (likes, comentarios)
- ✅ Sistema de Usuarios (seguimientos)
- ✅ Sistema de Chat (mensajes, invitaciones)
- ✅ Sistema de Menciones (posts y comentarios)

### Dependencias

- Django Channels 4.3.1
- Django REST Framework
- Redis (para producción)
- WebSocket support

## Estado del Proyecto

### ✅ Completado

- [x] Modelos de notificaciones
- [x] API REST completa
- [x] WebSocket consumer
- [x] Señales automáticas
- [x] Configuración de usuario
- [x] Sistema de device tokens
- [x] Tests comprehensivos
- [x] Documentación

### 🔄 Funcionalidades Extra (Opcionales)

- [ ] Push notifications reales (Firebase/APNs)
- [ ] Notificaciones por email
- [ ] Templates de notificaciones
- [ ] Analíticas avanzadas
- [ ] Notificaciones programadas

## Uso en Frontend

### React/JavaScript Example

```javascript
// Conexión WebSocket
const useNotifications = () => {
  const [notifications, setNotifications] = useState([]);
  const [unreadCount, setUnreadCount] = useState(0);

  useEffect(() => {
    const socket = new WebSocket(`ws://localhost:8000/ws/notifications/`);

    socket.onmessage = (e) => {
      const data = JSON.parse(e.data);

      switch (data.type) {
        case "notification.new":
          setNotifications((prev) => [data.notification, ...prev]);
          setUnreadCount(data.unread_count);
          break;
        case "notification.read":
          setUnreadCount(data.unread_count);
          break;
      }
    };

    return () => socket.close();
  }, []);

  return { notifications, unreadCount };
};
```

## Conclusión

El sistema de notificaciones está **100% funcional** y proporciona:

- Notificaciones en tiempo real
- API REST completa
- Configuración flexible
- Generación automática
- Rendimiento optimizado
- Tests comprehensivos

Es un sistema profesional listo para producción que mejora significativamente la experiencia de usuario en la red social.
