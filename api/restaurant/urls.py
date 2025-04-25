from django.urls import path, include
from .views import  RestaurantInfoView, MenuView, MenuItemView, OrderView, OrderItemView, CartItemView

urlpatterns = [
    # path('', index, name='restaurant_index'),
    path('info/', RestaurantInfoView.as_view(), name='restaurant_info'),
    path('menu/', MenuView.as_view(), name='restaurant_menu_detail'),
    path('menu/item/', MenuItemView.as_view(), name='restaurant_menu_item_detail'),
    path('order/', OrderView.as_view(), name='restaurant_order_detail'),
    path('order/item/', OrderItemView.as_view(), name='restaurant_order_item_detail'),
    path('cart/', CartItemView.as_view(), name='restaurant_cart_item_detail'),
    
]
