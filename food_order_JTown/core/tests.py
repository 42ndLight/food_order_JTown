from django.test import TestCase, Client
from django.urls import reverse
from core.models import Category, MenuItem, GalleryImage, ContactMessage
from decimal import Decimal

class MenuViewTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.category = Category.objects.create(name='Burgers', description='Handcrafted burgers')
        self.menu_item = MenuItem.objects.create(
            name='Smash Burger',
            price=Decimal('650.00'),
            category_id=self.category,
            description='Double beef patty with cheddar cheese',
            available=True
        )

    def test_menu_view_status_and_template(self):
        response = self.client.get(reverse('core:menu'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'core/menu.html')
        self.assertContains(response, 'FULL MENU')
        self.assertContains(response, 'Smash Burger')
        self.assertContains(response, 'id="category-dropdown-btn"')
        self.assertContains(response, 'id="category-dropdown-list"')

    def test_menu_view_context_data(self):
        response = self.client.get(reverse('core:menu'))
        self.assertIn('categories', response.context)
        self.assertIn('items_by_category', response.context)
        categories = response.context['categories']
        self.assertIn(self.category, categories)
        self.assertEqual(len(response.context['items_by_category']), 1)


class ContactViewTests(TestCase):
    def setUp(self):
        self.client = Client()

    def test_contact_get_renders_form_and_details(self):
        response = self.client.get(reverse('core:contact'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'core/contact.html')
        self.assertContains(response, 'GET IN TOUCH')
        self.assertContains(response, '+254 712 345 678')
        self.assertContains(response, 'hello@jtownburgers.com')
        self.assertContains(response, 'Westside Heights')
        self.assertContains(response, 'Send Message')

    def test_contact_post_valid_saves_message_and_redirects(self):
        post_data = {
            'name': 'Alex Kimani',
            'email': 'alex@example.com',
            'phone': '+254711223344',
            'message': 'We would like to book catering for 50 people next Saturday.',
        }
        response = self.client.post(reverse('core:contact'), post_data)
        self.assertRedirects(response, reverse('core:contact'))

        # Verify record saved in database
        self.assertEqual(ContactMessage.objects.count(), 1)
        msg = ContactMessage.objects.first()
        self.assertEqual(msg.name, 'Alex Kimani')
        self.assertEqual(msg.email, 'alex@example.com')
        self.assertIn('Alex Kimani', str(msg))

    def test_contact_post_invalid_shows_errors(self):
        response = self.client.post(reverse('core:contact'), {
            'name': '',
            'email': 'invalid-email',
            'message': '',
        })
        self.assertEqual(response.status_code, 200)
        self.assertEqual(ContactMessage.objects.count(), 0)
        self.assertContains(response, 'Please correct the following')


class AboutViewTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.img1 = GalleryImage.objects.create(
            title='Kitchen Flat-Top Grill',
            order=1,
            is_active=True
        )
        self.img2 = GalleryImage.objects.create(
            title='Inactive Draft Slide',
            order=2,
            is_active=False
        )

    def test_about_get_renders_story_and_active_gallery(self):
        response = self.client.get(reverse('core:about'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'core/about.html')
        self.assertContains(response, 'THE JTOWN STORY')
        self.assertContains(response, 'HARD SMASH.')
        self.assertContains(response, 'GALLERY & BEHIND THE SCENES')
        
        # Verify gallery images in context
        self.assertIn('gallery_images', response.context)
        gallery = response.context['gallery_images']
        self.assertEqual(gallery.count(), 1)
        self.assertIn(self.img1, gallery)
        self.assertNotIn(self.img2, gallery)
        self.assertEqual(str(self.img1), 'Kitchen Flat-Top Grill')


