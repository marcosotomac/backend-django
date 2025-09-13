# Configuración de AWS S3 para el Backend de Red Social (AWS Academy)

## ⚠️ Consideraciones para AWS Academy

Las cuentas de AWS Academy tienen **limitaciones específicas** que debes considerar:

- **Tiempo de sesión limitado**: Las credenciales expiran cada 3-4 horas
- **Regiones restringidas**: Solo ciertas regiones están disponibles (generalmente us-east-1)
- **Servicios limitados**: No todos los servicios de AWS están habilitados
- **Sin facturación**: Los costos son cubiertos por el programa educativo
- **Acceso temporal**: La cuenta se reinicia periódicamente

## Configuración de Amazon S3 para AWS Academy

### 1. Acceder a AWS Academy

1. Ingresa a tu **AWS Academy Learner Lab**
2. Haz clic en **"Start Lab"** para iniciar la sesión
3. Espera a que el indicador se ponga **verde** (Lab running)
4. Haz clic en **"AWS"** para acceder a la consola

### 2. Crear un bucket de S3

1. En la consola AWS, busca **"S3"** en el buscador
2. Haz clic en **"Create bucket"**
3. Configura el bucket:
   - **Bucket name**: `red-social-academy-{tu-student-id}` (debe ser único globalmente)
   - **Region**: **us-east-1** (por defecto en Academy)
   - **Block Public Access**: **Desmarcar SOLO "Block public access to buckets and objects granted through new public bucket or access point policies"**
   - **Versioning**: Desactivado (para evitar costos adicionales)
   - **Encryption**: Usar configuración por defecto

### 3. Configurar CORS

En tu bucket de S3, ve a la pestaña **"Permissions"** > **"Cross-origin resource sharing (CORS)"** y configura:

```json
[
  {
    "AllowedHeaders": ["*"],
    "AllowedMethods": ["GET", "PUT", "POST", "DELETE", "HEAD"],
    "AllowedOrigins": ["*"],
    "ExposeHeaders": ["ETag"]
  }
]
```

### 3. Obtener credenciales de AWS Academy

**⚠️ IMPORTANTE**: En AWS Academy, las credenciales se obtienen de forma diferente:

1. En tu **Learner Lab**, haz clic en **"AWS Details"**
2. Haz clic en **"Show"** junto a "AWS CLI"
3. Copia las credenciales que aparecen:

```bash
[default]
aws_access_key_id = ASIA...
aws_secret_access_key = ...
aws_session_token = ...
region = us-east-1
```

**🔄 Renovación automática**: Las credenciales de Academy **expiran cada 3-4 horas**. Para renovarlas:

1. Detén el servidor Django: `Ctrl + C`
2. Actualiza las variables en `.env` con las nuevas credenciales
3. Reinicia el servidor: `python manage.py runserver`

### 4. Configurar variables de entorno para Academy

Actualiza tu archivo `.env` con las credenciales de AWS Academy:

```env
# Configuración de AWS S3 (Academy)
USE_S3=True
AWS_ACCESS_KEY_ID=ASIA...  # De AWS Academy Details
AWS_SECRET_ACCESS_KEY=...  # De AWS Academy Details
AWS_SESSION_TOKEN=...      # ¡IMPORTANTE! Academy requiere session token
AWS_STORAGE_BUCKET_NAME=red-social-academy-tu-student-id
AWS_S3_REGION_NAME=us-east-1
AWS_S3_CUSTOM_DOMAIN=red-social-academy-tu-student-id.s3.amazonaws.com

# Para desarrollo local cuando Academy no esté disponible
USE_S3=False
```

### 5. Script de renovación automática (Opcional)

Crea un script para renovar credenciales fácilmente:

```bash
#!/bin/bash
# renew_aws_credentials.sh

echo "🔄 Renovando credenciales de AWS Academy..."
echo "Ve a AWS Academy > AWS Details > Show AWS CLI"
echo "Luego copia y pega las nuevas credenciales:"
echo ""
echo "AWS_ACCESS_KEY_ID="
read -r access_key
echo "AWS_SECRET_ACCESS_KEY="
read -r secret_key
echo "AWS_SESSION_TOKEN="
read -r session_token

# Actualizar .env
sed -i '' "s/AWS_ACCESS_KEY_ID=.*/AWS_ACCESS_KEY_ID=$access_key/" .env
sed -i '' "s/AWS_SECRET_ACCESS_KEY=.*/AWS_SECRET_ACCESS_KEY=$secret_key/" .env
sed -i '' "s/AWS_SESSION_TOKEN=.*/AWS_SESSION_TOKEN=$session_token/" .env

echo "✅ Credenciales actualizadas en .env"
echo "🚀 Reinicia el servidor: python manage.py runserver"
```

## Configuración Especial para AWS Academy

### Manejo de expiración de credenciales

AWS Academy **reinicia las credenciales cada vez que inicias el lab**. Para manejar esto:

1. **Configuración híbrida recomendada**:

```env
# Durante desarrollo - usar local
USE_S3=False

# Solo para pruebas/demos - usar Academy S3
USE_S3=True
```

2. **Detección automática de credenciales expiradas**:

