# 🧪 Tests Directory

## 📁 Estructura

```
tests/
├── __init__.py              # Package initialization
├── test_auth.py             # Authentication tests
├── chat/                    # Chat system tests
│   ├── test_chat_api.py     # Chat API comprehensive tests
│   └── test_chat_participants.py # Participants functionality tests
├── posts/                   # Posts system tests
│   └── test_posts_api.py    # Posts API tests
├── manual/                  # Manual verification tests
│   ├── test_chat_manual.py  # Manual chat testing
│   └── test_posts_manual.py # Manual posts testing
├── integration/             # Integration tests
│   └── test_postman_endpoints.py # Postman API validation
├── utils/                   # Testing utilities
│   ├── test_uploads.py      # File upload tests
│   └── check_urls.py        # URL verification utility
└── debug/                   # Debug scripts
    └── debug_chat.py        # Chat debugging tools
```

## 🚀 Comandos de Testing

### Ejecutar tests específicos:

```bash
# Tests de autenticación
python manage.py test tests.test_auth

# Tests del chat
python manage.py test tests.chat

# Tests de posts
python manage.py test tests.posts

# Todos los tests
python manage.py test tests

# Test específico del chat API
python manage.py test tests.chat.test_chat_api

# Tests manuales
python manage.py test tests.manual
```

### Scripts utilitarios:

```bash
# Debugging del chat
python tests/debug/debug_chat.py

# Verificar URLs
python tests/utils/check_urls.py

# Test de endpoints para Postman
python tests/integration/test_postman_endpoints.py
```

## 📊 Cobertura de Tests

| Módulo         | Tests | Estado        |
| -------------- | ----- | ------------- |
| Authentication | ✅    | Completo      |
| Chat API       | ✅    | 12/12 tests   |
| Posts API      | ✅    | Completo      |
| File Uploads   | ✅    | Completo      |
| Integration    | ✅    | Postman ready |

## 🎯 Tipos de Tests

- **Unit Tests**: Tests unitarios por módulo
- **Integration Tests**: Tests de integración con APIs
- **Manual Tests**: Scripts de verificación manual
- **Debug Scripts**: Herramientas de debugging
- **Utils**: Utilidades para testing
