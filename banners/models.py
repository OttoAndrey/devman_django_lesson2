from django.db import models
from django.urls import reverse


class Banner(models.Model):
    title = models.CharField('название', max_length=50)
    image = models.ImageField('изображение')
    slug = models.SlugField('слаг', unique=True, help_text="часть ссылки")
    active = models.BooleanField('активный', default=False, db_index=True)
    text = models.TextField('текст', blank=True)
    position = models.PositiveIntegerField('позиция', default=0)

    def get_absolute_url(self):
        return reverse('banner_detail', kwargs={'slug': self.slug})

    def __str__(self):
        return self.title

    class Meta:
        ordering = ['position']
        verbose_name = 'баннер'
        verbose_name_plural = 'баннеры'
