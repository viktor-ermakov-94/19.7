from django.db import models
from django.contrib.auth.models import User
from ckeditor.fields import RichTextField
from django.core.cache import cache


class Post(models.Model):
    TANK = 'TK'
    HEALER = 'HL'
    DAMAGE_DEALER = 'DD'
    TRADER = 'TD'
    GUILD_MASTER = 'GM'
    QUEST_GIVER = 'QG'
    BLACKSMITH = 'BS'
    TANNER = 'TN'
    POTION_MASTER = 'PM'
    SPELL_MASTER = 'SM'

    CATEGORIES = [
        (TANK, 'Танки'),
        (HEALER, 'Хилы'),
        (DAMAGE_DEALER, 'ДД'),
        (TRADER, 'Торговцы'),
        (GUILD_MASTER, 'Гилдмастеры'),
        (QUEST_GIVER, 'Квестгиверы'),
        (BLACKSMITH, 'Кузнецы'),
        (TANNER, 'Кожевники'),
        (POTION_MASTER, 'Зельевары'),
        (SPELL_MASTER, 'Мастера заклинаний'),
    ]

    title = models.CharField(max_length=128, verbose_name='Заголовок')
    author = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name='Автор')
    category = models.CharField(max_length=2, choices=CATEGORIES, default=TANK, verbose_name='Категория')
    content = RichTextField(verbose_name='Содержание объявления')
    dateCreation = models.DateTimeField(auto_now_add=True, verbose_name='Дата публикации')
    dateUpdate = models.DateTimeField(auto_now=True, verbose_name='Дата обновления')

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        return f'/{self.pk}'

    # D7.4.Кэширование на низком уровне (смотри еще view PostDetailView метод get_object)
    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)  # сначала вызываем метод родителя, чтобы объект сохранился
        cache.delete(f'post-{self.pk}')  # затем удаляем его из кэша, чтобы сбросить его


class Reply(models.Model):
    author = models.ForeignKey(User, on_delete=models.CASCADE)
    text = models.TextField(verbose_name='Как Вам статья?')
    post = models.ForeignKey(Post, on_delete=models.CASCADE, verbose_name='Объявление')
    dateCreation = models.DateTimeField(auto_now_add=True)
    accepted = models.BooleanField(default=False)

    def __str__(self):
        return f'{self.post} ==> {self.author}: {self.text}'

