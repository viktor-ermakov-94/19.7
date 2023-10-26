from django.urls import path
from .views import *

app_name = 'board'
urlpatterns = [
    path('', PostListView.as_view(), name='posts'),
    path('<int:pk>', PostDetailView.as_view(), name='post_detail'),

    path('add/', PostCreateView.as_view(), name='post_create'),
    path('<int:pk>/edit/', PostUpdateView.as_view(), name='post_update'),
    path('<int:pk>/delete/', PostDeleteView.as_view(), name='post_delete'),

    path('categories/<str:cat_disp> <cat_key>', CategoryDetailView.as_view(), name='category_detail'),
    path('author/<int:author_pk>', AuthorPostsListView.as_view(), name='author_posts'),

    path('show_replies/', ReplyListView.as_view(), name='show_replies'),

    path('accept_reply/<int:pk>', accept_reply, name='accept_reply'),
    path('delete_reply/<int:pk>', delete_reply, name='delete_reply'),
]
