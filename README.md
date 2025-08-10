# CMSR - Clothes Management System with Recommendation

> A sophisticated Django-based e-commerce platform featuring intelligent clothing recommendations, comprehensive inventory management, and seamless payment processing.

[![Django](https://img.shields.io/badge/Django-5.1.4-green.svg)](https://djangoproject.com/)
[![Python](https://img.shields.io/badge/Python-3.12-blue.svg)](https://python.org/)
[![License](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![Status](https://img.shields.io/badge/Status-Active-success.svg)]()

## 🌟 **Key Features**

### 🎯 **Smart Recommendation System**
- **Content-Based Filtering**: Recommends products based on user style preferences and body measurements
- **Collaborative Filtering**: Suggests items based on similar users' purchase behavior
- **User Interaction Tracking**: Monitors views and purchases to improve recommendations
- **Personalized Shopping Experience**: Tailored product suggestions for each user

### 🛒 **E-Commerce Core**
- **Product Catalog**: Comprehensive inventory management for men's and women's clothing
- **Shopping Cart**: Persistent cart with size selection and quantity management
- **User Profiles**: Detailed profiles with body measurements and style preferences
- **Order Management**: Complete order lifecycle from placement to delivery

### 💳 **Advanced Payment System**
- **Multiple Payment Methods**: Cash, QR Code, and Credit/Debit Cards
- **QR Payment Integration**: Support for major Cambodian banks (ABA, CANADIA, ACELEDA)
- **Payment Verification**: Admin screenshot verification system for QR payments
- **Email Notifications**: Automated payment confirmations and status updates

### 👨‍💼 **Admin Management**
- **Product Management**: Add, edit, and manage inventory with SKU tracking
- **Order Processing**: Track orders from pending to delivered status
- **Payment Verification**: Manual verification system for bank transfer screenshots
- **User Management**: View and manage customer profiles and preferences

## 🏗️ **System Architecture**

### **Models Overview**
```
🔹 UserProfile - Extended user data with body measurements and preferences
🔹 Product - Clothing items with categories, sizes, and pricing
🔹 Cart - Shopping cart management
🔹 Order - Order processing and tracking
🔹 OrderItem - Individual items within orders
🔹 Recommendation - AI-powered product suggestions
🔹 UserInteraction - Track user behavior for recommendations
🔹 Testimonial - Customer feedback system
```

### **Category Structure**
```
📂 Men's Collection
├── 👔 Shirts & T-Shirts
├── 👖 Jeans & Trousers
├── 🧥 Jackets & Blazers
├── 👔 Hoodies & Sweatshirts
├── 👟 Shoes & Accessories
└── 💼 Bags & Perfumes

📂 Women's Collection
├── 👗 Dresses & Tops
├── 👚 Shirts & Blouses
├── 👖 Jeans & Trousers
├── 🧥 Jackets & Blazers
├── 👠 Shoes & Accessories
└── 👜 Bags & Perfumes
```

## 🚀 **Quick Start Guide**

### **Prerequisites**
- Python 3.8+ installed
- Django 5.1.4
- SQLite3 (default) or PostgreSQL for production

### **Installation**

1. **Clone the Repository**
```bash
git clone https://github.com/sothy8/Clothes_Management_System-Recommendation.git
cd CSR
```

2. **Create Virtual Environment**
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. **Install Dependencies**
```bash
pip install django==5.1.4
pip install pillow  # For image handling
pip install django-crispy-forms  # For better forms
```

4. **Database Setup**
```bash
python manage.py makemigrations
python manage.py migrate
python manage.py createsuperuser
```

5. **Load Sample Data (Optional)**
```bash
python manage.py loaddata datadump.json
```

6. **Run Development Server**
```bash
python manage.py runserver
```

7. **Access the Application**
- **Main Site**: http://127.0.0.1:8000/
- **Admin Panel**: http://127.0.0.1:8000/admin/

## 📱 **User Interface**

### **Customer Features**
- **Landing Page**: Modern hero sections with featured products
- **Product Browsing**: Filter by category, size, and price
- **Product Details**: Comprehensive product information with size guides
- **User Registration**: Profile creation with body measurements
- **Shopping Cart**: Add items with size selection
- **Checkout Process**: Multiple payment options
- **Order Tracking**: View order status and history
- **Recommendations**: Personalized product suggestions

### **Admin Features**
- **Dashboard**: Order overview and key metrics
- **Product Management**: Add/edit products with image upload
- **Order Management**: Process orders and update status
- **Payment Verification**: Verify QR code payment screenshots
- **User Management**: View customer profiles and preferences
- **Inventory Tracking**: Monitor stock levels and SKUs

## 🎨 **Design Features**

### **Modern UI/UX**
- **Responsive Design**: Mobile-first approach with Bootstrap-inspired styling
- **Interactive Elements**: Hover effects and smooth transitions
- **Product Gallery**: High-quality image display with zoom functionality
- **Size Guide**: Interactive size charts for better fit selection
- **Payment Flow**: Streamlined checkout with visual feedback

### **Visual Components**
- **Hero Sections**: Engaging landing page with rotating banners
- **Product Cards**: Clean product presentation with key information
- **Filter System**: Easy-to-use product filtering and sorting
- **Payment Interface**: User-friendly payment method selection
- **Admin Dashboard**: Professional admin interface for management

## 🔧 **Configuration**

### **Django Settings**
```python
# Key settings in CSR/settings.py
DEBUG = True  # Set to False in production
ALLOWED_HOSTS = []  # Add your domain in production

# Media files configuration
MEDIA_URL = '/media/'
MEDIA_ROOT = os.path.join(BASE_DIR, 'media')

# Static files configuration
STATIC_URL = '/static/'
STATICFILES_DIRS = [os.path.join(BASE_DIR, 'static')]
```

### **Database Configuration**
```python
# Default SQLite (development)
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}
```

### **Email Configuration**
```python
# Add to settings.py for email notifications
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = 'smtp.gmail.com'
EMAIL_PORT = 587
EMAIL_USE_TLS = True
EMAIL_HOST_USER = 'your-email@gmail.com'
EMAIL_HOST_PASSWORD = 'your-app-password'
```

## 📊 **Database Schema**

### **Core Tables**
```sql
-- User Profile with body measurements
UserProfile: user_id, height, weight, body_shape, style_preferences

-- Product catalog
Product: product_id, name, category, subcategory, price, size, stock, sku

-- Shopping cart
Cart: user_id, product_id, size, quantity, date_added

-- Order management
Order: order_id, user_id, total_amount, payment_method, status, payment_status

-- Recommendation system
Recommendation: user_id, recommended_items, recommendation_score
UserInteraction: user_id, product_id, interaction_type, timestamp
```

## 🛡️ **Security Features**

- **CSRF Protection**: Built-in Django CSRF middleware
- **User Authentication**: Secure login/logout system
- **Permission Management**: Admin-only access to management features
- **Input Validation**: Form validation and sanitization
- **File Upload Security**: Secure image upload handling
- **Payment Security**: Screenshot verification for payment confirmation

## 🔮 **Recommendation Algorithm**

### **Content-Based Filtering**
```python
def content_based_recommendations(user_profile, products):
    # Filter products based on user style preferences
    recommended_products = products.filter(
        Q(category__icontains=user_profile.style_preferences) |
        Q(subcategory__icontains=user_profile.style_preferences)
    )
    return recommended_products
```

### **Collaborative Filtering**
```python
def collaborative_filtering_recommendations(user, products):
    # Find users with similar purchase patterns
    similar_users = UserInteraction.objects.filter(
        product__in=UserInteraction.objects.filter(user=user).values('product')
    ).exclude(user=user).values('user').distinct()
    
    # Recommend products purchased by similar users
    recommended_products = Product.objects.filter(
        id__in=UserInteraction.objects.filter(
            user__in=similar_users,
            interaction_type='purchase'
        ).values('product')
    )
    return recommended_products
```

## 📱 **API Endpoints**

### **Main URLs**
```
/                    - Home page
/men/                - Men's collection
/women/              - Women's collection
/product/<id>/       - Product detail page
/cart/               - Shopping cart
/checkout/           - Checkout process
/profile/            - User profile
/recommendations/    - Personalized recommendations
/admin/              - Admin panel
```

### **Category URLs**
```
/men/shirts/         - Men's shirts
/men/t-shirts/       - Men's t-shirts
/men/jeans/          - Men's jeans
/women/dresses/      - Women's dresses
/women/tops/         - Women's tops
... (all subcategories)
```

## 🎯 **Business Logic**

### **Size Recommendation**
The system considers user body measurements (height, weight, body shape) to suggest appropriate sizes for different clothing types.

### **Style Matching**
Based on user style preferences and past purchases, the system recommends similar style products and complementary items.

### **Inventory Management**
Automatic stock tracking with low-stock alerts and SKU generation for efficient inventory management.

## 📈 **Performance Features**

- **Database Optimization**: Efficient queries with select_related and prefetch_related
- **Image Optimization**: Proper image handling and compression
- **Caching**: Template caching for better performance
- **Lazy Loading**: Product images loaded on demand
- **Pagination**: Large product lists split into manageable pages

## 🛠️ **Development Tools**

### **Admin Interface Enhancements**
- **Custom Admin Views**: Enhanced product and order management
- **Bulk Actions**: Mass update operations for efficiency
- **Search and Filtering**: Advanced search capabilities
- **Payment Verification**: Visual screenshot verification system

### **Form Handling**
- **Custom Forms**: Enhanced user registration and profile forms
- **Validation**: Comprehensive form validation
- **File Uploads**: Secure image upload handling
- **AJAX Support**: Dynamic form submissions

## 🌐 **Deployment Guidelines**

### **Production Checklist**
- [ ] Set `DEBUG = False`
- [ ] Configure `ALLOWED_HOSTS`
- [ ] Set up proper database (PostgreSQL recommended)
- [ ] Configure email settings
- [ ] Set up static file serving
- [ ] Configure media file storage
- [ ] Set up SSL certificate
- [ ] Configure backup strategy

### **Environment Variables**
```bash
# Create .env file for production
SECRET_KEY=your-secret-key
DEBUG=False
DATABASE_URL=postgres://user:pass@localhost/dbname
EMAIL_HOST_USER=your-email@domain.com
EMAIL_HOST_PASSWORD=your-email-password
```

## 🤝 **Contributing**

We welcome contributions from the community! Whether you're fixing bugs, adding new features, improving documentation, or suggesting enhancements, your help is appreciated.

### **How to Contribute**

#### **🐛 Reporting Bugs**
1. Check if the bug has already been reported in [Issues](https://github.com/sothy8/Clothes_Management_System-Recommendation/issues)
2. Create a new issue with the **Bug Report** template
3. Include:
   - Clear description of the bug
   - Steps to reproduce
   - Expected vs actual behavior
   - Screenshots (if applicable)
   - Environment details (Python version, Django version, OS)

#### **💡 Suggesting Features**
1. Check existing [Issues](https://github.com/sothy8/Clothes_Management_System-Recommendation/issues) for similar suggestions
2. Create a new issue with the **Feature Request** template
3. Describe:
   - The problem you're trying to solve
   - Your proposed solution
   - Alternative solutions considered
   - Additional context or mockups

#### **🔧 Development Contributions**

**Setting Up Development Environment:**
```bash
# 1. Fork and clone the repository
git clone https://github.com/YOUR_USERNAME/Clothes_Management_System-Recommendation.git
cd CSR

# 2. Create a virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# 3. Install dependencies
pip install -r requirements.txt

# 4. Set up database
python manage.py migrate
python manage.py createsuperuser

# 5. Run tests
python manage.py test

# 6. Start development server
python manage.py runserver
```

**Making Changes:**
1. Create a feature branch: `git checkout -b feature/your-feature-name`
2. Make your changes following our coding standards (see below)
3. Write or update tests for your changes
4. Run tests: `python manage.py test`
5. Commit your changes: `git commit -m "Add: brief description of changes"`
6. Push to your fork: `git push origin feature/your-feature-name`
7. Create a Pull Request with detailed description

### **📝 Coding Standards**

#### **Python/Django Guidelines**
- Follow [PEP 8](https://www.python.org/dev/peps/pep-0008/) style guide
- Use meaningful variable and function names
- Add docstrings to functions and classes
- Keep functions small and focused
- Use Django best practices

**Example:**
```python
def calculate_recommendation_score(user_profile, product):
    """
    Calculate recommendation score for a product based on user profile.
    
    Args:
        user_profile (UserProfile): User's profile with preferences
        product (Product): Product to score
        
    Returns:
        float: Recommendation score between 0-1
    """
    # Implementation here
    pass
```

#### **Frontend Guidelines**
- Use semantic HTML
- Follow responsive design principles
- Keep CSS organized and commented
- Use consistent naming conventions
- Optimize images and assets

#### **Database Guidelines**
- Write clear migration names
- Include proper indexes for query optimization
- Use appropriate field types
- Add helpful comments for complex queries

### **🧪 Testing Guidelines**

- Write tests for new features
- Maintain existing test coverage
- Include both unit and integration tests
- Test edge cases and error conditions

```python
# Example test structure
class ProductRecommendationTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user('testuser', 'test@example.com')
        self.product = Product.objects.create(name='Test Product', ...)
    
    def test_recommendation_calculation(self):
        # Test implementation
        pass
```

### **📋 Pull Request Guidelines**

**Before Submitting:**
- [ ] Code follows the style guidelines
- [ ] Tests pass locally
- [ ] New tests added for new functionality
- [ ] Documentation updated (if needed)
- [ ] No merge conflicts with main branch

**PR Description Should Include:**
- Clear title describing the change
- Detailed description of what was changed and why
- Screenshots for UI changes
- Testing instructions
- Related issue numbers (if applicable)

**Example PR Title:**
- ✅ `Add: Size recommendation algorithm for user profiles`
- ✅ `Fix: Cart quantity validation bug`
- ✅ `Update: Payment verification UI improvements`
- ❌ `Fixed stuff` (too vague)

### **🎯 Areas We Need Help With**

- **🤖 AI/ML**: Improving recommendation algorithms
- **🎨 Frontend**: UI/UX improvements and mobile responsiveness
- **🔒 Security**: Payment processing and data protection
- **📱 Mobile**: React Native or PWA development
- **📊 Analytics**: User behavior tracking and insights
- **🌐 Internationalization**: Multi-language support
- **📚 Documentation**: API docs, tutorials, and guides
- **🧪 Testing**: Automated testing and quality assurance

### **💬 Community Guidelines**

- Be respectful and inclusive
- Help others learn and grow
- Provide constructive feedback
- Follow our [Code of Conduct](CODE_OF_CONDUCT.md)

### **📞 Getting Help**

- **Questions**: Open a [Discussion](https://github.com/sothy8/Clothes_Management_System-Recommendation/discussions)
- **Chat**: Join our community chat (if available)
- **Documentation**: Check the [Wiki](https://github.com/sothy8/Clothes_Management_System-Recommendation/wiki)
- **Contact**: Reach out to [@sothy8](https://github.com/sothy8)

### **🏆 Recognition**

Contributors will be:
- Added to the Contributors section
- Mentioned in release notes
- Invited to be maintainers (for significant contributions)

**Thank you for contributing to CMSR! 🙏**

## 📄 **License**

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 👨‍💻 **Author**

**Vandeth Sothy**
- 📧 Email: [sothyvandeth8034@gmail.com](mailto:sothyvandeth8034@gmail.com)
- 📱 Phone: [+855 12 628 034](tel:+85512628034)
- 💼 LinkedIn: [www.linkedin.com/in/sothy-vandeth](https://www.linkedin.com/in/sothy-vandeth)
- 🐙 GitHub: [@sothy8](https://github.com/sothy8)
- 🚀 Project: [Clothes Management System - Recommendation](https://github.com/sothy8/Clothes_Management_System-Recommendation)

## 🙏 **Acknowledgments**

- Django framework for the robust foundation
- Bootstrap for responsive design components
- The open-source community for various tools and libraries
- Beta testers for valuable feedback and suggestions

---

<div align="center">
  <p><strong>Built with ❤️ for modern e-commerce needs</strong></p>
  <p>⭐ Star this repo if you find it helpful!</p>
</div>