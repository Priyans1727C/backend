from django.db import models
from django.conf import settings
from django.core.validators import MinValueValidator
from django.utils.translation import gettext_lazy as _
from django.conf import settings





class Store(models.Model):
    """
    Model to store information about a shop/store.
    Each store is owned by a registered user with the role of 'shop_owner'.
    """

    class StoreTypeChoices(models.TextChoices):
        RESTAURANTS = 'restaurants', 'Restaurants'
        GROCERY = 'grocery', 'Grocery'
        GARMENT = 'garment', 'Garment'
        ELECTRONICS = 'electronics', 'Electronics'
        FURNITURE = 'furniture', 'Furniture'
        BOOKS = 'books', 'Books'
        OTHER = 'other', 'Other'

    owner = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='stores',
        limit_choices_to={'role': 'shop_owner'},
        help_text=_("User who owns the store."),
    )
    name = models.CharField(max_length=255, unique=True, help_text=_("Store name"))
    type = models.CharField(
        max_length=20,
        choices=StoreTypeChoices.choices,
        default=StoreTypeChoices.OTHER,
        help_text=_("Type of store (e.g., Grocery, Garment, Electronics, etc.)"),
    )
    description = models.TextField(blank=True, null=True, help_text=_("Short description of the store"))
    created_at = models.DateTimeField(auto_now_add=True, help_text=_("Time when the store was created"))
    updated_at = models.DateTimeField(auto_now=True, help_text=_("Last updated timestamp"))

    def __str__(self):
        return f"{self.name} - {self.type}"

    class Meta:
        ordering = ['-created_at']
        verbose_name = "Store"
        verbose_name_plural = "Stores"


# Create your models here.
class Restaurant(models.Model):
    """
    Model to store information about a shop.
    Each store is owned by a registered user with the role of 'shop_owner'.
    """
    
    store = models.OneToOneField(
        Store,
        on_delete=models.CASCADE,
        related_name='restaurant',
        help_text=_("User who owns the restaurant."),
    )
    name = models.CharField(max_length=255, unique=True, help_text=_("restaurant name"))
    description = models.TextField(blank=True, null=True, help_text=_("Short description of the restaurant"))
    
    address = models.TextField(help_text=_("Full address of the restaurant"))
    city = models.CharField(max_length=100, help_text=_("City where the restaurant is located"))
    state = models.CharField(max_length=100, help_text=_("State where the restaurant is located"))
    pincode = models.CharField(max_length=10, help_text=_("Postal code of the restaurant"))

    phone = models.CharField(max_length=20, blank=True, null=True, help_text=_("restaurant contact number"))
    email = models.EmailField(blank=True, null=True, help_text=_("restaurant email address"))

    opening_time = models.TimeField(help_text=_("Opening time of the restaurant"))
    closing_time = models.TimeField(help_text=_("Closing time of the restaurant"))

    is_active = models.BooleanField(default=True, help_text=_("Whether the restaurant is active or not"))

    created_at = models.DateTimeField(auto_now_add=True, help_text=_("Time when the restaurant was created"))
    updated_at = models.DateTimeField(auto_now=True, help_text=_("Last updated timestamp"))

    def __str__(self):
        return f"{self.name} - {self.store.name})"

    class Meta:
        ordering = ['-created_at']
        verbose_name = "restaurant"
        verbose_name_plural = "restaurants"






class Menu(models.Model):
    restaurant = models.ForeignKey(Restaurant, on_delete=models.CASCADE, related_name='menus')
    category_name = models.CharField(max_length=100)
    created_at = models.DateTimeField(auto_now_add=True, help_text=_("Time when the restaurant was created"))
    updated_at = models.DateTimeField(auto_now=True, help_text=_("Last updated timestamp"))


    def __str__(self):
        return self.category_name

class MenuItem(models.Model):
    menu = models.ForeignKey(Menu, on_delete=models.CASCADE, related_name='menu_items')
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True, null=True)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    image_url = models.URLField(blank=True, null=True)
    is_available = models.BooleanField(default=True)
    is_vegetarian = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True, help_text=_("Time when the restaurant was created"))
    updated_at = models.DateTimeField(auto_now=True, help_text=_("Last updated timestamp"))


    def __str__(self):
        return self.name
    
    
class Order(models.Model):
    STATUS_CHOICES = [
        ("Pending", "Pending"),
        ("Processing", "Processing"),
        ("Delivered", "Delivered"),
        ("Cancelled", "Cancelled"),
    ]

    restaurant = models.ForeignKey(Restaurant, on_delete=models.CASCADE, related_name="orders")
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="orders")
    order_date = models.DateTimeField(auto_now_add=True)
    delivery_address = models.TextField(blank=True, null=True)
    order_status = models.CharField(max_length=50, choices=STATUS_CHOICES, default="Pending")
    total_amount = models.DecimalField(max_digits=10, decimal_places=2, validators=[MinValueValidator(0.01)])
    payment_method = models.CharField(max_length=50, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True, help_text=_("Time when the restaurant was created"))
    updated_at = models.DateTimeField(auto_now=True, help_text=_("Last updated timestamp"))

    def __str__(self):
        return f"Order {self.id} - {self.user.username}"


class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name="items")
    item = models.ForeignKey(MenuItem, on_delete=models.CASCADE, related_name="order_items")
    quantity = models.IntegerField(validators=[MinValueValidator(1)])
    price = models.DecimalField(max_digits=10, decimal_places=2, validators=[MinValueValidator(0.01)])
    special_instructions = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True, help_text=_("Time when the restaurant was created"))
    updated_at = models.DateTimeField(auto_now=True, help_text=_("Last updated timestamp"))


    def __str__(self):
        return f"{self.quantity} x {self.item.name}"
    
    
class CartItem(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="cart_items")
    store = models.ForeignKey(Store, on_delete=models.CASCADE, related_name="cart_items")
    item = models.ForeignKey(MenuItem, on_delete=models.CASCADE, related_name="cart_items")
    quantity = models.IntegerField(validators=[MinValueValidator(1)])
    added_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username} - {self.item.name} ({self.quantity})"
