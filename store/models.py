from django.db import models

class Product(models.Model):
    name = models.CharField(max_length=200, unique=True)
    price_gbp = models.DecimalField(max_digits=8, decimal_places=2)
    description = models.TextField(blank=True)

    def __str__(self):
        return self.name
