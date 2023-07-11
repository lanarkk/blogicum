from django.contrib import admin

from .models import Category, Location, Post


@admin.register(Post)
class PostAdmin(admin.ModelAdmin):
    """Модель Пост в админ зоне.
    Описывает ее внешний вид и функционал."""

    list_display = (
        'title',
        'text',
        'is_published',
        'created_at',
        'pub_date',
        'author',
        'location',
        'category'
    )
    list_display_links = (
        'title',
        'text',
        'location',
        'category',
        'pub_date',
    )
    list_editable = (
        'is_published',
    )


@admin.register(Location)
class LocationAdmin(admin.ModelAdmin):
    """Модель Локация в админ зоне.
    Описывает ее внешний вид и функционал."""

    list_display = (
        'name',
        'is_published',
        'created_at'
    )
    list_editable = (
        'is_published',
    )


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    """Модель Категория в админ зоне.
    Описывает ее внешний вид и функционал."""

    list_display = (
        'title',
        'description',
        'slug',
        'is_published',
        'created_at'
    )
    list_display_links = (
        'title',
        'description',
        'slug',
    )
    list_editable = (
        'is_published',
    )


admin.site.empty_value_display = 'Не задано'
