from django.db import models


class ProductData(models.Model):
    categories_id = models.TextField(blank=True, null=True)
    categories = models.TextField(blank=True, null=True)
    image = models.TextField(blank=True, null=True)
    price = models.FloatField(blank=True, null=True)
    discounted_price = models.FloatField(blank=True, null=True)
    item_number = models.TextField(blank=True, null=True)
    color = models.TextField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'product_data'