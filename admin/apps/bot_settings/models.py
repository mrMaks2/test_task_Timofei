from django.db import models

class Channel(models.Model):
    chat_id = models.CharField(max_length=200, unique=True, verbose_name='ID канала или @username')
    title = models.CharField(max_length=300, blank=True, verbose_name='Название')
    is_mandatory = models.BooleanField(default=True, verbose_name='Обязательная подписка')

    class Meta:
        verbose_name = 'Канал для подписки'
        verbose_name_plural = 'Каналы для подписки'

    def __str__(self):
        return self.title or self.chat_id

class Setting(models.Model):
    key = models.CharField(max_length=100, unique=True)
    value = models.TextField()

    class Meta:
        verbose_name = 'Настройка'
        verbose_name_plural = 'Настройки'

    def __str__(self):
        return self.key