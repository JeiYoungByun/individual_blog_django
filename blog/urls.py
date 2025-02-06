from django.urls import path
from . import views

urlpatterns = [
    #FBV
    #path('<int:pk>/', views.single_post_page),
    #path('', views.index),

    #CBV
    path('update_comment/<int:pk>/', views.CommentUpdate.as_view()),
    path('category/<str:slug>/', views.category_page),
    path('', views.PostList.as_view(), name='post_list'),
    path('<int:pk>/', views.PostDetail.as_view(), name='post_detail'),
    path('tag/<str:slug>/', views.tag_page),
    path('create_post/', views.PostCreate.as_view()),
    path('update_post/<int:pk>/', views.PostUpdate.as_view()),
    path('<int:pk>/new_comment/', views.new_comment, name='new_comment'),
]