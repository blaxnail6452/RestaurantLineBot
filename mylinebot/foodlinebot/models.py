from djongo import models

# Create your models here.
class taipei_restaurant(models.Model):
    restaurant_number = models.IntegerField()
    restaurant_name = models.CharField(max_length = 100)
    restaurant_rating = models.CharField(max_length = 100)
    restaurant_address = models.CharField(max_length = 100)
    restaurant_type = models.CharField(max_length = 100)
