from django.urls import path
from . import views

urlpatterns = [
    path('robots.txt', views.robots_txt, name='robots_txt'),
    path('', views.product_list, name='product_list'),
    path('login/', views.login_view, name='login'),
    path('register/', views.register_view, name='register'),
    path('logout/', views.logout_view, name='logout'),

    # Compras del cliente
    path('comprar/<str:product_id>/', views.comprar, name='comprar'),
    path('mis-pedidos/', views.mis_pedidos, name='mis_pedidos'),
    path('mis-pedidos/<str:order_id>/estado/', views.pedido_estado, name='pedido_estado'),

    # Dashboard CRUD (solo rol admin)
    path('dashboard/', views.dashboard, name='dashboard'),
    path('dashboard/productos/nuevo/', views.product_create, name='product_create'),
    path('dashboard/productos/<str:product_id>/editar/', views.product_update, name='product_update'),
    path('dashboard/productos/<str:product_id>/eliminar/', views.product_delete, name='product_delete'),
]
