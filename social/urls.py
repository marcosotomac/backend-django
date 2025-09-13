from django.urls import path
from . import views

app_name = 'social'

urlpatterns = [
    # Follow system
    path('follow/<str:username>/', views.follow_user, name='follow_user'),
    path('unfollow/<str:username>/', views.unfollow_user, name='unfollow_user'),
    path('followers/<str:username>/', views.followers_list, name='followers_list'),
    path('following/<str:username>/', views.following_list, name='following_list'),
    path('check-follow/<str:username>/',
         views.check_follow_status, name='check_follow_status'),

    # Likes
    path('like/post/<uuid:post_id>/', views.like_post, name='like_post'),
    path('unlike/post/<uuid:post_id>/', views.unlike_post, name='unlike_post'),
    path('like/comment/<uuid:comment_id>/',
         views.like_comment, name='like_comment'),
    path('unlike/comment/<uuid:comment_id>/',
         views.unlike_comment, name='unlike_comment'),

    # Comments
    path('comment/post/<uuid:post_id>/',
         views.create_comment, name='create_comment'),
    path('comment/<uuid:comment_id>/reply/',
         views.reply_comment, name='reply_comment'),
    path('comment/<uuid:comment_id>/',
         views.comment_detail, name='comment_detail'),
    path('comment/<uuid:comment_id>/update/',
         views.update_comment, name='update_comment'),
    path('comment/<uuid:comment_id>/delete/',
         views.delete_comment, name='delete_comment'),
    path('post/<uuid:post_id>/comments/',
         views.post_comments, name='post_comments'),

    # Notifications
    path('notifications/', views.notifications_list, name='notifications_list'),
    path('notifications/mark-read/', views.mark_notifications_read,
         name='mark_notifications_read'),
]
