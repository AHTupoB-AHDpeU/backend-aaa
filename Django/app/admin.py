from django.contrib import admin
from .models import Order, Service, Rating, Review

@admin.register(Service)
class ServiceAdmin(admin.ModelAdmin):
    list_display = ('name', 'price', 'id')
    search_fields = ('name', 'description')
    list_filter = ('price',)

@admin.register(Rating)
class RatingAdmin(admin.ModelAdmin):
    list_display = ('name', 'value', 'id')
    search_fields = ('name',)

@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    list_display = ('user', 'service', 'rating', 'date', 'id')
    list_filter = ('date', 'rating')
    search_fields = ('user__username', 'service__name', 'description')
    readonly_fields = ('date',)

@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ('id', 'get_user_info', 'total_cost', 'status', 'created_at', 'get_services_count')
    list_filter = ('status', 'created_at')
    search_fields = ('user__username', 'user__email', 'user__first_name', 'user__last_name', 'address')
    filter_horizontal = ('services',)
    readonly_fields = ('created_at',)
    
    def get_user_info(self, obj):
        user_info = f"{obj.user.username}"
        if obj.user.first_name or obj.user.last_name:
            user_info += f" ({obj.user.first_name} {obj.user.last_name})"
        if obj.user.email:
            user_info += f" - {obj.user.email}"
        return user_info
    get_user_info.short_description = 'Пользователь'
    
    def get_services_count(self, obj):
        return obj.services.count()
    get_services_count.short_description = 'Количество услуг'