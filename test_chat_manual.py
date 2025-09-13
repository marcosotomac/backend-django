"""
Script manual para probar endpoints del chat
"""
import requests
import json

BASE_URL = 'http://127.0.0.1:8000'

def test_chat_manually():
    print("🧪 Testing Chat Endpoints Manually")
    print("="*50)
    
    try:
        # 1. Test básico de conexión
        response = requests.get(f'{BASE_URL}/api/v1/chat/rooms/')
        print(f"GET /api/v1/chat/rooms/ - Status: {response.status_code}")
        
        if response.status_code == 401:
            print("❌ Necesita autenticación - esto es esperado")
        
        # 2. Test de registro de usuario
        register_data = {
            'username': 'chattest123',
            'email': 'chattest123@test.com',
            'password': 'testpass123',
            'password_confirm': 'testpass123',
            'first_name': 'Chat',
            'last_name': 'Test'
        }
        
        response = requests.post(f'{BASE_URL}/api/v1/auth/register/', json=register_data)
        print(f"POST /api/v1/auth/register/ - Status: {response.status_code}")
        
        if response.status_code == 201:
            # 3. Login
            login_data = {
                'username': 'chattest123',
                'password': 'testpass123'
            }
            
            response = requests.post(f'{BASE_URL}/api/v1/auth/login/', json=login_data)
            print(f"POST /api/v1/auth/login/ - Status: {response.status_code}")
            
            if response.status_code == 200:
                token = response.json()['access']
                headers = {'Authorization': f'Bearer {token}'}
                
                # 4. Test endpoints del chat con autenticación
                print("\n🔐 Testing with authentication:")
                
                # GET rooms
                response = requests.get(f'{BASE_URL}/api/v1/chat/rooms/', headers=headers)
                print(f"GET /api/v1/chat/rooms/ - Status: {response.status_code}")
                
                # POST create room
                room_data = {
                    'name': 'Test Room',
                    'room_type': 'group',
                    'description': 'Test room description'
                }
                
                response = requests.post(f'{BASE_URL}/api/v1/chat/rooms/', json=room_data, headers=headers)
                print(f"POST /api/v1/chat/rooms/ - Status: {response.status_code}")
                
                if response.status_code == 201:
                    room_id = response.json()['id']
                    print(f"Created room ID: {room_id}")
                    
                    # Test JOIN endpoint
                    response = requests.post(f'{BASE_URL}/api/v1/chat/rooms/{room_id}/join/', headers=headers)
                    print(f"POST /api/v1/chat/rooms/{room_id}/join/ - Status: {response.status_code}")
                    
                    if response.status_code != 200:
                        print(f"Response text: {response.text}")
                    
                    # Test room messages endpoint
                    response = requests.get(f'{BASE_URL}/api/v1/chat/rooms/{room_id}/messages/', headers=headers)
                    print(f"GET /api/v1/chat/rooms/{room_id}/messages/ - Status: {response.status_code}")
                    
                    print("\n✅ All main endpoints working!")
                else:
                    print(f"Failed to create room: {response.text}")
            else:
                print(f"Login failed: {response.text}")
        else:
            print(f"Register failed: {response.text}")
            
    except Exception as e:
        print(f"Error: {e}")

if __name__ == '__main__':
    test_chat_manually()