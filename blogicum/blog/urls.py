from django.urls import include, path

from . import views

app_name = 'blog'

urlpatterns = [
    path(
        'profile/<str:username>/',
        views.UserProfileDetailView.as_view(),
        name='profile'
    ),
    path(
        'edit_profile/',
        views.UserEditProfileUpdateView.as_view(),
        name='edit_profile'
    ),
    path(
        'posts/create/',
        views.CreatePostCreateView.as_view(),
        name='create_post'
    ),
    path(
        'posts/<int:pk>/',
        views.PostDetailDetailView.as_view(),
        name='post_detail'
    ),
    path(
        'posts/<int:pk>/edit/',
        views.EditPostUpdateView.as_view(),
        name='edit_post'
    ),
    path(
        'posts/<int:pk>/delete/',
        views.DeletePostDeleteView.as_view(),
        name='delete_post'
    ),
    path(
        'posts/<int:pk>/comment/',
        views.add_comment,
        name='add_comment'
        ),
    path(
        'category/<slug:category_slug>/',
        views.CategoryPostsListView.as_view(), name='category_posts'
    ),
    path('', views.IndexListView.as_view(), name='index'),
]
