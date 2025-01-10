from django.urls import path
from . import views

urlpatterns = [
    #FBV
    #path('<int:pk>/', views.single_post_page),
    #path('', views.index),

    #CBV
    path('category/<str:slug>/', views.category_page),
    path('', views.PostList.as_view(), name='post_list'),
    path('<int:pk>/', views.PostDetail.as_view(), name='post_detail'),
]