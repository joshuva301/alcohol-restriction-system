from django.db import models
from django.utils import timezone

class User(models.Model):
    unique_id = models.CharField(max_length=12, unique=True)
    name = models.CharField(max_length=100)
    age = models.IntegerField()
    gender = models.CharField(max_length=10)
    phone = models.CharField(max_length=15)
    email = models.EmailField(unique=True)
    image = models.ImageField(upload_to='user_images/')
    
    def __str__(self):
        return self.name

class PurchaseHistory(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    purchase_date = models.DateField(auto_now_add=True)
    bottle_count = models.IntegerField(default=0)
    location = models.CharField(max_length=255, blank=True, null=True)  # Store location if needed

    def __str__(self):
        return f"{self.user.name} - {self.bottle_count} bottles on {self.purchase_date}"
