from django.shortcuts import render
from rest_framework import generics
from .models import MenuItem , Cart, Order, OrderItem
from .serializers import MenuItemSerializer, ManagerSerializer, DeliveryCrewSerializer, CartSerializer, OrderItemSerializer, OrderSerializer
from rest_framework.response import Response
from rest_framework.decorators import api_view
from django.shortcuts import get_object_or_404
from rest_framework import status
from django.core.paginator import Paginator, EmptyPage
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from rest_framework.decorators import permission_classes, throttle_classes
from rest_framework.throttling import AnonRateThrottle, UserRateThrottle
from .throttles import TenCallsPerMinute
from .permissions import IsManager, IsDeliveryCrew
from django.contrib.auth.models import User, Group

# Create your views here.
#@permission_classes([IsAuthenticated])

class MenuItemsView(generics.ListCreateAPIView):
    queryset = MenuItem.objects.all()
    serializer_class = MenuItemSerializer
    def get_permissions(self):
        permission_classes = []
        if self.request.method != 'GET':
            permission_classes = [IsAuthenticated,IsManager | IsAdminUser]

        return [permission() for permission in permission_classes]
    
class SingleMenuItemsView(generics.RetrieveUpdateDestroyAPIView):
    queryset = MenuItem.objects.all()
    serializer_class = MenuItemSerializer
    def get_permissions(self):
        permission_classes = []
        if self.request.method != 'GET':
            permission_classes = [IsAuthenticated,IsManager | IsAdminUser]

        return [permission() for permission in permission_classes]

class ManagerView(generics.ListCreateAPIView, generics.DestroyAPIView):
    manager_group = Group.objects.get(name='Managers')
    queryset = User.objects.filter(groups=manager_group)
    #queryset = User.objects.filter(groups__name='Managers')
    serializer_class = ManagerSerializer
    permission_classes = [IsManager|IsAdminUser]
    
    def post(self, request, *args, **kwargs):
        username = request.data['username']
        #user_exists = User.objects.filter(username=user_data.get('username'), email = user_data.get('email')).first()
        
        if username:
            user = get_object_or_404(User, username=username)
            managers = Group.objects.get(name='Managers')
            managers.user_set.add(user)
            
            return Response('User added to Managers group',status.HTTP_201_CREATED)
        return Response({"message":"Error"}, status.HTTP_400_BAD_REQUEST)

class SingleManagerView(generics.DestroyAPIView):
    manager_group = Group.objects.get(name='Managers')
    queryset = User.objects.filter(groups=manager_group)
    serializer_class = ManagerSerializer
    permission_classes = [IsManager|IsAdminUser]
    
class DeliverCrewView(generics.ListCreateAPIView, generics.DestroyAPIView):
    delivery_group = Group.objects.get(name='Delivery crew')
    queryset = User.objects.filter(groups=delivery_group)
    #queryset = User.objects.filter(groups__name='Managers')
    serializer_class = DeliveryCrewSerializer
    permission_classes = [IsManager|IsAdminUser]
    
    def post(self, request, *args, **kwargs):
        username = request.data['username']
        #user_exists = User.objects.filter(username=user_data.get('username'), email = user_data.get('email')).first()
        
        if username:
            user = get_object_or_404(User, username=username)
            delivery_group = Group.objects.get(name='Delivery crew')
            delivery_group.user_set.add(user)
            
            return Response('User added to Delivery crew',status.HTTP_201_CREATED)
        return Response({"message":"Error"}, status.HTTP_400_BAD_REQUEST)

class SingleDeliveryCrewView(generics.DestroyAPIView):
    deliverycrew_group = Group.objects.get(name='Delivery crew')
    queryset = User.objects.filter(groups=deliverycrew_group)
    serializer_class = DeliveryCrewSerializer
    permission_classes = [IsManager|IsAdminUser]
    
