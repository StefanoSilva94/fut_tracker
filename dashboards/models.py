from django.db import models


class Player(models.Model):
    name = models.CharField(max_length=100)
    pack_name = models.CharField(max_length=100)
    rating = models.IntegerField()
    position = models.CharField(max_length=50)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    
    class Meta:
        db_table = 'packed_items'

    def __str__(self):
        return self.name