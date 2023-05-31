from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.generics import ListAPIView
from rest_framework import authentication
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
            dict = {
                'category_id':category_id,
                'category_name':category_name
            }
            data_list.append(dict)

        return JsonResponse(data=data_list,safe=False)
    