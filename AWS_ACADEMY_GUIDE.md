# 🎓 Guía Rápida AWS Academy - Red Social Backend

## 📋 Lista de verificación para demostración

### ✅ Preparación inicial

- [ ] Proyecto Django funcionando localmente
- [ ] Archivo `.env` configurado (copiar de `.env.academy.example`)
- [ ] AWS Academy Lab iniciado y funcionando

### ✅ Configurar S3 en Academy

1. **Iniciar Lab**:

   ```
   AWS Academy → Learner Lab → Start Lab → Esperar indicador verde
   ```

2. **Crear bucket S3**:

   ```
   AWS Console → S3 → Create bucket
   Nombre: red-social-academy-tu-id
   Región: us-east-1
   Block Public Access: Desmarcar "Block public access to buckets and objects granted through new public bucket or access point policies"
   ```

3. **Configurar CORS** (en el bucket):

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

4. **Obtener credenciales**:

   ```
   AWS Academy → AWS Details → Show (AWS CLI section)
   ```

5. **Actualizar backend**:
   ```bash
   python aws_academy_helper.py update
   # Ingresar credenciales cuando se soliciten
   ```

### ✅ Pruebas de funcionalidad

1. **Verificar conexión**:

   ```bash
   python aws_academy_helper.py test
   ```

2. **Iniciar servidor**:

   ```bash
   python manage.py runserver
   ```

3. **Probar endpoints**:
   - Swagger UI: http://127.0.0.1:8000/swagger/
   - Storage info: http://127.0.0.1:8000/api/v1/upload/info/

## 🎬 Script de demostración

### Demo 1: Registro y upload de avatar

```bash
# 1. Registrar usuario
curl -X POST http://127.0.0.1:8000/api/v1/auth/register/ \
  -H "Content-Type: application/json" \
  -d '{
    "username": "demo_user",
    "email": "demo@academy.com",
    "password": "DemoPass123!",
    "password_confirm": "DemoPass123!",
    "first_name": "Demo",
    "last_name": "User"
  }'

# 2. Login y obtener token
TOKEN=$(curl -s -X POST http://127.0.0.1:8000/api/v1/auth/login/ \
  -H "Content-Type: application/json" \
  -d '{"email": "demo@academy.com", "password": "DemoPass123!"}' | \
  python -c "import sys, json; print(json.load(sys.stdin)['access'])")

# 3. Subir imagen
curl -X POST http://127.0.0.1:8000/api/v1/upload/image/ \
  -H "Authorization: Bearer $TOKEN" \
  -F "image=@ruta/a/imagen.jpg"
```

### Demo 2: Crear post con imagen

```bash
# Crear post con imagen directo a S3
curl -X POST http://127.0.0.1:8000/api/v1/posts/ \
  -H "Authorization: Bearer $TOKEN" \
  -F "content=¡Demo de red social con AWS Academy! #aws #django #s3" \
  -F "image=@ruta/a/imagen.jpg"
```

## 🚨 Solución de problemas comunes

### Error: "TokenRefreshRequired"

```bash
# Las credenciales expiraron
python aws_academy_helper.py update
# Ingresar nuevas credenciales de Academy
```

### Error: "NoSuchBucket"

```bash
# El bucket no existe
# 1. Ir a AWS Console → S3
# 2. Crear bucket con el nombre correcto
# 3. Configurar CORS
```

### Error: "Access Denied"

```bash
# Permisos del bucket incorrectos
# 1. S3 Console → tu bucket → Permissions
# 2. Block public access → Edit
# 3. Desmarcar la opción de bucket policies
```

### Cambiar a almacenamiento local rápidamente

```bash
python aws_academy_helper.py switch
# Cambia entre S3 y almacenamiento local
```

## 📊 Verificación de que S3 funciona

### 1. Verificar en consola AWS

- Ve a S3 Console
- Tu bucket debería mostrar archivos en `media/` y/o `temp-uploads/`

### 2. Verificar URLs de imágenes

- Las URLs deben contener: `tu-bucket.s3.amazonaws.com`
- No deben contener: `127.0.0.1:8000/media/`

### 3. Verificar desde navegador

- Abrir URL de imagen directamente
- Debe cargar desde S3, no desde servidor local

## 🎯 Puntos clave para presentación

1. **Escalabilidad**: "S3 puede manejar millones de imágenes"
2. **Disponibilidad**: "99.999999999% (11 9's) de durabilidad"
3. **CDN Ready**: "Fácil integración con CloudFront"
4. **Costos**: "Solo pagas por lo que usas"
5. **Backup automático**: "Los datos están replicados automáticamente"

## 🔄 Flujo de desarrollo recomendado

### Durante desarrollo:

```env
USE_S3=False  # Almacenamiento local
```

### Para demo/presentación:

```env
USE_S3=True   # AWS S3
```

### Script rápido para alternar:

```bash
# Cambiar a local
python aws_academy_helper.py switch

# Cambiar a S3 (requiere credenciales válidas)
python aws_academy_helper.py switch
```

## 📸 Capturas recomendadas

1. **Swagger UI** mostrando endpoints de upload
2. **AWS S3 Console** con archivos subidos
3. **URLs de imágenes** apuntando a S3
4. **Postman/curl** funcionando con autenticación
5. **Logs del servidor** mostrando "✅ Credenciales S3 válidas"

## ⏰ Timeline para demo (5 minutos)

1. **Minuto 1**: Mostrar proyecto funcionando localmente
2. **Minuto 2**: Cambiar a S3 con `aws_academy_helper.py`
3. **Minuto 3**: Subir imagen via API/Swagger
4. **Minuto 4**: Mostrar imagen en S3 Console
5. **Minuto 5**: Crear post con imagen, mostrar URL final

¡Listo para impresionar! 🚀
