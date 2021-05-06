from django.urls import path, include
from rest_framework.authtoken import views
from rest_framework.routers import DefaultRouter

from .views import PostViewSet, CommentViewSet, GroupViewSet, FollowViewSet

v1_router = DefaultRouter()
v1_router.register('posts', PostViewSet)
v1_router.register(r'posts/(?P<post_id>\d+)/comments',
                   CommentViewSet, basename='comments')
v1_router.register('groups', GroupViewSet)
v1_router.register('users/(?P<user_id>\d+)/follow', FollowViewSet,
                   basename='follow')


urlpatterns = [
    path('v1/', include(v1_router.urls)),
    path('v1/api_token_auth/', views.obtain_auth_token),
]
