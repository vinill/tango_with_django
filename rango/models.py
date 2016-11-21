from django.db import models

class Category(models.Model):
    name = models.CharField(max_length=128, unique=True)
    def __str__(self): # For Python 2, use __unicode__ too
     return self.name
class Page(models.Model):
    category = models.ForeignKey(Category)
    title = models.CharField(max_length=128)
    url = models.URLField()
    views = models.IntegerField(default=0)
    def __str__(self): # For Python 2, use __unicode__ too
        return self.title




#TODO TEST FILE FIELD https://docs.djangoproject.com/es/1.9/ref/models/fields/#model-field-types