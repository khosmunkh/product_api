from django.urls import path
from .views import *
urlpatterns = [
    path('category_list', CategoryList.as_view(), name='category_list'),
    path('product_list', ProductList.as_view(), name='product_list'),
    path('single_product/<str:item_number>', SingleProduct.as_view(), name='single_product')
]