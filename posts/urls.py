from django.urls import path
from . import views

app_name = 'posts'

urlpatterns = [
    # CRUD de posts
    path('create/', views.PostCreateView.as_view(), name='post_create'),
    path('<uuid:pk>/', views.PostDetailView.as_view(), name='post_detail'),
    path('<uuid:pk>/update/', views.PostUpdateView.as_view(), name='post_update'),
    path('<uuid:pk>/delete/', views.PostDeleteView.as_view(), name='post_delete'),
    path('<uuid:pk>/stats/', views.post_stats_view, name='post_stats'),

    # Listado de posts
    path('', views.PostListView.as_view(), name='post_list'),
    path('feed/', views.FeedView.as_view(), name='feed'),
    path('my-posts/', views.my_posts_view, name='my_posts'),
    path('user/<str:username>/', views.UserPostsView.as_view(), name='user_posts'),

    # Hashtags
    path('hashtag/<str:hashtag_name>/',
         views.HashtagPostsView.as_view(), name='hashtag_posts'),
    path('hashtags/trending/', views.TrendingHashtagsView.as_view(),
         name='trending_hashtags'),
]
