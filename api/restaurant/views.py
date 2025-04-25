from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework.views import APIView
from .models import Restaurant, Menu, MenuItem, Order, OrderItem, CartItem
from .serializers import RestaurantInfoSerializer, MenuSerializer, MenuItemSerializer, OrderSerializer, OrderItemSerializer, CartItemSerializer
from drf_spectacular.utils import extend_schema, OpenApiParameter
from drf_spectacular.types import OpenApiTypes
from django.contrib.auth import get_user_model

class RestaurantInfoView(generics.GenericAPIView):
    serializer_class = RestaurantInfoSerializer
    @extend_schema(
        parameters=[
            OpenApiParameter(
                name='store_id',         # The name of the query parameter
                description='Optional ID of the store to filter data for.', # Description for docs
                required=False,         # Set to True if the parameter is mandatory
                type=OpenApiTypes.INT,  # Use INT, STR, UUID, BOOL, DATE, DATETIME etc.
                                        # Or use simple Python types: int, str, bool
                location=OpenApiParameter.QUERY # Specify this is a query parameter
                                                # Other options: PATH, HEADER, COOKIE
            ),
            # Add more OpenApiParameter instances here if you have other query params
        ],
        # You can add other extend_schema arguments like responses, summary etc.
        summary="Retrieve data, optionally filtered by store ID",
        responses={200: OpenApiTypes.OBJECT} # Example response
    )
    def get(self, request, *args, **kwargs):
        """
        Retrieve restaurant information.
        If store_id is provided, it will return the restaurant information for that store.
        """
        
        store_id = request.query_params.get('store_id')
        if not store_id:
            return Response({"error": "store_id is required", "params": "/?store_id=<int>"}, status=status.HTTP_400_BAD_REQUEST)

        try:
            restaurant = Restaurant.objects.get(store_id=store_id)
            serializer = self.get_serializer(restaurant)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except Restaurant.DoesNotExist:
            return Response({"error": "Restaurant not found for the given store_id"}, status=status.HTTP_404_NOT_FOUND)

    def post(self, request, *args, **kwargs):
        """
        Add a new restaurant entry.
        The request should contain a JSON object with the restaurant details.
        """
        
        store_id = request.data.get('store')
        print(type(request.data))
        if not store_id:
            return Response({"error": "store_id is required"}, status=status.HTTP_400_BAD_REQUEST)

        if Restaurant.objects.filter(store_id=store_id).exists():
            return Response({"error": "A Restaurant already exists for the given store_id"}, status=status.HTTP_400_BAD_REQUEST)

        serializer = self.get_serializer(data=request.data.get('attributes', request.data)) # Handles both nested and non-nested data.
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def put(self, request, *args, **kwargs):
        """
        Update an existing restaurant entry.
        The request should contain a JSON object with the updated restaurant details.
        """
        store_id = request.data.get('store')
        if not store_id:
            return Response({"error": "store_id is required"}, status=status.HTTP_400_BAD_REQUEST)

        try:
            restaurant = Restaurant.objects.get(store_id=store_id)
            serializer = self.get_serializer(restaurant, data=request.data.get('attributes', request.data), partial=True) #handles nested and non-nested data.
            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data, status=status.HTTP_200_OK)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        except Restaurant.DoesNotExist:
            return Response({"error": "Restaurant not found for the given store_id"}, status=status.HTTP_404_NOT_FOUND)

    def delete(self, request, *args, **kwargs):
        """
        Delete an existing restaurant entry.
        The request should contain the store_id of the restaurant to be deleted.
        """
        store_id = request.query_params.get('store_id')
        if not store_id:
            return Response({"error": "store_id is required", "params": "/?store_id=<int>"}, status=status.HTTP_400_BAD_REQUEST)
        try:
            restaurant = Restaurant.objects.get(store_id=store_id)
            restaurant.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        except Restaurant.DoesNotExist:
            return Response({"error": "Restaurant not found for the given store_id"}, status=status.HTTP_404_NOT_FOUND)
        

