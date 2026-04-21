from django.urls import path
from . import views
from django.contrib.auth import views as auth_views
from .views import register

urlpatterns = [
    path('', views.home, name='home'),
    path('events/', views.event_list, name='event_list'),
    path('register/<int:event_id>/', views.register_event, name='register_event'),
    path('payment/<int:event_id>/', views.payment_page, name='payment'),
    path('payment-success/<int:event_id>/', views.payment_success, name='payment_success'),
    path('login/', auth_views.LoginView.as_view(
        template_name='events/login.html'
    ), name='login'),
    path('logout/', auth_views.LogoutView.as_view(), name='logout'),
    path('register/', register, name='register'),
    path('dashboard/', views.dashboard, name='dashboard'),
    path('unregister/<int:event_id>/', views.unregister_event, name='unregister_event'),
    path('logout/', views.custom_logout, name='logout'),
    path('ticket/<int:event_id>/', views.ticket_view, name='ticket'),
    path('qr/<int:event_id>/', views.generate_qr, name='qr'),
]