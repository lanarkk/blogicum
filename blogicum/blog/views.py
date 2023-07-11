from django.shortcuts import get_object_or_404, render
from django.utils import timezone

from blog.models import Category, Post


POSTS_TO_SHOW = 5


def get_post():
    return (
        Post.objects.select_related(
            'category',
            'location',
            'author'
        ).filter(
            pub_date__lte=timezone.now(),
            is_published=True,
            category__is_published=True
        )
    )


def index(request):
    """Главная страница Блогикума."""
    post_list = get_post()[:POSTS_TO_SHOW]
    context = {'post_list': post_list}
    return render(request, 'blog/index.html', context)


def post_detail(request, post_id):
    """Страница конкретного блога."""
    post = get_object_or_404(
        get_post(),
        pk=post_id
    )
    context = {'post': post}
    return render(request, 'blog/detail.html', context)


def category_posts(request, category_slug):
    """Страница конкретной категории."""
    category = get_object_or_404(
        Category,
        slug=category_slug,
        is_published=True
    )
    post_list = get_post().filter(category=category,)
    context = {
        'category': category,
        'post_list': post_list
    }
    return render(request, 'blog/category.html', context)
