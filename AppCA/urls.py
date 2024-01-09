from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='index'), 
    path('register/', views.register, name='register'), 
    path('login/', views.login_view, name='login'), 
    path('logout/', views.logout_view, name='logout'),
    path('add_node/', views.add_node, name='add_node'),
    path('accounts/login/', views.login_view, name='login'),
    path('no_permission/', views.no_permission, name='no_permission'),
]