```python
# En settings.py, agregar después de la configuración S3:
import logging

logger = logging.getLogger(__name__)

def test_s3_credentials():
    """Verificar si las credenciales S3 están funcionando"""
    if USE_S3:
        try:
            import boto3
            from botocore.exceptions import ClientError

            s3 = boto3.client('s3',
                aws_access_key_id=AWS_ACCESS_KEY_ID,
                aws_secret_access_key=AWS_SECRET_ACCESS_KEY,
                aws_session_token=AWS_SESSION_TOKEN,
                region_name=AWS_S3_REGION_NAME
            )
            s3.head_bucket(Bucket=AWS_STORAGE_BUCKET_NAME)
            logger.info("✅ Credenciales S3 válidas")
            return True
        except ClientError as e:
            logger.warning(f"❌ Credenciales S3 inválidas: {e}")
            logger.warning("🔄 Cambiando a almacenamiento local")
            return False
    return False

# Verificar credenciales al inicio
if USE_S3 and not test_s3_credentials():
    USE_S3 = False
    DEFAULT_FILE_STORAGE = 'django.core.files.storage.FileSystemStorage'
    STATICFILES_STORAGE = 'django.contrib.staticfiles.storage.StaticFilesStorage'
```

### Limitaciones y consideraciones

#### 🕐 **Tiempo de sesión**

- Las credenciales expiran cada **3-4 horas**
- El lab se **detiene automáticamente** después del tiempo límite
- **Reinicia el lab** para obtener nuevas credenciales

#### 🌍 **Regiones disponibles**

- Generalmente solo **us-east-1** (N. Virginia)
- Algunas veces **us-west-2** (Oregon)
- Verifica en tu consola Academy qué regiones están disponibles

#### 💾 **Persistencia de datos**

- Los buckets **pueden eliminarse** cuando el lab se reinicia
- **Respalda** las imágenes importantes localmente
- Considera usar almacenamiento local para desarrollo

#### 🔒 **Permisos limitados**

- No se pueden crear usuarios IAM
- Permisos predefinidos del rol Academy
- Configuraciones de seguridad limitadas

### Flujo de trabajo recomendado

#### Para desarrollo diario:

```env
USE_S3=False  # Usar almacenamiento local
```

#### Para pruebas/demos:

1. Iniciar AWS Academy Lab
2. Copiar credenciales nuevas
3. Actualizar `.env`:

```env
USE_S3=True
AWS_ACCESS_KEY_ID=ASIA...
AWS_SECRET_ACCESS_KEY=...
AWS_SESSION_TOKEN=...
```

4. Reiniciar servidor Django
5. Probar funcionalidad S3

#### Para presentaciones:

- Tener **capturas de pantalla** de S3 funcionando
- **Video demo** del upload funcionando
- **Backup local** de todas las imágenes

## Comandos útiles

### Migrar archivos existentes a S3

```bash
# Instalar AWS CLI
pip install awscli

# Configurar AWS CLI
aws configure

# Subir archivos existentes
aws s3 sync media/ s3://tu-red-social-media/media/ --acl public-read
```

### Backup de S3

```bash
# Descargar todos los archivos
aws s3 sync s3://tu-red-social-media/ ./backup/
```

## Costos estimados

Para una red social pequeña a mediana:

- **Almacenamiento**: ~$0.023 por GB/mes
- **Transferencia**: Primeros 1GB gratis/mes, luego ~$0.09 por GB
- **Requests**: GET ~$0.0004 por 1,000 requests, PUT ~$0.005 por 1,000 requests

### Ejemplo de costos mensuales:

- 10GB de imágenes: ~$0.23
- 100,000 visualizaciones: ~$0.04
- 10,000 uploads: ~$0.05
- **Total estimado**: ~$0.32/mes

## Optimizaciones

### 1. CDN (CloudFront)

Para mejor rendimiento global, configura CloudFront:

```env
AWS_S3_CUSTOM_DOMAIN=tu-dominio.cloudfront.net
```

### 2. Compresión de imágenes

El sistema incluye compresión automática de imágenes. Puedes ajustar la calidad en `utils.py`:

```python
IMAGE_QUALITY = 85  # Reduce para menor tamaño de archivo
IMAGE_MAX_WIDTH = 1920  # Tamaño máximo
IMAGE_MAX_HEIGHT = 1080
```

### 3. Políticas de lifecyle

Configura políticas para eliminar archivos antiguos automáticamente:

1. Ve a tu bucket S3
2. Management tab → Lifecycle rules
3. Configura reglas para eliminar archivos después de X días

## Seguridad

### Variables de entorno en producción

**NUNCA** pongas las credenciales directamente en el código. Usa:

- **Heroku**: Variables de entorno en el dashboard
- **AWS EC2**: IAM Roles en lugar de access keys
- **Docker**: Variables de entorno o secrets
- **Kubernetes**: Secrets

### Ejemplo para EC2:

1. Crea un IAM Role con las políticas necesarias
2. Asigna el role a tu instancia EC2
3. No necesitas `AWS_ACCESS_KEY_ID` ni `AWS_SECRET_ACCESS_KEY`

## Troubleshooting

### Error: "NoCredentialsError"

- Verifica que las variables de entorno estén configuradas
- En producción, verifica que el IAM role esté asignado

### Error: "Access Denied"

- Verifica los permisos del bucket
- Verifica las políticas IAM
- Verifica la configuración CORS

### Error: "Bucket does not exist"

- Verifica el nombre del bucket en `AWS_STORAGE_BUCKET_NAME`
- Verifica que el bucket esté en la región correcta

### Imágenes no se cargan

- Verifica la configuración de Block Public Access
- Verifica que los objetos tengan ACL public-read
- Verifica el CORS del bucket
