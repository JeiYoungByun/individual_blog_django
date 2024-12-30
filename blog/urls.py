from django.urls import path
from . import views

urlpatterns = [
    #FBV
    #path('<int:pk>/', views.single_post_page),
    #path('', views.index),

    #CBV
    path('', views.PostList.as_view()),
    path('<int:pk>/', views.PostDetail.as_view()),
]