from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone

class Service(models.Model):
    name = models.CharField(max_length=200, verbose_name="Название услуги")
    picture = models.ImageField(upload_to='services/', blank=True, null=True, verbose_name="Изображение")
    price = models.IntegerField(verbose_name="Цена")
    description = models.TextField(verbose_name="Описание")

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = 'Услуга'
        verbose_name_plural = 'Услуги'

class Rating(models.Model):
    name = models.CharField(max_length=100, verbose_name="Название рейтинга")
    value = models.FloatField(choices=[(i * 0.5, f"{i * 0.5}") for i in range(2, 11)], verbose_name="Значение")

    def __str__(self):
        return f"{self.name}: {self.value}"

    class Meta:
        verbose_name = 'Рейтинг'
        verbose_name_plural = 'Рейтинги'

class Review(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name="Пользователь")
    service = models.ForeignKey(Service, on_delete=models.CASCADE, verbose_name="Услуга")
    rating = models.ForeignKey(Rating, on_delete=models.CASCADE, verbose_name="Оценка")
    date = models.DateField(auto_now_add=True, verbose_name="Дата отзыва")
    description = models.TextField(blank=True, null=True, verbose_name="Текст отзыва")

    def __str__(self):
        return f"{self.user.username} - {self.service.name} - {self.rating.value}"

    class Meta:
        ordering = ['-date']
        verbose_name = 'Отзыв'
        verbose_name_plural = 'Отзывы'

class Order(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Ожидает обработки'),
        ('confirmed', 'Подтвержден'),
        ('in_progress', 'В работе'),
        ('completed', 'Завершен'),
        ('cancelled', 'Отменен')
    ]
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name="Пользователь")
    services = models.ManyToManyField(Service, verbose_name="Услуги")
    address = models.TextField(verbose_name="Адрес доставки")
    total_cost = models.IntegerField(verbose_name="Общая стоимость")
    created_at = models.DateTimeField(default=timezone.now, verbose_name="Дата создания")
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='pending',
        verbose_name="Статус заказа"
    )

    def __str__(self):
        try:
            return f"Заказ #{self.id} - {self.user.username}"
        except:
            return f"Заказ #{self.id}"

    class Meta:
        verbose_name = 'Заказ'
        verbose_name_plural = 'Заказы'
        ordering = ['-created_at']