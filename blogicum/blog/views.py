from django.contrib.auth import get_user_model
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.paginator import Paginator
from django.db.models import Count
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse, reverse_lazy
from django.utils import timezone
from django.views.generic import (CreateView, DeleteView, DetailView, ListView,
                                  UpdateView)

from blog.models import Category, Comment, Post

from .forms import CommentForm, PostForm, UserForm

POSTS_TO_SHOW = 10

User = get_user_model()


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


class PostListView(ListView):
    """Главная страница проекта.
    На ней расположен список всех постов.
    """

    model = Post
    queryset = get_post().annotate(comment_count=Count('comments'))
    ordering = '-pub_date'
    paginate_by = POSTS_TO_SHOW


def category_posts(request, category_slug):
    """Страница конкретной категории."""
    category = get_object_or_404(
        Category,
        slug=category_slug,
        is_published=True
    )
    post_list = get_post().filter(category=category,)
    paginator = Paginator(post_list, POSTS_TO_SHOW)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    context = {
        'category': category,
        'page_obj': page_obj
    }
    return render(request, 'blog/category.html', context)


def profile(request, username):
    """Страница конкретного пользователя. """
    profile = get_object_or_404(User, username=username)
    if request.user == profile:
        post_list = Post.objects.select_related(
            'category',
            'location',
            'author'
        ).filter(
            author=profile
        ).annotate(comment_count=Count('comments')).order_by(
            '-pub_date'
        )
    else:
        post_list = get_post().filter(
            author=profile
        ).annotate(comment_count=Count('comments')).order_by(
            '-pub_date'
        )
    paginator = Paginator(post_list, POSTS_TO_SHOW)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    context = {
        'profile': profile,
        'page_obj': page_obj
    }
    return render(request, 'blog/profile.html', context)


@login_required
def edit_profile(request):
    """Страница редактирования пользователя. """
    instance = get_object_or_404(User, username=request.user)
    form = UserForm(request.POST or None, instance=instance)
    context = {'form': form}
    if form.is_valid():
        form.save()
    return render(request, 'blog/user.html', context)


class PostDetailView(DetailView):
    """Страница конкретного поста. """

    post_obj = None
    model = Post
    pk_url_kwarg = 'post_id'

    def dispatch(self, request, *args, **kwargs):
        self.post_obj = get_object_or_404(
            Post,
            pk=kwargs['post_id']
        )
        if (self.post_obj.author != self.request.user):
            self.post_obj = get_object_or_404(
                get_post(),
                pk=kwargs['post_id'],

            )
        return super().dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['form'] = CommentForm()
        context['comments'] = (
            self.object.comments.select_related('author')
        )
        return context


class PostCreateView(LoginRequiredMixin, CreateView):
    """Страница создания поста. """

    model = Post
    form_class = PostForm

    def form_valid(self, form):
        form.instance.author = self.request.user
        return super().form_valid(form)

    def get_success_url(self):
        return reverse('blog:profile', kwargs={'username': self.request.user})


class PostUpdateView(UpdateView):
    """Страница редактирования поста. """

    post_obj = None
    model = Post
    form_class = PostForm
    pk_url_kwarg = 'post_id'
    template_name = 'blog/post_form.html'

    def dispatch(self, request, *args, **kwargs):
        self.post_obj = get_object_or_404(
                Post,
                pk=kwargs['post_id']
            )
        if (self.request.user == self.post_obj.author
           and not request.user.is_anonymous):
            return super().dispatch(request, *args, **kwargs)
        return redirect('blog:post_detail', post_id=kwargs['post_id'])

    def get_success_url(self) -> str:
        return reverse('blog:post_detail',
                       kwargs={'post_id': self.post_obj.pk})


class PostDeleteView(LoginRequiredMixin, DeleteView):
    """Страница удаления поста. """

    post_obj = None
    model = Post
    pk_url_kwarg = 'post_id'
    template_name = 'blog/post_form.html'
    success_url = reverse_lazy('blog:index')

    def dispatch(self, request, *args, **kwargs):
        self.post_obj = get_object_or_404(
                Post,
                pk=kwargs['post_id']
            )
        if (self.request.user == self.post_obj.author
           and not request.user.is_anonymous):
            return super().dispatch(request, *args, **kwargs)
        return redirect('blog:post_detail', post_id=kwargs['post_id'])


class CommentCreateView(LoginRequiredMixin, CreateView):
    """Страница создания комментария. """

    post_obj = None
    model = Comment
    form_class = CommentForm
    pk_url_kwarg = 'post_id'

    def dispatch(self, request, *args, **kwargs):
        self.post_obj = get_object_or_404(
            Post,
            pk=kwargs['post_id']
        )
        return super().dispatch(request, *args, **kwargs)

    def form_valid(self, form):
        form.instance.author = self.request.user
        form.instance.post = self.post_obj
        return super().form_valid(form)

    def get_success_url(self) -> str:
        return reverse('blog:post_detail',
                       kwargs={'post_id': self.post_obj.pk})


class CommentUpdateView(LoginRequiredMixin, UpdateView):
    """Страница редактирования комментария. """

    comment_obj = None
    model = Comment
    form_class = CommentForm
    pk_url_kwarg = 'comment_id'
    template_name = 'blog/post_form.html'

    def dispatch(self, request, *args, **kwargs):
        self.comment_obj = get_object_or_404(
                Comment,
                pk=kwargs['comment_id']
            )
        if (self.request.user == self.comment_obj.author
           and not request.user.is_anonymous):
            return super().dispatch(request, *args, **kwargs)
        return redirect('blog:post_detail', post_id=kwargs['post_id'])

    def get_success_url(self) -> str:
        return reverse('blog:post_detail',
                       kwargs={'post_id': self.comment_obj.post.pk})


class CommentDeleteView(LoginRequiredMixin, DeleteView):
    """Страница удаления комментария. """

    post_obj = None
    model = Comment
    pk_url_kwarg = 'comment_id'
    template_name = 'blog/comment_form.html'

    def dispatch(self, request, *args, **kwargs):
        self.comment_obj = get_object_or_404(
                Comment,
                pk=kwargs['comment_id']
            )
        if (self.request.user == self.comment_obj.author
           and not request.user.is_anonymous):
            return super().dispatch(request, *args, **kwargs)
        return redirect('blog:post_detail', post_id=kwargs['post_id'])

    def get_success_url(self) -> str:
        return reverse('blog:post_detail',
                       kwargs={'post_id': self.comment_obj.post.pk})
