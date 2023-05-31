from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.generics import ListAPIView
from rest_framework import authentication
from app.serializers import *
from rest_framework.permissions import IsAuthenticated
from django.http import JsonResponse

from app.models import *
# Create your views here.

class CategoryList(APIView):
    """
        Нэхэмжлэх жагсаалт
    """
    def get(self, *args, **kwargs):
        product_datas = ProductData.objects.all()
        data_list = []
        # authentication_classes = (authentication.TokenAuthentication,
        for product_data in product_datas:
            category_id = product_data.categories_id
            category_name = product_data.categories
            data_dict = {
                'category_id':category_id,
                'category_name':category_name
            }
            data_list.append(data_dict)

        return JsonResponse(data={"data":data_list})
    

class ProductList(APIView):
    """
        Items жагсаалт
    """
    def get(self, *args, **kwargs):
        product_datas = ProductData.objects.all()
        data_list = []
        # authentication_classes = (authentication.TokenAuthentication,
        for product_data in product_datas:
            item_number = product_data.item_number
            img_path = product_data.image
            price = product_data.price
            discounted_price = product_data.discounted_price
            color = product_data.color
            data_dict = {
                'item_number':item_number,
                'img_path':img_path,
                'price':price,
                'discounted_price':discounted_price,
                'color':color
            }
            data_list.append(data_dict)

        return JsonResponse(data={"data":data_list})


class SingleProduct(APIView):
    
    def post(self, request,item_number, *args, **kwargs):
        print(item_number)
        product_data = ProductData.objects.filter(item_number=item_number).first()

        data_dict = {
            'item_number': product_data.item_number,
            'img_path': product_data.image,
            'price': product_data.price,
            'discounted_price': product_data.discounted_price,
            'color': product_data.color,
        }
        
        return JsonResponse(data={'product':data_dict})