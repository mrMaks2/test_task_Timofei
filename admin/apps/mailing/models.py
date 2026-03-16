from django.db import models

class Mailing(models.Model):
    STATUS_CHOICES = [
        ('draft', 'Черновик'),
        ('ready', 'Готово'),
        ('sending', 'Отправляется'),
        ('sent', 'Отправлено'),
    ]
    text = models.TextField()
    image = models.ImageField(upload_to='mailings/', blank=True, null=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='draft')
    created_at = models.DateTimeField(auto_now_add=True)
    sent_at = models.DateTimeField(null=True, blank=True)
    total_count = models.IntegerField(default=0)
    success_count = models.IntegerField(default=0)
    error_count = models.IntegerField(default=0)

    class Meta:
        verbose_name = 'Рассылка'
        verbose_name_plural = 'Рассылки'

    def __str__(self):
        return f"Рассылка #{self.id} - {self.status}"

class MailingLog(models.Model):
    mailing = models.ForeignKey(Mailing, on_delete=models.CASCADE, related_name='logs')
    user = models.ForeignKey('customers.Customer', on_delete=models.CASCADE)
    status = models.CharField(max_length=20)  # success / error
    error_message = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'Лог рассылки'
        verbose_name_plural = 'Логи рассылок'