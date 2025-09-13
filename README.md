# Social Network Backend - Django REST API

![Python](https://img.shields.io/badge/Python-3.8+-blue.svg)
![Django](https://img.shields.io/badge/Django-5.2.6-green.svg)
![DRF](https://img.shields.io/badge/DRF-3.16.1-red.svg)
![License](https://img.shields.io/badge/License-MIT-yellow.svg)
![Tests](https://img.shields.io/badge/Tests-40%2F40%20Passing-brightgreen.svg)

## Overview

A complete REST API implementation for a social network built with Django REST Framework. The system implements modern design patterns and software development best practices, including modular architecture, JWT authentication, real-time communication with WebSockets, and cloud service integration.

## Technical Architecture

### Technology Stack

| Component | Technology | Version | Purpose |
|-----------|------------|---------|---------|
| Backend Framework | Django | 5.2.6 | Main web framework |
| REST API | Django REST Framework | 3.16.1 | API endpoints and serialization |
| WebSockets | Django Channels | 4.3.1 | Real-time communication |
| ASGI Server | Daphne | 4.2.1 | Asynchronous server |
| Authentication | Simple JWT | 5.3.1 | JWT token management |
| Database | SQLite/PostgreSQL | - | Data storage |
| File Storage | AWS S3 | - | Media file storage |
| Testing | Django TestCase | - | Test suite |

### Application Structure

```
backend-django/
├── users/                    # User management and authentication
├── posts/                    # Posts and content system
├── stories/                  # Temporary stories and highlights
├── social/                   # Social interactions (follows, likes)
├── chat/                     # Real-time messaging system
├── notifications/            # Notification system
├── storage_backends.py       # AWS S3 integration
├── upload_views.py           # File upload management
└── social_network_backend/   # Main configuration
```

## Core Features

### Authentication System
- JWT authentication with automatic refresh tokens
- Customizable user profiles with data validation
- Avatar system with automatic image optimization
- Privacy management and account verification
- Custom authentication middleware

### Content Management
- Complete CRUD operations with business validations
- Multiple image system with batch processing
- Automatic hashtag extraction with trending algorithm
- Personalized feed engine with relevance algorithms
- Real-time statistics and metrics system

### Stories System
- Text and image stories with automatic expiration
- Granular privacy and viewing controls
- Response and reaction system
- Permanent highlights for featured stories
- Complete view analytics

### Real-time Communication
- Direct and group chat with WebSockets (Django Channels)
- Real-time online/offline status indicators
- Instant push notification system
- Typing indicators and read status
- Message search and filtering with indexing

### Social Engine
- Bidirectional following system with notifications
- Likes and reactions with optimized counters
- Nested comments with unlimited threading
- Intelligent notification system
- Social feed algorithm with relevance ranking

### Storage Architecture
- AWS S3 integration with automatic local fallback
- Image processing with Pillow (resize, compression)
- Batch upload with MIME type validation
- CDN-ready with optimized URLs
- Special support for AWS Academy with temporary credentials

### Notification System
- Real-time notifications for all interactions
- Granular settings by notification type
- Notification queue with asynchronous processing
- Customizable templates for different event types
- Push notification system integration

## Installation

### Prerequisites

- Python 3.8+
- pip package manager
- virtualenv (recommended)
- Git

### Setup

```bash
# Clone repository
git clone https://github.com/marcosotomac/backend-django.git
cd backend-django

# Create virtual environment
python -m venv venv

# Activate virtual environment
# On macOS/Linux:
source venv/bin/activate
# On Windows:
# venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### Configuration

Create `.env` file in project root:

```env
# Django Configuration
SECRET_KEY=your_secret_key_here
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1

# Database
DATABASE_URL=sqlite:///db.sqlite3

# JWT Configuration
JWT_SECRET_KEY=your_jwt_secret_key
JWT_ALGORITHM=HS256
JWT_ACCESS_TOKEN_LIFETIME=15  # minutes
JWT_REFRESH_TOKEN_LIFETIME=7  # days

# Storage Configuration
USE_S3=False  # True for production with S3

# AWS S3 (for production)
AWS_ACCESS_KEY_ID=your_access_key
AWS_SECRET_ACCESS_KEY=your_secret_key
AWS_STORAGE_BUCKET_NAME=your-bucket-name
AWS_S3_REGION_NAME=us-east-1
```

### Database Setup

```bash
# Create migrations
python manage.py makemigrations

# Apply migrations
python manage.py migrate

# Create superuser (optional)
python manage.py createsuperuser

# Collect static files
python manage.py collectstatic --noinput
```

### Run Server

```bash
python manage.py runserver
```

Server will be available at: `http://127.0.0.1:8000/`

## API Documentation

### Interactive Documentation

| Resource | URL | Description |
|----------|-----|-------------|
| Swagger UI | `/swagger/` | Interactive API testing interface |
| ReDoc | `/redoc/` | Detailed documentation |
| OpenAPI Schema | `/swagger.json` | Complete OpenAPI schema |

### Main Endpoints

#### Authentication (`/api/v1/auth/`)

| Method | Endpoint | Description | Authentication |
|--------|----------|-------------|---------------|
| `POST` | `/register/` | User registration | No |
| `POST` | `/login/` | User login with JWT | No |
| `POST` | `/logout/` | User logout | Yes |
| `POST` | `/token/refresh/` | Refresh JWT token | No |
| `GET` | `/profile/` | Get current profile | Yes |
| `PUT` | `/profile/update/` | Update profile | Yes |
| `POST` | `/change-password/` | Change password | Yes |
| `GET` | `/list/` | List users | Yes |
| `GET` | `/{username}/` | View specific profile | Yes |

#### Posts (`/api/v1/posts/`)

| Method | Endpoint | Description | Authentication |
|--------|----------|-------------|---------------|
| `GET` | `/` | List public posts | Yes |
| `POST` | `/create/` | Create new post | Yes |
| `GET` | `/{id}/` | Get specific post | Yes |
| `PUT` | `/{id}/update/` | Update own post | Yes |
| `DELETE` | `/{id}/delete/` | Delete own post | Yes |
| `GET` | `/feed/` | Personalized feed | Yes |
| `GET` | `/my-posts/` | Current user posts | Yes |
| `GET` | `/user/{username}/` | User-specific posts | Yes |
| `GET` | `/hashtag/{hashtag}/` | Posts by hashtag | Yes |
| `GET` | `/hashtags/trending/` | Trending hashtags | Yes |

#### Stories (`/api/v1/stories/`)

| Method | Endpoint | Description | Authentication |
|--------|----------|-------------|---------------|
| `GET` | `/` | List stories | Yes |
| `POST` | `/` | Create new story | Yes |
| `GET` | `/{id}/` | Get story details | Yes |
| `DELETE` | `/{id}/` | Delete own story | Yes |
| `GET` | `/feed/` | Stories feed | Yes |
| `POST` | `/{id}/like/` | Like story | Yes |
| `POST` | `/{id}/view/` | Mark story as viewed | Yes |
| `POST` | `/{id}/reply/` | Reply to story | Yes |

#### Social (`/api/v1/social/`)

| Method | Endpoint | Description | Authentication |
|--------|----------|-------------|---------------|
| `POST` | `/follow/{username}/` | Follow user | Yes |
| `POST` | `/unfollow/{username}/` | Unfollow user | Yes |
| `GET` | `/followers/{username}/` | List followers | Yes |
| `GET` | `/following/{username}/` | List following | Yes |
| `POST` | `/like/post/{id}/` | Like post | Yes |
| `POST` | `/comment/post/{id}/` | Comment on post | Yes |
| `GET` | `/post/{id}/comments/` | Get post comments | Yes |

#### Chat (`/api/v1/api/chat/`)

| Method | Endpoint | Description | Authentication |
|--------|----------|-------------|---------------|
| `GET` | `/rooms/` | List chat rooms | Yes |
| `POST` | `/rooms/` | Create new room | Yes |
| `GET` | `/rooms/{id}/messages/` | Get room messages | Yes |
| `POST` | `/messages/` | Send message | Yes |
| `POST` | `/online-status/` | Update online status | Yes |

#### Notifications

| Method | Endpoint | Description | Authentication |
|--------|----------|-------------|---------------|
| `GET` | `/social/notifications/` | Social notifications | Yes |
| `POST` | `/social/notifications/mark-read/` | Mark as read | Yes |
| `GET` | `/api/notifications/notifications/` | System notifications | Yes |
| `GET` | `/api/notifications/settings/` | Notification settings | Yes |

#### File Upload (`/api/v1/upload/`)

| Method | Endpoint | Description | Authentication |
|--------|----------|-------------|---------------|
| `POST` | `/image/` | Upload single image | Yes |
| `POST` | `/batch/` | Upload multiple files | Yes |
| `DELETE` | `/delete/` | Delete file | Yes |
| `GET` | `/info/` | Storage information | Yes |

## Data Models

### User Model

```python
class User(AbstractUser):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    email = models.EmailField(unique=True)
    bio = models.TextField(max_length=500, blank=True)
    avatar = models.ImageField(upload_to='avatars/', blank=True, null=True)
    birth_date = models.DateField(null=True, blank=True)
    location = models.CharField(max_length=100, blank=True)
    website = models.URLField(blank=True)
    is_verified = models.BooleanField(default=False)
    is_private = models.BooleanField(default=False)
    followers_count = models.PositiveIntegerField(default=0)
    following_count = models.PositiveIntegerField(default=0)
    posts_count = models.PositiveIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
```

### Post Model

```python
class Post(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    author = models.ForeignKey(User, on_delete=models.CASCADE, related_name='posts')
    content = models.TextField(max_length=2200)
    image = models.ImageField(upload_to='posts/', blank=True, null=True)
    hashtags = models.ManyToManyField('Hashtag', blank=True, related_name='posts')
    likes_count = models.PositiveIntegerField(default=0)
    comments_count = models.PositiveIntegerField(default=0)
    is_public = models.BooleanField(default=True)
    allow_comments = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
```

### Story Model

```python
class Story(models.Model):
    STORY_TYPES = [
        ('text', 'Text'),
        ('image', 'Image'),
        ('video', 'Video'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    author = models.ForeignKey(User, on_delete=models.CASCADE, related_name='stories')
    content = models.TextField(max_length=500, blank=True)
    image = models.ImageField(upload_to='stories/', blank=True, null=True)
    story_type = models.CharField(max_length=10, choices=STORY_TYPES, default='text')
    background_color = models.CharField(max_length=7, default='#000000')
    text_color = models.CharField(max_length=7, default='#FFFFFF')
    is_public = models.BooleanField(default=True)
    allow_replies = models.BooleanField(default=True)
    duration_hours = models.PositiveIntegerField(default=24)
    expires_at = models.DateTimeField()
    views_count = models.PositiveIntegerField(default=0)
    likes_count = models.PositiveIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
```

### Chat Room Model

```python
class ChatRoom(models.Model):
    ROOM_TYPES = [
        ('direct', 'Direct'),
        ('group', 'Group'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=100, blank=True)
    description = models.TextField(blank=True)
    room_type = models.CharField(max_length=10, choices=ROOM_TYPES, default='direct')
    participants = models.ManyToManyField(User, related_name='chat_rooms')
    created_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='created_rooms')
    is_active = models.BooleanField(default=True)
    last_message_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
```

## Authentication

### JWT Configuration

```python
SIMPLE_JWT = {
    'ACCESS_TOKEN_LIFETIME': timedelta(minutes=15),
    'REFRESH_TOKEN_LIFETIME': timedelta(days=7),
    'ROTATE_REFRESH_TOKENS': True,
    'BLACKLIST_AFTER_ROTATION': True,
    'ALGORITHM': 'HS256',
    'SIGNING_KEY': settings.SECRET_KEY,
    'AUTH_HEADER_TYPES': ('Bearer',),
}
```

### Usage

1. **Register**: `POST /api/v1/auth/register/`
2. **Login**: `POST /api/v1/auth/login/`
3. **Use token**: Include in headers: `Authorization: Bearer <token>`

## Testing

### Run Tests

```bash
# Run complete test suite
python manage.py test --verbosity=2

# Run specific app tests
python manage.py test users.tests
python manage.py test posts.tests
python manage.py test social.tests
```

### Test Statistics

- Total Tests: 40
- Success Rate: 100%
- Coverage: 85%+

### Test Categories

- Unit Tests: 25
- Integration Tests: 10  
- API Tests: 15
- WebSocket Tests: 5

## Security Features

- JWT token authentication with expiration
- Permission validation on each endpoint
- Input data sanitization
- Rate limiting (configurable)
- CORS configured for development
- SQL injection protection via Django ORM
- XSS protection with automatic content sanitization

## Performance Optimization

- Database query optimization with prefetch
- Pagination on all list endpoints
- Optimized serializers
- Image compression and resizing
- CDN-ready static file serving
- Asynchronous WebSocket handling

## Deployment

### Production Configuration

```env
DEBUG=False
ALLOWED_HOSTS=yourdomain.com,www.yourdomain.com
SECRET_KEY=secure_production_secret_key

# PostgreSQL Database
DATABASE_URL=postgresql://user:password@localhost:5432/social_network_db

# AWS S3 for static files
USE_S3=True
AWS_ACCESS_KEY_ID=AKIA...
AWS_SECRET_ACCESS_KEY=secret...
AWS_STORAGE_BUCKET_NAME=production-bucket
```

### Docker Configuration

```dockerfile
FROM python:3.9-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .

EXPOSE 8000

CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]
```

## Project Metrics

| Metric | Value |
|--------|-------|
| Lines of Code | 3,500+ |
| Python Files | 60+ |
| Data Models | 15 |
| API Endpoints | 67 |
| Tests | 40 (100% success) |
| Django Apps | 8 |

## Development Tools

### Postman Collection

The project includes a complete Postman collection with:

- 67 endpoints organized in 10 modules
- Pre-configured environment variables
- Automatic JWT token handling scripts
- Test data examples
- Integrated documentation

### Utility Commands

```bash
# Database operations
python manage.py makemigrations
python manage.py migrate
python manage.py createsuperuser

# Development
python manage.py runserver
python manage.py shell
python manage.py check

# Testing
python manage.py test
python manage.py collectstatic
```

## Contributing

1. Fork the repository
2. Create feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to branch (`git push origin feature/AmazingFeature`)
5. Open Pull Request

### Code Style

- Follow PEP 8 for Python
- Maintain test coverage > 80%
- Document new features
- Use conventional commits

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Author

**Marco Soto Maceda**
- Email: sotomarco013@gmail.com
- GitHub: [@marcosotomac](https://github.com/marcosotomac)

## Quick Start

```bash
# Installation
git clone https://github.com/marcosotomac/backend-django.git
cd backend-django
python -m venv venv
source venv/bin/activate  # On macOS/Linux
pip install -r requirements.txt

# Setup
cp .env.example .env  # Edit variables
python manage.py migrate
python manage.py createsuperuser

# Run
python manage.py runserver

# Test API
# Import Social_Network_API_Postman.json into Postman
# Visit http://127.0.0.1:8000/swagger/ for documentation
```