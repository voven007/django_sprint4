from django.urls import path
from . import views
from django.conf import settings
# Импортируем функцию, позволяющую серверу разработки отдавать файлы.
from django.conf.urls.static import static
app_name = 'blog'

urlpatterns = [
    path('',
         views.PostListView.as_view(),
         name='index'),
    path('posts/create/',
         views.PostCreateView.as_view(),
         name='create_post'),
    path('posts/<int:pk>/edit/',
         views.PostUpdateView.as_view(),
         name='edit_post'),
    path('posts/<int:pk>/delete/',
         views.PostDeleteView.as_view(),
         name='delete_post'),
    path('posts/<int:pk>/',
         views.PostDetailView.as_view(),
         name='post_detail'),
    path('profile/edit/',
         views.ProfileEditUpdateView.as_view(),
         name='edit_profile', ),
    path('profile/<slug:username>/',
         views.ProfileListView.as_view(),
         name='profile'),
    path('category/<slug:category_slug>/',
         views.CategoryPostListlView.as_view(),
         name='category_posts'),
    path('posts/<post_id>/comment/',
         views.CommentCreateView.as_view(),
         name='add_comment'),
    path('posts/<post_id>/edit_comment/<comment_id>/',
         views.CommentUpdateView.as_view(),
         name='edit_comment'),
    path('posts/<post_id>/delete_comment/<comment_id>/',
         views.CommentDeleteView.as_view(),
         name='delete_comment'),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
