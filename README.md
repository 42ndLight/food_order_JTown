# food_order_JTown

```markdown
# Food Order JTown

**Food Order JTown** is a Django-powered web application designed for a burger stand in JTown (Jersey Town). This responsive platform, built with Python and hosted on AWS, enables customers to browse a categorized menu, add items to a cart, and place orders, while providing shop owners with tools to manage operations efficiently. Developed as a 6-week MVP, it focuses on simplicity, modularity, and core e-commerce functionality to drive foot traffic, streamline orders, and reward customer loyalty.

## Overview

The app serves as the online presence for a burger stand, showcasing the menu, facilitating customer interactions, and simplifying operations. It prioritizes:
- **Customer Engagement**: Easy menu browsing and optional ordering to attract buyers.
- **E-commerce**: Streamlined order placement with Stripe payments, supporting in-person pickup.
- **Loyalty**: Optional user accounts with loyalty points to encourage repeat business.
- **Management Tools**: Admin dashboard and notifications for real-time order tracking.
- **Modularity**: Organized into apps (`core`, `users`, `orders`, `payments`, `shop`) for maintainability and role-based access.

The app avoids complex features like inventory tracking or delivery logistics, focusing on order placement and staff notifications for a small business's needs.

## Features

### Customer (End-User) Features
- **Menu Browsing**: View categorized menu items (e.g., burgers, sides) with names, descriptions, prices, and images, optimized for mobile using Bootstrap.
- **User Accounts & Loyalty**: Optional registration/login to track order history and earn/redeem loyalty points (based on order totals).
- **Ordering**: Add items to a session-based cart, submit orders with notes, and pay via Stripe (guest or logged-in). Orders are saved with status updates.
- **Static Pages**: Homepage for branding, About page for stand info, and Contact page with a form/map for inquiries.

### Shop Owner/Admin Features
- **Backshop Management**: Django admin panel for CRUD operations on menu items, categories, users, and orders. Custom `shop` app dashboard for order oversight.
- **Order Monitoring**: Real-time-ish order list (via JS polling) with details and status updates (e.g., 'pending' to 'completed').
- **Notifications**: Automatic email notifications (via SendGrid/SES) on order creation; in-app alerts in the dashboard (via `Notification` model).

### System-Wide Features
- **Payment Integration**: Stripe (via `dj-stripe`) for secure payments, with webhooks syncing order and payment statuses.
- **Security**: Django authentication with role-based access (e.g., `is_shop_owner` flag) to restrict admin features.
- **Data Storage**: PostgreSQL (AWS RDS) for data, S3 for images, and session-based carts for guests.

## Tech Stack

- **Backend**: Django (views, models, forms), Python
- **Frontend**: HTML/CSS, Django templates, Bootstrap for responsive design
- **Database**: PostgreSQL (production, AWS RDS)
- **Storage**: AWS S3 for menu item images
- **Payments**: Mpesa Payment Integration
- **Notifications**: SendGrid/SES for emails, custom `Notification` model
- **Deployment**: AWS Elastic Beanstalk, CloudWatch for monitoring
- **Session Management**: Django sessions for cart persistence
- **Logging**: Django logging for debugging cart actions and errors

## Project Structure

```
food_order_JTown/
├── core/
│   ├── models.py          # MenuItem, Category models
│   ├── views.py           # Menu, homepage, about, contact views
│   └── urls.py            # URL configurations
├── users/
│   ├── models.py          # Custom User model with loyalty points
│   ├── views.py           # Registration, login, profile views
│   └── forms.py           # User-related forms
├── orders/
│   ├── models.py          # Order, OrderItem models
│   ├── views.py           # CartAddView, CartDetailView, OrderCreateView, OrderSuccessView
│   ├── forms.py           # OrderForm, OrderItemForm
│   └── templates/orders/  # cart_detail.html, checkout.html, order_success.html
├── payments/
│   ├── models.py          # Payment model (dj-stripe)
│   ├── views.py           # Payment processing views
│   
├── shop/
│   ├── models.py          # Notification model
│   ├── views.py           # Dashboard for order management
│   └── templates/shop/    # Dashboard templates
├── templates/
│   ├── base.html          # Base template with Bootstrap
│   └── menu.html          # Menu template with categories
├── static/                # CSS, JS, images
├── manage.py              # Django management script
├── requirements.txt       # Dependencies
└── ...                    # Additional Django files
```

## Prerequisites

- Python 3.8+
- Django 5.2+ (or compatible)
- AWS account (for RDS, S3, Elastic Beanstalk)
- Mpesa Sandox (Development)
- SendGrid/SES for email notifications
- Virtual environment (recommended)

## Installation & Setup

1. **Clone the Repository**:
   ```bash
   git clone https://github.com/42ndLight/food_order_JTown.git
   cd food_order_JTown
   ```

2. **Create a Virtual Environment**:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install Dependencies**:
   ```bash
   pip install django django-daraja boto3  # Core dependencies
   pip install -r requirements.txt    # If available
   ```

4. **Configure Environment**:
   - Set up `.env` with keys for AWS (RDS, S3), Stripe, and SendGrid/SES.
   - Update `settings.py` for database, static/media files, and email backend.

5. **Set Up the Database**:
   ```bash
   python manage.py makemigrations
   python manage.py migrate
   ```

6. **Load Initial Data** (Optional: Add menu items/categories via admin or fixtures):
   ```bash
   python manage.py loaddata fixtures.json  # If fixtures exist
   ```

7. **Create a Superuser** (For admin access):
   ```bash
   python manage.py createsuperuser
   ```

8. **Run the Development Server**:
   ```bash
   python manage.py runserver
   ```

9. **Access the App**:
   - Menu: `http://127.0.0.1:8000/menu/`
   - Cart: `http://127.0.0.1:8000/cart/`
   - Admin: `http://127.0.0.1:8000/admin/`  (admin only)
   - Dashboard: `http://127.0.0.1:8000/shop/dashboard/` (admin only)

