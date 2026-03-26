from django.urls import path

from . import views

app_name = 'blog'

urlpatterns = [
    path(
        'posts/<int:post_id>/',
        views.PostDetailDetailView.as_view(),
        name='post_detail'
    ),
    path(
        'posts/create/',
        views.PostCreateView.as_view(),
        name='create_post'
    ),
    path(
        'posts/<int:post_id>/edit/',
        views.PostUpdateView.as_view(),
        name='edit_post'
    ),
    path(
        'posts/<int:post_id>/delete/',
        views.PostDeleteView.as_view(),
        name='delete_post'
    ),
    path(
        'posts/<int:post_id>/comment/',
        views.add_comment,
        name='add_comment'
    ),
    path(
        'posts/<int:post_id>/comments/<int:comment_id>/',
        views.edit_comment,
        name='edit_comment'
    ),
    path(
        'posts/<int:post_id>/comments/<int:comment_id>/delete_comment/',
        views.delete_comment,
        name='delete_comment'
    ),
    path(
        'category/<slug:category_slug>/',
        views.CategoryPostsListView.as_view(), name='category_posts'
    ),
    path(
        'profile/me/edit/',
        views.UserEditProfileUpdateView.as_view(),
        name='edit_profile'
    ),
    path(
        'profile/<str:username>/',
        views.UserProfileDetailView.as_view(),
        name='profile'
    ),
    path('', views.IndexListView.as_view(), name='index'),
]
