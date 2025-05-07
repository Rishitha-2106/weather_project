from django.db import models
from django.contrib.auth.models import User
class UserProfile(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE,default=1)
    full_name = models.CharField(max_length=100)
    phone_number = models.CharField(max_length=15)
    branch = models.CharField(max_length=100)
    college = models.CharField(max_length=100)  
    email_id = models.EmailField(max_length=100,default='@gmail.com')
    def __str__(self):
        return self.full_name


class SearchHistory(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    city = models.CharField(max_length=100)
    searched_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username} - {self.city}"
