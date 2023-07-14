from django.core.paginator import Paginator
from django.db.models import Count
from django.utils import timezone

from blog.models import Post

POSTS_TO_SHOW = 10


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


def comment_count(get_obj):
    return get_obj.annotate(comment_count=Count('comments'))


def paginating(request, post_list):
    paginator = Paginator(post_list, POSTS_TO_SHOW)
    page_number = request.GET.get('page')
    return paginator.get_page(page_number)