class MenuView(APIView):
    """
    Handles CRUD operations for Restaurant Menus.
    """

    def get_restaurant(self, store_id):
        try:
            return Restaurant.objects.get(store_id=store_id)
        except Restaurant.DoesNotExist:
            return None

    def get(self, request, *args, **kwargs):
        store_id = request.query_params.get('store_id')
        if not store_id:
            return Response({"error": "store_id is required", "params": "/?store_id=<int>"}, status=status.HTTP_400_BAD_REQUEST)

        restaurant = self.get_restaurant(store_id)
        if not restaurant:
            return Response({"error": "Restaurant not found for the given store_id"}, status=status.HTTP_404_NOT_FOUND)

        menus = restaurant.menus.all()
        serializer = MenuSerializer(menus, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def post(self, request, *args, **kwargs):
        store_id = request.data.get('store_id')
        if not store_id:
            return Response({"error": "store_id is required"}, status=status.HTTP_400_BAD_REQUEST)

        restaurant = self.get_restaurant(store_id)
        if not restaurant:
            return Response({"error": "Restaurant not found for the given store_id"}, status=status.HTTP_404_NOT_FOUND)

        serializer = MenuSerializer(data=request.data.get('attributes', request.data))
        if serializer.is_valid():
            serializer.save(restaurant=restaurant)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def put(self, request, *args, **kwargs):
        store_id = request.data.get('store_id')
        menu_id = request.data.get('menu_id')

        if not store_id or not menu_id:
            return Response({"error": "store_id and menu_id are required"}, status=status.HTTP_400_BAD_REQUEST)

        restaurant = self.get_restaurant(store_id)
        if not restaurant:
            return Response({"error": "Restaurant not found for the given store_id"}, status=status.HTTP_404_NOT_FOUND)

        try:
            menu = restaurant.menus.get(id=menu_id)
        except Menu.DoesNotExist:
            return Response({"error": "Menu not found with the given id"}, status=status.HTTP_404_NOT_FOUND)

        serializer = MenuSerializer(menu, data=request.data.get('attributes', request.data), partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, *args, **kwargs):
        store_id = request.query_params.get('store_id') or request.data.get('store_id')
        menu_id = request.query_params.get('menu_id') or request.data.get('menu_id')

        if not store_id or not menu_id:
            return Response({"error": "store_id and menu_id are required"}, status=status.HTTP_400_BAD_REQUEST)

        restaurant = self.get_restaurant(store_id)
        if not restaurant:
            return Response({"error": "Restaurant not found for the given store_id"}, status=status.HTTP_404_NOT_FOUND)

        try:
            menu = restaurant.menus.get(id=menu_id)
        except Menu.DoesNotExist:
            return Response({"error": "Menu not found with the given id"}, status=status.HTTP_404_NOT_FOUND)

        menu.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
    
    
    
class MenuItemView(APIView):
    """
    Handles CRUD operations for Menu Items.
    """

    def get_menu(self, store_id, menu_id):
        try:
            restaurant = Restaurant.objects.get(store_id=store_id)
            return restaurant.menus.get(id=menu_id)
        except (Restaurant.DoesNotExist, Menu.DoesNotExist):
            return None
    def get(self, request, *args, **kwargs):
        store_id = request.query_params.get('store_id') or request.data.get('store_id')
        menu_id = request.query_params.get('menu_id') or request.data.get('menu_id')

        if not store_id or not menu_id:
            return Response({"error": "store_id and menu_id are required", "params": "/?store_id=<int>&menu_id=<int>"}, status=status.HTTP_400_BAD_REQUEST)

        menu = self.get_menu(store_id, menu_id)
        if not menu:
            return Response({"error": "Menu not found for the given store_id and menu_id"}, status=status.HTTP_404_NOT_FOUND)

        menu_items = menu.menu_items.all()
        serializer = MenuItemSerializer(menu_items, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
    def post(self, request, *args, **kwargs):
        store_id = request.data.get('store_id')
        menu_id = request.data.get('menu_id')
        request.data['menu'] = menu_id

        if not store_id or not menu_id:
            return Response({"error": "store_id and menu_id are required"}, status=status.HTTP_400_BAD_REQUEST)

        menu = self.get_menu(store_id, menu_id)
        if not menu:
            return Response({"error": "Menu not found for the given store_id and menu_id"}, status=status.HTTP_404_NOT_FOUND)
        
        serializer = MenuItemSerializer(data=request.data.get('attributes', request.data))
        if serializer.is_valid():
            serializer.save(menu=menu)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    def put(self, request, *args, **kwargs):
        store_id = request.data.get('store_id')
        menu_id = request.data.get('menu_id')
        item_id = request.data.get('item_id')
        request.data['menu'] = menu_id

        if not store_id or not menu_id or not item_id:
            return Response({"error": "store_id, menu_id and item_id are required"}, status=status.HTTP_400_BAD_REQUEST)

        menu = self.get_menu(store_id, menu_id)
        if not menu:
            return Response({"error": "Menu not found for the given store_id and menu_id"}, status=status.HTTP_404_NOT_FOUND)

        try:
            item = menu.menu_items.get(id=item_id)
        except MenuItem.DoesNotExist:
            return Response({"error": "MenuItem not found with the given id"}, status=status.HTTP_404_NOT_FOUND)

        serializer = MenuItemSerializer(item, data=request.data.get('attributes', request.data), partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    def delete(self, request, *args, **kwargs):
        store_id = request.query_params.get('store_id') or request.data.get('store_id')
        menu_id = request.query_params.get('menu_id') or request.data.get('menu_id')
        item_id = request.query_params.get('item_id') or request.data.get('item_id')

        if not store_id or not menu_id or not item_id:
            return Response({"error": "store_id, menu_id and item_id are required"}, status=status.HTTP_400_BAD_REQUEST)

        menu = self.get_menu(store_id, menu_id)
        if not menu:
            return Response({"error": "Menu not found for the given store_id and menu_id"}, status=status.HTTP_404_NOT_FOUND)

        try:
            item = menu.menu_items.get(id=item_id)
        except MenuItem.DoesNotExist:
            return Response({"error": "MenuItem not found with the given id"}, status=status.HTTP_404_NOT_FOUND)

        item.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
    

class OrderView(APIView):
    """
    Handles CRUD operations for Orders.
    """


    def get_order(self, store_id ,order_id):
        try:
            restaurant = Restaurant.objects.get(store_id=store_id)
            return restaurant.orders.get(id=order_id)
        except (Restaurant.DoesNotExist, Order.DoesNotExist):
            return None
           
    def get(self, request, *args, **kwargs):
        store_id = request.query_params.get('store_id') or request.data.get('store_id')
        order_id = request.query_params.get('order_id') or request.data.get('order_id')
        if not order_id or not store_id:
            return Response({"error": "store_id and order_id is required", "params": "/?order_id=<int>"}, status=status.HTTP_400_BAD_REQUEST)

        order = self.get_order(store_id, order_id)
        if not order:
            return Response({"error": "Order not found for the given order_id"}, status=status.HTTP_404_NOT_FOUND)

        serializer = OrderSerializer(order)
        return Response(serializer.data, status=status.HTTP_200_OK)
    def post(self, request, *args, **kwargs):
        store_id = request.data.get('store_id')
        user_id = request.data.get('user_id')

        if not store_id or not user_id:
            return Response({"error": "store_id and user_id are required"}, status=status.HTTP_400_BAD_REQUEST)

        # Get restaurant
        restaurant = Restaurant.objects.filter(store_id=store_id).first()
        if not restaurant:
            return Response({"error": "Restaurant not found for the given store_id"}, status=status.HTTP_404_NOT_FOUND)

        # Get user
        User = get_user_model()
        try:
            user = User.objects.get(id=user_id)
        except User.DoesNotExist:
            return Response({"error": "Invalid user_id"}, status=status.HTTP_400_BAD_REQUEST)

        # Prepare data — set user and restaurant as IDs, not instances
        data = request.data.copy()
        data['user'] = user.id
        data['restaurant'] = restaurant.id

        serializer = OrderSerializer(data=data.get('attributes', data))
        if serializer.is_valid():
            # Pass instances here, not in the data
            serializer.save(user=user, restaurant=restaurant)
            return Response(serializer.data, status=status.HTTP_201_CREATED)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    def put(self, request, *args, **kwargs):
        store_id = request.data.get('store_id')
        order_id = request.data.get('order_id')
        user_id = request.data.get('user_id')

        if not store_id or not order_id or not user_id:
            return Response(
                {"error": "store_id, order_id, and user_id are required"},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Fetch restaurant
        restaurant = Restaurant.objects.filter(store_id=store_id).first()
        if not restaurant:
            return Response(
                {"error": "Restaurant not found for the given store_id"},
                status=status.HTTP_404_NOT_FOUND
            )

        # Fetch user
        User = get_user_model()
        try:
            user = User.objects.get(id=user_id)
        except User.DoesNotExist:
            return Response({"error": "Invalid user_id"}, status=status.HTTP_400_BAD_REQUEST)

        # Fetch order
        try:
            order = restaurant.orders.get(id=order_id)
        except Order.DoesNotExist:
            return Response(
                {"error": "Order not found for the given order_id and store_id"},
                status=status.HTTP_404_NOT_FOUND
            )

        # Update data
        data = request.data.copy()
        data['user'] = user.id
        data['restaurant'] = restaurant.id

        serializer = OrderSerializer(order, data=data.get('attributes', data), partial=True)
        if serializer.is_valid():
            serializer.save(user=user, restaurant=restaurant)
            return Response(serializer.data, status=status.HTTP_200_OK)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, *args, **kwargs):
        store_id = request.query_params.get('store_id') or request.data.get('store_id')
        order_id = request.query_params.get('order_id') or request.data.get('order_id')
        user_id = request.query_params.get('`user_id`') or request.data.get('user_id')

        if not store_id or not order_id or not user_id:
            return Response(
                {"error": "store_id, order_id, and user_id are required"},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Fetch restaurant
        restaurant = Restaurant.objects.filter(store_id=store_id).first()
        if not restaurant:
            return Response(
                {"error": "Restaurant not found for the given store_id"},
                status=status.HTTP_404_NOT_FOUND
            )

        # Fetch user
        User = get_user_model()
        try:
            user = User.objects.get(id=user_id)
        except User.DoesNotExist:
            return Response({"error": "Invalid user_id"}, status=status.HTTP_400_BAD_REQUEST)

        # Fetch order
        try:
            order = restaurant.orders.get(id=order_id)
        except Order.DoesNotExist:
            return Response(
                {"error": "Order not found for the given order_id and store_id"},
                status=status.HTTP_404_NOT_FOUND
            )
        order.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

class OrderItemView(APIView):
    """
    Handles CRUD operations for Order Items.
    """
    def get_order(self, store_id ,order_id):
        try:
            restaurant = Restaurant.objects.get(store_id=store_id)
            return restaurant.orders.get(id=order_id)
        except (Restaurant.DoesNotExist, Order.DoesNotExist):
            return None
    def get(self, request, *args, **kwargs):
        store_id = request.query_params.get('store_id') or request.data.get('store_id')
        order_id = request.query_params.get('order_id') or request.data.get('order_id')
        user_id = request.query_params.get('`user_id`') or request.data.get('user_id')

        if not order_id or not store_id:
            return Response({"error": "store_id and order_id is required", "params": "/?order_id=<int>"}, status=status.HTTP_400_BAD_REQUEST)

        order = self.get_order(store_id, order_id)
        if not order:
            return Response({"error": "Order not found for the given order_id"}, status=status.HTTP_404_NOT_FOUND)

        order_items = order.items.all()
        serializer = OrderItemSerializer(order_items, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def post(self, request, *args, **kwargs):
        store_id = request.data.get('store_id')
        order_id = request.data.get('order_id')
        item_id = request.data.get('item_id')          #menu item id
        request.data['item'] = item_id
        request.data['order'] = order_id

        if not all([store_id, order_id, item_id]):
            return Response({"error": "store_id, order_id and item_id are required"}, status=status.HTTP_400_BAD_REQUEST)

        order = self.get_order(store_id, order_id)
        if not order:
            return Response({"error": "Order not found for the given order_id"}, status=status.HTTP_404_NOT_FOUND)

        try:
            menu_item = MenuItem.objects.get(id=item_id)
        except MenuItem.DoesNotExist:
            return Response({"error": "MenuItem not found"}, status=status.HTTP_404_NOT_FOUND)

        serializer = OrderItemSerializer(data=request.data.get('attributes', request.data))
        if serializer.is_valid():
            serializer.save(order=order, item=menu_item)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


    def put(self, request, *args, **kwargs):
        store_id = request.data.get('store_id')
        order_id = request.data.get('order_id')
        order_item_id = request.data.get('item_id')  # ID of OrderItem, not MenuItem

        if not all([store_id, order_id, order_item_id]):
            return Response({"error": "store_id, order_id, and item_id (OrderItem.id) are required"}, status=status.HTTP_400_BAD_REQUEST)

        order = self.get_order(store_id, order_id)
        if not order:
            return Response({"error": "Order not found for the given order_id"}, status=status.HTTP_404_NOT_FOUND)

        try:
            order_item = order.items.get(id=order_item_id)
        except OrderItem.DoesNotExist:
            return Response({"error": "OrderItem not found with the given id"}, status=status.HTTP_404_NOT_FOUND)

        serializer = OrderItemSerializer(order_item, data=request.data.get('attributes', request.data), partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    
    def delete(self, request, *args, **kwargs):
        store_id = request.query_params.get('store_id') or request.data.get('store_id')
        order_id = request.query_params.get('order_id') or request.data.get('order_id')
        order_item_id = request.query_params.get('item_id') or request.data.get('item_id')

        if not all([store_id, order_id, order_item_id]):
            return Response({"error": "store_id, order_id and item_id are required"}, status=status.HTTP_400_BAD_REQUEST)

        order = self.get_order(store_id, order_id)
        if not order:
            return Response({"error": "Order not found for the given order_id"}, status=status.HTTP_404_NOT_FOUND)

        try:
            order_item = order.items.get(id=order_item_id)
        except OrderItem.DoesNotExist:
            return Response({"error": "OrderItem not found with the given id"}, status=status.HTTP_404_NOT_FOUND)

        order_item.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class CartItemView(APIView):
    """
    Handles CRUD operations for Cart Items.
    """
    def get_cart(self, user_id):
        try:
            return CartItem.objects.filter(user_id=user_id)
        except CartItem.DoesNotExist:
            return None
    def get_item(self, store_id, item_id):
        try:
            restaurant = Restaurant.objects.get(store_id=store_id)
            return MenuItem.objects.get(menu__restaurant=restaurant, id=item_id)
        except (Restaurant.DoesNotExist, MenuItem.DoesNotExist):
            return None

        
    def get(self, request, *args, **kwargs):
        user_id = request.query_params.get('user_id') or request.data.get('user_id')
        if not user_id:
            return Response({"error": "user_id is required"}, status=status.HTTP_400_BAD_REQUEST)

        cart_items = self.get_cart(user_id)
        if not cart_items:
            return Response({"error": "Cart not found for the given user_id"}, status=status.HTTP_404_NOT_FOUND)

        serializer = CartItemSerializer(cart_items, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
    
    def post(self, request, *args, **kwargs):
        user_id = request.data.get('user_id')
        item_id = request.data.get('item_id')
        store_id = request.data.get('store_id')
        
        if not all([user_id, item_id, store_id]):
            return Response({"error": "user_id, item_id and store_id are required"}, status=status.HTTP_400_BAD_REQUEST)
     
        user = get_user_model()
        try:
            user = user.objects.get(id=user_id)
        except user.DoesNotExist:
            return Response({"error": "Invalid user_id"}, status=status.HTTP_400_BAD_REQUEST)
        if not user:
            return Response({"error": "User not found"}, status=status.HTTP_404_NOT_FOUND)
        
        menu_item = self.get_item(store_id, item_id)
        if not menu_item:
            return Response({"error": "MenuItem not found"}, status=status.HTTP_404_NOT_FOUND)
        
        request.data['item'] = item_id
        request.data['user'] = user_id
        request.data['store'] = store_id
        serializer = CartItemSerializer(data=request.data.get('attributes', request.data))
        if serializer.is_valid():
            serializer.save(user=user, item=menu_item)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    def put(self, request, *args, **kwargs):
        user_id = request.data.get('user_id')
        cart_item_id = request.data.get('cart_item_id')

        if not all([user_id, cart_item_id]):
            return Response({"error": "user_id and cart_item_id are required"}, status=status.HTTP_400_BAD_REQUEST)
        user = get_user_model()
        try:
            user = user.objects.get(id=user_id)
        except user.DoesNotExist:
            return Response({"error": "Invalid user_id"}, status=status.HTTP_400_BAD_REQUEST)
        if not user:
            return Response({"error": "User not found"}, status=status.HTTP_404_NOT_FOUND)
        try:
            cart_item = CartItem.objects.get(id=cart_item_id, user=user)
        except CartItem.DoesNotExist:
            return Response({"error": "CartItem not found"}, status=status.HTTP_404_NOT_FOUND)
        serializer = CartItemSerializer(cart_item, data=request.data.get('attributes', request.data), partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    def delete(self, request, *args, **kwargs):
        user_id = request.query_params.get('user_id') or request.data.get('user_id')
        cart_item_id = request.query_params.get('cart_item_id') or request.data.get('cart_item_id')

        if not all([user_id, cart_item_id]):
            return Response({"error": "user_id and cart_item_id are required"}, status=status.HTTP_400_BAD_REQUEST)

        user = get_user_model()
        try:
            user = user.objects.get(id=user_id)
        except user.DoesNotExist:
            return Response({"error": "Invalid user_id"}, status=status.HTTP_400_BAD_REQUEST)
        if not user:
            return Response({"error": "User not found"}, status=status.HTTP_404_NOT_FOUND)
        
        try:
            cart_item = CartItem.objects.get(id=cart_item_id, user=user)
        except CartItem.DoesNotExist:
            return Response({"error": "CartItem not found"}, status=status.HTTP_404_NOT_FOUND)

        cart_item.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
    