class CartView(generics.ListCreateAPIView, generics.DestroyAPIView):
    #queryset = Cart.objects.all().filter(user=self.request.user)
    #queryset = User.objects.filter(groups__name='Managers')
    serializer_class = CartSerializer
    permission_classes = [IsAuthenticated]
    #OrderItem.objects.all().delete()
    def get_queryset(self):
        return Cart.objects.all().filter(user=self.request.user)
    def destroy(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        queryset.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

class OrderView(generics.ListCreateAPIView):
    serializer_class = OrderSerializer
    queryset = Order.objects.all()
    #def get_queryset(self):
    #    return Cart.objects.all()
        
class SingleOrderItemView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Order.objects.all()
    serializer_class = OrderSerializer
    
    def get_queryset(self):
        return Cart.objects.all().filter(user=self.request.user)
    
    def delete(self,request, pk):
        queryset = Order.objects.get(pk=pk)
        print(queryset)
        queryset.delete()
        queryset = OrderItem.objects.get(order=self.request.user)
        queryset.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
    
    def get(self, request, pk):
        try:
            order = Order.objects.get(pk=pk)
        except Order.DoesNotExist:
            return Response({'error': 'Order not found'}, status=status.HTTP_404_NOT_FOUND)

        serializer = OrderSerializer(order)
        
        # Check if the 'user' field in the JSON matches the current user's id
        if serializer.data['user'] != request.user.username:
            return Response({'error': 'You are unauthorized to view this order'}, status=status.HTTP_401_UNAUTHORIZED)

        return Response(serializer.data, status=status.HTTP_200_OK)
    
'''
me
@api_view(['GET','POST','PUT','PATCH','DELETE'])
def menu_items(request):
    if request.method == 'GET':
        items = MenuItem.objects.select_related('category').all()
        category_name = request.query_params.get('category')
        to_price = request.query_params.get('to_price')
        search = request.query_params.get('search')
        ordering = request.query_params.get('ordering')
        perpage = request.query_params.get('perpage', default=2)
        page = request.query_params.get('page',default=1)
        if category_name:
            items = items.filter(category__title=category_name)
        if to_price:
            items = items.filter(price__lte=to_price)
        if search:
            items = items.filter(title__contains=search)
        if ordering:
            ordering_fields = ordering.split(',')
            items = items.order_by(*ordering_fields)
        
        paginator = Paginator(items, per_page=perpage)
        try:
            items = paginator.page(number=page)
        except EmptyPage:
            items = []
        serialized_item = MenuItemSerializer(items, many=True)
        return Response(serialized_item.data,status.HTTP_200_OK)
    else:
        if request.user.groups.filter(name='Manager').exists():
            serialized_item = MenuItemSerializer(data=request.data)
            serialized_item.is_valid(raise_exception=True)
            serialized_item.save()
            return Response(serialized_item.data, status.HTTP_201_CREATED)
        return Response("Only managers can Add items", status.HTTP_403_FORBIDDEN)

@api_view(['GET','POST','PUT','PATCH','DELETE'])
def single_item(request, id):
    if request.method == 'GET':
        item = get_object_or_404(MenuItem, pk=id)
        serialized_item = MenuItemSerializer(item)
        return Response(serialized_item.data)
    else:
        if request.user.groups.filter(name='Manager').exists():
            serialized_item = MenuItemSerializer(data=request.data)
            serialized_item.is_valid(raise_exception=True)
            serialized_item.save()
            return Response(serialized_item.data, status.HTTP_201_CREATED)
        return Response("Only managers can Add items", status.HTTP_403_FORBIDDEN)
'''
        

@api_view()
@permission_classes([IsAuthenticated])
def secret(request):
    return Response({'message':'Some Secret Message'})

@api_view()
@permission_classes([IsAuthenticated])
def manager_view(request):
    if request.user.groups.filter(name='Manager').exists():
        return Response({'message':'Only Managager Should See This'})
    else:
        return Response({'message': 'You are not authorized'})
    
@api_view()
@throttle_classes([AnonRateThrottle])
def throttle_check(request):
    return Response({'message':'successful'})

@api_view()
@permission_classes([IsAuthenticated])
@throttle_classes([TenCallsPerMinute])
def throttle_check_auth(request):
    return Response({'message':'successful'})

'''
class MenuItemsView(generics.ListCreateAPIView):
    queryset = MenuItem.objects.all()
    serializer_class = MenuItemSerializer
    
class SingleMenuItemsView(generics.RetrieveAPIView, generics.DestroyAPIView):
    queryset = MenuItem.objects.all()
    serializer_class = MenuItemSerializer'''
