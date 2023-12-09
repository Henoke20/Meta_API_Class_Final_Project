from rest_framework import serializers
from .models import MenuItem
from decimal import Decimal
from .models import Category , Cart , Order, OrderItem
from django.contrib.auth.models import User
from datetime import date

#class MenuItemSerializer(serializers.Serializer):
#    id = serializers.IntegerField()
#    title = serializers.CharField(max_length=255)
#    price = serializers.DecimalField(max_digits=6, decimal_places=2)
#    inventory = serializers.IntegerField()

class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ['id','slug','title']

class MenuItemSerializer(serializers.ModelSerializer):
    #category = CategorySerializer(read_only=True)
    class Meta:
        model = MenuItem
        fields = ['id','title','price','featured','category',]

class ManagerSerializer(serializers.ModelSerializer):
    class Meta():
        model = User
        fields = ['id','username','email']      
 
class DeliveryCrewSerializer(serializers.ModelSerializer):
    class Meta():
        model = User
        fields = ['id','username','email']      



class CartSerializer(serializers.ModelSerializer):
    user = serializers.SerializerMethodField()
    
    class Meta:
        model = Cart
        fields = ['id','user','menuitem','quantity','unit_price','price']
        read_only_fields = ['user','unit_price','price']
    def get_user(self, obj): 
        return obj.user.username 
    
    def create(self, validated_data):
        print(validated_data)
        # Extract the associated MenuItem instance from the validated data
        menuitem_instance = validated_data['menuitem']
        validated_data['user'] = self.context['request'].user
        # Calculate the price based on the associated MenuItem's price and quantity
        unit_price = menuitem_instance.price
        validated_data['unit_price'] = unit_price
        validated_data['price'] = unit_price * validated_data['quantity']
        # Continue with the regular creation process
        return super().create(validated_data)


class OrderSerializer(serializers.ModelSerializer):
    user = serializers.SerializerMethodField()
    class Meta:
        model = Order
        fields = '__all__'
        read_only_fields = ['user','total']
    def get_user(self, obj): 
        return obj.user.username
    def create(self, validated_data):
        user = self.context['request'].user
        cart_items = Cart.objects.filter(user = user)
        total = sum(cart_item.price for cart_item in cart_items)
        print(total)
                
        
        for cart_item in cart_items:
            OrderItem.objects.create(
                order = user,
                menuitem = cart_item.menuitem,
                quantity = cart_item.quantity,
                unit_price = cart_item.unit_price,
                price = cart_item.price,
            )
            #total+=cart_item.price
        
        
        Cart.objects.filter(user = self.context['request'].user).delete()
        return super().create(validated_data)

    
    
        


    
class OrderItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = OrderItem
        fields = ['id','order','menuitem','quantity','unit_price','price']
        read_only_fields = ['order','unit_price','price']
    
    
    def create(self, validated_data):
        print(validated_data)
        # Extract the associated MenuItem instance from the validated data
        menuitem_instance = validated_data['menuitem']
        #validated_data['user'] = self.context['request'].user
        # Calculate the price based on the associated MenuItem's price and quantity
        unit_price = menuitem_instance.price
        validated_data['unit_price'] = unit_price
        validated_data['price'] = unit_price * validated_data['quantity']
        # Continue with the regular creation process
        return super().create(validated_data)

