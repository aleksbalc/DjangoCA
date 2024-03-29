from django.urls import path
from . import views
from .models import Node
from .copy_file import copy_file_ks
from .update_node_state import createNIDList
from .copy_from_ks import copyFileFromKS, printBinaryFile

urlpatterns = [
    path('', views.index, name='index'), 
    path('login/', views.login_view, name='login'), 
    path('logout/', views.logout_view, name='logout'),
    path('add_node/', views.add_node, name='add_node'),
    path('accounts/login/', views.login_view, name='login'),
    path('no_permission/', views.no_permission, name='no_permission'),
    path('generate_keys/', views.generate_keys, name='generate_keys'),
    path('generated_keys/<int:key_generation_id>/', views.generated_keys, name='generated_keys'),
    path('manage_nodes/', views.manage_nodes, name='manage_nodes'),
    path('key_success/', views.key_success, name='key_success'),
]
