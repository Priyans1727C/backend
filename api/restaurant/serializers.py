from rest_framework import serializers
from .models import Restaurant, Menu, MenuItem, Order, OrderItem, CartItem
from django.utils.translation import gettext_lazy as _



class RestaurantInfoSerializer(serializers.ModelSerializer):
    """
    Serializer for the Restaurant model.
    """
    class Meta:
        model = Restaurant
        fields = '__all__'
        read_only_fields = ['created_at', 'updated_at']
        extra_kwargs = {
            'name': {'required': True},
            'description': {'required': False},
            'address': {'required': True},
            'city': {'required': True},
            'state': {'required': True},
            'pincode': {'required': True},
            'phone': {'required': False},
            'email': {'required': False},
            'opening_time': {'required': True},
            'closing_time': {'required': True},
            'is_active': {'required': False}
        }


class MenuSerializer(serializers.ModelSerializer):
    """
    Serializer for the Menu model.
    """
    class Meta:
        model = Menu
        fields = '__all__'
        read_only_fields = ['created_at', 'updated_at']
        extra_kwargs = {
            'restaurant': {'required': True},
            'category_name': {'required': True}
        }
        
class MenuItemSerializer(serializers.ModelSerializer):
    """
    Serializer for the MenuItem model.
    """
    class Meta:
        model = MenuItem
        fields = '__all__'
        read_only_fields = ['created_at', 'updated_at']
        extra_kwargs = {
            'menu': {'required': True},
            'name': {'required': True},
            'price': {'required': True}
        }

class OrderSerializer(serializers.ModelSerializer):
    """
    Serializer for the Order model.
    """
    class Meta:
        model = Order
        fields = '__all__'
        read_only_fields = ['created_at', 'updated_at']
        extra_kwargs = {
            'restaurant': {'required': True},
            'user': {'required': True},
            'order_status': {'required': True}
        }

class OrderItemSerializer(serializers.ModelSerializer):
    """
    Serializer for the OrderItem model.
    """
    class Meta:
        model = OrderItem
        fields = '__all__'
        read_only_fields = ['created_at', 'updated_at']
        extra_kwargs = {
            'order': {'required': True},
            'item': {'required': True},
            'quantity': {'required': True}
        }

class CartItemSerializer(serializers.ModelSerializer):
    """
    Serializer for the CartItem model.
    """
    class Meta:
        model = CartItem
        fields = '__all__'
        read_only_fields = ['created_at', 'updated_at']
        extra_kwargs = {
            'user': {'required': True},
            'item': {'required': True},
            'quantity': {'required': True}
        }
