from django.contrib.auth import get_user_model
from django.db import models

NUMBER_OF_LETTERS_VISIBLE = 21

User = get_user_model()


class PublishedModel(models.Model):
    """Абстрактная модель.
    Добвляет флаг is_published
    и дату время created_at."""

    is_published = models.BooleanField(
        'Опубликовано',
        default=True,
        help_text='Снимите галочку, чтобы скрыть публикацию.'
    )
    created_at = models.DateTimeField(
        'Добавлено',
        auto_now_add=True,
    )

    class Meta:
        abstract = True


class Category(PublishedModel):
    """Модель Категория. Создает в бд
    таблицу с категориями постов."""

    title = models.CharField('Заголовок', max_length=256)
    description = models.TextField('Описание')
    slug = models.SlugField(
        'Идентификатор',
        unique=True,
        help_text=(
            'Идентификатор страницы для URL; '
            'разрешены символы латиницы, цифры, '
            'дефис и подчёркивание.'
        )
    )

    class Meta:
        verbose_name = 'категория'
        verbose_name_plural = 'Категории'

    def __str__(self):
        return self.title[:NUMBER_OF_LETTERS_VISIBLE]


class Location(PublishedModel):
    """Модель Локация. Создает в бд
    таблицу с местоположениями."""

    name = models.CharField('Название места', max_length=256)

    class Meta:
        verbose_name = 'местоположение'
        verbose_name_plural = 'Местоположения'

    def __str__(self):
        return self.name[:NUMBER_OF_LETTERS_VISIBLE]


class Post(PublishedModel):
    """Модель Пост. Создает в бд
    таблицу с постами пользователей."""

    title = models.CharField('Заголовок', max_length=256)
    text = models.TextField('Текст')
    image = models.ImageField('Фото', upload_to='post_images', blank=True)
    pub_date = models.DateTimeField(
        'Дата и время публикации',
        help_text=(
            'Если установить дату и время в будущем '
            '— можно делать отложенные публикации.'
        ),
    )
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        verbose_name='Автор публикации',
    )
    location = models.ForeignKey(
        Location,
        on_delete=models.SET_NULL,
        verbose_name='Местоположение',
        null=True,
        blank=True,
    )
    category = models.ForeignKey(
        Category,
        on_delete=models.SET_NULL,
        null=True,
        verbose_name='Категория',
    )

    class Meta:
        verbose_name = 'публикация'
        verbose_name_plural = 'Публикации'
        default_related_name = "posts"
        ordering = ('-pub_date',)

    def __str__(self):
        return self.title[:NUMBER_OF_LETTERS_VISIBLE]


class Comment(PublishedModel):
    text = models.TextField('Текст комментария')
    post = models.ForeignKey(
        Post,
        on_delete=models.CASCADE,
        related_name='comments',
    )
    author = models.ForeignKey(User, on_delete=models.CASCADE)

    class Meta:
        ordering = ('created_at',)
        verbose_name = 'Поздравление'
        verbose_name_plural = 'Поздравления'

    def __str__(self):
        return self.text[:NUMBER_OF_LETTERS_VISIBLE]
