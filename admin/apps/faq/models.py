from django.db import models

class FAQ(models.Model):
    question = models.TextField()
    answer = models.TextField()
    is_active = models.BooleanField(default=True)
    order = models.IntegerField(default=0)

    class Meta:
        verbose_name = 'Вопрос-ответ'
        verbose_name_plural = 'Вопросы-ответы'
        ordering = ['order']

    def __str__(self):
        return self.question[:50]