#!/usr/bin/env python3
import os
import sys
import django

# Add the project directory to the Python path
sys.path.append('/home/ight42/kod3/projects/food_order_JTown')

# Set up Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'food_order_JTown.settings')
django.setup()

from core.models import Category, MenuItem

# Create categories
main_course, created = Category.objects.get_or_create(
    name="Main Course",
    defaults={'description': 'Hearty main dishes'}
)

appetizer, created = Category.objects.get_or_create(
    name="Appetizers", 
    defaults={'description': 'Starter dishes'}
)

# Create menu items
MenuItem.objects.get_or_create(
    name="Beef Stroganoff",
    defaults={
        'description': 'Tender beef strips in a rich sour cream sauce with mushrooms',
        'price': 18.99,
        'image': 'menu/stroganoff.jpeg',
        'category_id': main_course,
        'available': True
    }
)

MenuItem.objects.get_or_create(
    name="Sample Dish",
    defaults={
        'description': 'A delicious sample dish for testing',
        'price': 12.99,
        'image': 'menu/images.jpeg',
        'category_id': appetizer,
        'available': True
    }
)

print("Sample data created successfully!")
print(f"Categories: {Category.objects.count()}")
print(f"Menu Items: {MenuItem.objects.count()}")
