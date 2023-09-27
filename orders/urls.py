from django.urls import path

from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('porentregar/', views.to_deliver_balance, name='to_deliver'),
    path('entreagdo/', views.delivered_balance, name='delivered'),
    path('pedido/form/', views.order_form, name='order_form'),
    path('pedido/procesar/', views.process_new_order, name='process_order'),
    path('pedido/editar/<int:id>/', views.edit_order_form, name='edit_order_form'),
    path('pedido/mutar/<int:id>/', views.process_order_edit, name='process_edit'),
    path('pedido/eliminar/<int:id>/', views.delete_order, name='delete_order'),
    path('pedido/detalle/<int:id>/', views.order_detail, name='order_detail'),
    path('pedido/entregado/<int:id>/',
         views.order_delivered, name='order_delivered'),
    path('clientes/', views.customers, name='customers'),
    path('clientes/agregar/', views.customer_form, name='client_form'),
    path('clientes/procesar/', views.process_new_customer, name='process_customer'),
    path('clientes/editar/<int:id>/',
         views.customer_edit_form, name='customer_edit_form'),
    path('clientes/mutar/<int:id>/', views.customer_edit_process,
         name='customer_edit_process'),
    path('clientes/eliminar/<int:id>/',
         views.delete_customer, name='delete_customer'),
    path('productos/', views.products, name='products'),
    path('productos/agregar/', views.product_form, name='product_form'),
    path('productos/procesar/', views.process_new_product, name='process_product'),
    path('productos/editar/<int:id>',
         views.product_edit_form, name='product_edit_form'),
    path('productos/mutar/<int:id>', views.product_edit_process,
         name='product_edit_process'),
    path('productos/eliminar/<int:id>',
         views.delete_product, name='delete_product')
]
