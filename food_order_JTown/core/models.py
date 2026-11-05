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


class GalleryImage(models.Model):
	title = models.CharField(max_length=100)
	image = models.ImageField(upload_to='gallery/')
	order = models.PositiveIntegerField(default=0)
	is_active = models.BooleanField(default=True)
	created_at = models.DateTimeField(auto_now_add=True)

	class Meta:
		ordering = ['order', '-created_at']
		verbose_name = 'Gallery Image'
		verbose_name_plural = 'Gallery Images'

	def __str__(self):
		return self.title


class ContactMessage(models.Model):
	name = models.CharField(max_length=100)
	email = models.EmailField()
	phone = models.CharField(max_length=20, blank=True)
	message = models.TextField()
	created_at = models.DateTimeField(auto_now_add=True)

	class Meta:
		ordering = ['-created_at']
		verbose_name = 'Contact Message'
		verbose_name_plural = 'Contact Messages'

	def __str__(self):
		return f"Message from {self.name} ({self.email})"
