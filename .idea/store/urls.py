from django.urls import path
from .views import index,signup,Login,logout,cart,checkout,orders,home

urlpatterns = [
path('',home,name='homepage'),
path('index',index,name='index'),
path('signup',signup),
path('login',Login.as_view(),name='login'),
path('logout',logout,name='logout'),
path('cart',cart,name='cart'),
path('checkout',checkout,name='checkout'),
path('orders',orders,name='order')

]
