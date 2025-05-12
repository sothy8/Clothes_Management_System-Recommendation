from django.urls import path
from . import views

urlpatterns = [
    # Home and Account-related URLs
    path('', views.home, name='home'),
    path('signup/', views.signup, name='signup'),
    path('signin/', views.signin, name='signin'),
    path('signout/', views.signout, name='signout'),
    path('profile/', views.profile, name='profile'),
    
    # Check Out / Payment
    path('cart/', views.cart, name='cart'),
    path('checkout/', views.checkout, name='checkout'),
    path('confirm_order/', views.confirm_order, name='confirm_order'),
    
    # Product and Category URLs
    path('shop/', views.shop, name='shop'),
    path('products/<str:category>/', views.product_list, name='product_list'),
    path('product/<str:product_id>/', views.product_detail, name='product_detail'),
    path('add-to-cart/<int:product_id>/', views.add_to_cart, name='add_to_cart'),
    path('update-cart/', views.update_cart, name='update_cart'),
    
    # Recommendations and Testimonials
    path('recommendations/', views.recommendations, name='recommendations'),
    path('submit-testimonial/', views.submit_testimonial, name='submit_testimonial'),
    
    # Contact and Search
    path('contact/', views.contact, name='contact'),
    path('search/', views.search, name='search'),

    # Men Categories
    path('men/shirts/', views.men_shirts, name='men/men_shirts'),
    path('men/t_shirts/', views.men_tshirts, name='men/men_t_shirts'),
    path('men/polo_shirts/', views.men_polo_shirts, name='men/men_polo_shirts'),
    path('men/blazers/', views.men_blazers, name='men/men_blazers'),
    path('men/jackets/', views.men_jackets, name='men/men_jackets'),
    path('men/hoodies_sweatshirts/', views.men_hoodies_sweatshirts, name='men/men_hoodies_sweatshirts'),
    path('men/sweaters_cardigans/', views.men_sweaters_cardigans, name='men/men_sweaters_cardigans'),
    path('men/jeans/', views.men_jeans, name='men/men_jeans'),
    path('men/trousers/', views.men_trousers, name='men/men_trousers'),
    path('men/shorts/', views.men_shorts, name='men/men_shorts'),
    path('men/shoes/', views.men_shoes, name='men/men_shoes'),
    path('men/bags/', views.men_bags, name='men/men_bags'),
    path('men/accessories/', views.men_accessories, name='men/men_accessories'),
    path('men/perfume/', views.men_perfume, name='men/men_perfume'),

    # Women Categories
    path('women/shirts/', views.women_shirts, name='women/women_shirts'),
    path('women/t_shirts/', views.women_tshirts, name='women/women_t_shirts'),
    path('women/tops/', views.women_tops, name='women/women_tops'),
    path('women/dresses/', views.women_dresses, name='women/women_dresses'),
    path('women/polo_shirts/', views.women_polo_shirts, name='women/women_polo_shirts'),
    path('women/blazers/', views.women_blazers, name='women/women_blazers'),
    path('women/jackets/', views.women_jackets, name='women/women_jackets'),
    path('women/hoodies_sweatshirts/', views.women_hoodies_sweatshirts, name='women/women_hoodies_sweatshirts'),
    path('women/sweaters_cardigans/', views.women_sweaters_cardigans, name='women/women_sweaters_cardigans'),
    path('women/shorts/', views.women_shorts, name='women/women_shorts'),
    path('women/jeans/', views.women_jeans, name='women/women_jeans'),
    path('women/trousers/', views.women_trousers, name='women/women_trousers'),
    path('women/shoes/', views.women_shoes, name='women/women_shoes'),
    path('women/bags/', views.women_bags, name='women/women_bags'),
    path('women/accessories/', views.women_accessories, name='women/women_accessories'),
    path('women/perfume/', views.women_perfume, name='women/women_perfume'),
] 