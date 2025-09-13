#!/usr/bin/env python3
"""
Script de prueba para verificar endpoints de Posts
"""
import requests
import json

BASE_URL = 'http://127.0.0.1:8000'

def test_posts_endpoints():
    """Test básico de endpoints de posts"""
    
    print("🧪 Testeando endpoints de Posts...")
    
    # 1. Registrar usuario
    print("\n1. Registrando usuario...")
    register_data = {
        "username": "testuser_api",
        "email": "testapi@example.com",
        "password": "testpass123",
        "password_confirm": "testpass123",
        "first_name": "Test",
        "last_name": "User"
    }
    
    response = requests.post(f"{BASE_URL}/api/v1/auth/register/", json=register_data)
    print(f"Status: {response.status_code}")
    if response.status_code != 201:
        print(f"Error en registro: {response.text}")
        return
    
    # 2. Login
    print("\n2. Haciendo login...")
    login_data = {
        "username": "testuser_api",
        "password": "testpass123"
    }
    
    response = requests.post(f"{BASE_URL}/api/v1/auth/login/", json=login_data)
    print(f"Status: {response.status_code}")
    if response.status_code != 200:
        print(f"Error en login: {response.text}")
        return
    
    token_data = response.json()
    access_token = token_data['access']
    headers = {'Authorization': f'Bearer {access_token}'}
    
    # 3. Crear post
    print("\n3. Creando post...")
    post_data = {
        "content": "Este es un post de prueba con #testing #django #api",
        "is_public": True,
        "allow_comments": True
    }
    
    response = requests.post(f"{BASE_URL}/api/v1/posts/create/", json=post_data, headers=headers)
    print(f"Status: {response.status_code}")
    if response.status_code == 201:
        post_result = response.json()
        post_id = post_result['post']['id']
        print(f"Post creado con ID: {post_id}")
    else:
        print(f"Error creando post: {response.text}")
        return
    
    # 4. Listar posts
    print("\n4. Listando posts...")
    response = requests.get(f"{BASE_URL}/api/v1/posts/", headers=headers)
    print(f"Status: {response.status_code}")
    if response.status_code == 200:
        posts = response.json()
        print(f"Posts encontrados: {posts['count']}")
    else:
        print(f"Error listando posts: {response.text}")
    
    # 5. Ver detalle del post
    print("\n5. Viendo detalle del post...")
    response = requests.get(f"{BASE_URL}/api/v1/posts/{post_id}/", headers=headers)
    print(f"Status: {response.status_code}")
    if response.status_code == 200:
        post_detail = response.json()
        print(f"Post content: {post_detail['content']}")
        print(f"Hashtags: {len(post_detail['hashtags'])} encontrados")
    else:
        print(f"Error obteniendo detalle: {response.text}")
    
    # 6. Ver mis posts
    print("\n6. Viendo mis posts...")
    response = requests.get(f"{BASE_URL}/api/v1/posts/my-posts/", headers=headers)
    print(f"Status: {response.status_code}")
    if response.status_code == 200:
        my_posts = response.json()
        print(f"Mis posts: {my_posts['count']}")
    else:
        print(f"Error obteniendo mis posts: {response.text}")
    
    # 7. Ver hashtags trending
    print("\n7. Viendo hashtags trending...")
    response = requests.get(f"{BASE_URL}/api/v1/posts/hashtags/trending/", headers=headers)
    print(f"Status: {response.status_code}")
    if response.status_code == 200:
        trending = response.json()
        print(f"Hashtags trending: {len(trending['results'])}")
    else:
        print(f"Error obteniendo trending: {response.text}")
    
    # 8. Ver posts por hashtag
    print("\n8. Viendo posts por hashtag 'testing'...")
    response = requests.get(f"{BASE_URL}/api/v1/posts/hashtag/testing/", headers=headers)
    print(f"Status: {response.status_code}")
    if response.status_code == 200:
        hashtag_posts = response.json()
        print(f"Posts con #testing: {len(hashtag_posts['results'])}")
    else:
        print(f"Error obteniendo posts por hashtag: {response.text}")
    
    # 9. Ver estadísticas del post
    print("\n9. Viendo estadísticas del post...")
    response = requests.get(f"{BASE_URL}/api/v1/posts/{post_id}/stats/", headers=headers)
    print(f"Status: {response.status_code}")
    if response.status_code == 200:
        stats = response.json()
        print(f"Likes: {stats['likes_count']}, Comments: {stats['comments_count']}")
    else:
        print(f"Error obteniendo stats: {response.text}")
    
    # 10. Actualizar post
    print("\n10. Actualizando post...")
    update_data = {
        "content": "Post actualizado con #updated #testing",
        "is_public": True,
        "allow_comments": True
    }
    
    response = requests.put(f"{BASE_URL}/api/v1/posts/{post_id}/update/", json=update_data, headers=headers)
    print(f"Status: {response.status_code}")
    if response.status_code == 200:
        print("Post actualizado exitosamente")
    else:
        print(f"Error actualizando post: {response.text}")
    
    # 11. Feed
    print("\n11. Viendo feed...")
    response = requests.get(f"{BASE_URL}/api/v1/posts/feed/", headers=headers)
    print(f"Status: {response.status_code}")
    if response.status_code == 200:
        feed = response.json()
        print(f"Posts en feed: {len(feed['results'])}")
    else:
        print(f"Error obteniendo feed: {response.text}")
    
    print("\n✅ Pruebas completadas!")

if __name__ == "__main__":
    try:
        test_posts_endpoints()
    except requests.exceptions.ConnectionError:
        print("❌ Error: No se puede conectar al servidor. Asegúrate de que esté ejecutándose en http://127.0.0.1:8000")
    except Exception as e:
        print(f"❌ Error inesperado: {e}")