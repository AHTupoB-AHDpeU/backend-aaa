from datetime import datetime
from django.urls import path, include
from django.contrib import admin
from django.contrib.auth.views import LoginView, LogoutView
from app import forms, views

from django.conf import settings
from django.conf.urls.static import static


urlpatterns = [
    path('admin/', admin.site.urls),
    path('', views.home, name='home'),
    path('contact/', views.contact, name='contact'),
    path('about/', views.about, name='about'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),

    # API routes
    path('api/register/', views.register_view, name='api_register'),
    path('api/login/', views.login_view, name='api_login'),
    path('api/logout/', views.logout_view, name='api_logout'),
    path('api/profile/', views.user_profile_view, name='api_profile'),
    path('api/services/', views.services_list, name='services_list'),
    path('api/reviews/', views.reviews_list, name='reviews_list'),
    path('api/reviews/create/', views.create_review, name='create_review'),
    path('api/ratings/', views.ratings_list, name='ratings_list'),
    path('api/orders/create/', views.create_order, name='create_order'),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
