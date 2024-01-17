from django.contrib import admin
from .models import Node, KeyGeneration, KeyRequests

admin.site.register(Node)
admin.site.register(KeyGeneration)
admin.site.register(KeyRequests)