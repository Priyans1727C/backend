from django.contrib import admin
from .models import Restaurant, Menu, MenuItem, Order, OrderItem, CartItem
# Register your models here.

class RestaurantAdmin(admin.ModelAdmin):
    list_display = ('name', 'store', 'is_active', 'created_at')
    # search_fields = ('name', 'owner__username')
    list_filter = ('is_active', 'created_at')
    ordering = ('-created_at',)
    list_per_page = 20

admin.site.register(Restaurant, RestaurantAdmin)


class MenuAdmin(admin.ModelAdmin):
    list_display = ('restaurant', 'category_name')
    # search_fields = ('restaurant__name', 'category_name')
    list_filter = ('restaurant',)
    ordering = ('-restaurant',)
    list_per_page = 20

admin.site.register(Menu, MenuAdmin)

class MenuItemAdmin(admin.ModelAdmin):
    list_display = ('menu', 'name', 'price')
    # search_fields = ('menu__category_name', 'name')
    list_filter = ('menu',)
    ordering = ('-menu',)
    list_per_page = 20

admin.site.register(MenuItem, MenuItemAdmin)

class OrderAdmin(admin.ModelAdmin):
    list_display = ('restaurant', 'user', 'order_status', 'created_at')
    # search_fields = ( 'username')
    list_filter = ('order_status', 'created_at')
    ordering = ('-created_at',)
    list_per_page = 20
admin.site.register(Order, OrderAdmin)

class OrderItemAdmin(admin.ModelAdmin):
    list_display = ('order', 'item', 'quantity')
    search_fields = ('item',)
    list_filter = ('order',)
    ordering = ('-order',)
    list_per_page = 20

admin.site.register(OrderItem, OrderItemAdmin)

class CartItemAdmin(admin.ModelAdmin):
    list_display = ('user', 'item', 'quantity')
    search_fields = ('user',)
    list_filter = ('user',)
    ordering = ('-user',)
    list_per_page = 20

admin.site.register(CartItem, CartItemAdmin)