from django.contrib.auth import get_user_model
from django.db import models


User = get_user_model()


class PublishedModel(models.Model):
    is_published = models.BooleanField(
        default=True,
        verbose_name='Опубликовано',
        help_text='Снимите галочку, чтобы скрыть публикацию.',
        blank=False
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Добавлено',
        blank=False
    )

    class Meta:
        abstract = True


class Category(PublishedModel):
    title = models.CharField(
        max_length=256,
        verbose_name='Заголовок',
        blank=False
    )
    description = models.TextField(verbose_name='Описание', blank=False)
    slug = slug = models.SlugField(
        unique=True,
        verbose_name='Идентификатор',
        help_text='Идентификатор страницы для URL; '
                  'разрешены символы латиницы, цифры, дефис и подчёркивание.',
        blank=False
    )

    class Meta:
        verbose_name = 'категория'
        verbose_name_plural = 'Категории'

    def __str__(self):
        return self.title[:30]


class Location(PublishedModel):
    name = models.CharField(
        max_length=256,
        verbose_name='Название места',
        blank=False
    )

    class Meta:
        verbose_name = 'местоположение'
        verbose_name_plural = 'Местоположения'

    def __str__(self):
        return self.name[:30]


class Post(PublishedModel):
    title = models.CharField(
        max_length=256,
        verbose_name='Заголовок',
        blank=False
    )
    text = models.TextField(verbose_name='Текст', blank=False)
    pub_date = models.DateTimeField(
        verbose_name='Дата и время публикации',
        help_text='Если установить дату и время в '
                  'будущем — можно делать отложенные публикации.',
        blank=False
    )
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        verbose_name='Автор публикации',
        related_name='posts',
        blank=False
    )
    location = models.ForeignKey(
        Location,
        on_delete=models.SET_NULL,
        null=True,
        verbose_name='Местоположение',
        related_name='posts'
    )
    category = models.ForeignKey(
        Category,
        on_delete=models.SET_NULL,
        null=True,
        verbose_name='Категория',
        blank=False,
        related_name='posts'
    )

    class Meta:
        verbose_name = 'публикация'
        verbose_name_plural = 'Публикации'
        ordering = ('-pub_date',)

    def __str__(self):
        return self.title[:30]


class Comment(models.Model):
    text = models.TextField('Текст комментария')
    comment = models.ForeignKey(
        Post,
        on_delete=models.CASCADE,
        related_name='comment',
    )
    created_at = models.DateTimeField(auto_now_add=True)
    author = models.ForeignKey(User, on_delete=models.CASCADE)

    class Meta:
        ordering = ('created_at',)
