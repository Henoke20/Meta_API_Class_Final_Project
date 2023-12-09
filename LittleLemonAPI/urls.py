from django.urls import path
from . import views
from rest_framework.authtoken.views import obtain_auth_token

urlpatterns = [
    path('menu-items', views.MenuItemsView.as_view()),
    #path('menu-items/', views.menu_items),
    #path('menu-items/<int:id>', views.single_item),
    path('secret/',views.secret),
    path('api-token-auth/', obtain_auth_token),
    path('groups/manager/users', views.ManagerView.as_view()),
    path('groups/manager/users/<int:pk>', views.SingleManagerView.as_view()),
    path('groups/delivery-crew/users', views.DeliverCrewView.as_view()),
    path('groups/delivery-crew/users/<int:pk>', views.SingleDeliveryCrewView.as_view()),
    path('orders', views.OrderView.as_view()),
    path('orders/<int:pk>', views.SingleOrderItemView.as_view()),
    path('cart/menu-items', views.CartView.as_view()),    
    path('throttle-check/', views.throttle_check),
    path('throttle-check-auth/', views.throttle_check_auth),
    path('menu-items/<int:pk>', views.SingleMenuItemsView.as_view()),
]