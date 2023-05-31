from django.urls import path
from .views import *
urlpatterns = [
    path('category_list', CategoryList.as_view(), name='category_list')
]