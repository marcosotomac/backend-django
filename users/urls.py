from django.urls import path
from rest_framework_simplejwt.views import TokenRefreshView
from . import views

app_name = 'users'

urlpatterns = [
    # Autenticación
    path('register/', views.UserRegistrationView.as_view(), name='register'),
    path('login/', views.UserLoginView.as_view(), name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),

    # Perfil de usuario
    path('profile/', views.UserProfileView.as_view(), name='profile'),
    path('profile/update/', views.UserUpdateView.as_view(), name='profile_update'),
    path('change-password/', views.ChangePasswordView.as_view(),
         name='change_password'),

    # Usuarios
    path('list/', views.UserListView.as_view(), name='user_list'),
    path('<str:username>/', views.UserDetailView.as_view(), name='user_detail'),
]