## Usage Guide

### For Customers
1. **Browse Menu**: Visit `/menu/` to explore items by category (e.g., Burgers, Sides). View details and images.
2. **Add to Cart**: Select quantity and add items to the session-based cart.
3. **Checkout**: Review cart, fill out order form (guest or logged-in), and pay via Stripe.
4. **Loyalty**: Register/login to earn points on paid orders, view history, or redeem rewards.
5. **Contact**: Use the contact form or map to reach the stand.

### For Shop Owners
1. **Manage Menu**: Use `/admin/` to add/edit menu items and categories.
2. **Monitor Orders**: Access `/shop/dashboard/` to view and update order statuses (e.g., 'pending' to 'completed').
3. **Notifications**: Receive emails for new orders; check in-app alerts for real-time updates.

## Configuration

- **Settings**: In `settings.py`, set `DEBUG=False` for production, configure `ALLOWED_HOSTS`, and set up AWS (RDS, S3), Mpesa, and email backends.
- **URLs**: Map views in `urls.py` (e.g., `path('menu/', MenuView.as_view(), name='menu')`).
- **Static/Media Files**: Run `python manage.py collectstatic` and configure `MEDIA_URL` for images on S3.
- **Security**: Use Django's `LoginRequiredMixin` and permission checks for admin views.
- **Deployment**: Deploy to AWS Elastic Beanstalk with PostgreSQL (RDS) and CloudWatch for monitoring.

## Business Logic Summary

- **Customers**: Discover menu, order easily, and return via loyalty points, driving revenue and retention.
- **Owners**: Manage menu/orders efficiently, receive timely notifications, and track statuses, minimizing errors and delays.
- **System**: Secure payments (Stripe), role-based access, and data flows (menu → orders → notifications) ensure smooth operations for a small burger stand.

## Development & Contributing

- **Local Development**: Run `python manage.py runserver` for testing.
- **To Contribute**:
  1. Fork the repo.
  2. Create a feature branch (`git checkout -b feature/add-reviews`).
  3. Commit changes (`git commit -m "Add review system"`).
  4. Push to branch (`git push origin feature/add-reviews`).
  5. Open a Pull Request.
- **Testing**: Add unit tests in `tests.py` for views, forms, and models (using Django's TestCase).
- **Issues**: Report bugs or suggest features via GitHub Issues.

## Future Enhancements

- Customer reviews/ratings for menu items.
- Persistent carts for logged-in users (database-backed).
- Advanced loyalty features (e.g., tiered rewards).
- Delivery integration (e.g., third-party APIs).
- Analytics dashboard for sales/traffic insights.
- CI/CD pipeline for automated testing/deployment.

## License

This project is licensed under the MIT License. See [LICENSE](LICENSE) for details.

## Contact

- **Repository**: [42ndLight/food_order_JTown](https://github.com/42ndLight/food_order_JTown)
- **Author**: 42ndLight (GitHub user)
- **Questions?** Open an issue on GitHub.

---

*Last Updated: September 25, 2025*
```

