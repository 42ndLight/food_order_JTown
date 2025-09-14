from django.db import models

# Create your models here.
class Category(models.Model):
	name = models.CharField(max_length=50, unique=True)
	description = models.TextField(blank=True)

	def __str__(self):
		return self.name


class MenuItem(models.Model):
	name = models.CharField(max_length=50, unique=True)
	description = models.TextField(blank=True)
	price = models.DecimalField(max_digits=10, decimal_places=2)
	image = models.ImageField(upload_to='menu/')
	category_id = models.ForeignKey(Category,on_delete=models.CASCADE, related_name='menuitem')
	available = models.BooleanField(default=True)

	def __str__(self):
		return self.name
