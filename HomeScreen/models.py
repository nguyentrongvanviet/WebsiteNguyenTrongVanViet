from django.db import models

class Infomation(models.Model):
    full_name = models.CharField(max_length=255)
    date_of_birth = models.DateField(default= '2006-10-29')  
    email_address = models.EmailField()
    phone_number_field = models.CharField(max_length=255)


class MapMarker(models.Model):
    """Store clicked locations on the map"""
    title = models.CharField(max_length=255)
    latitude = models.FloatField()
    longitude = models.FloatField()
    address = models.TextField(blank=True, null=True)
    city = models.CharField(max_length=255, blank=True, null=True)
    country = models.CharField(max_length=255, blank=True, null=True)
    postcode = models.CharField(max_length=20, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.title} ({self.latitude}, {self.longitude})"
