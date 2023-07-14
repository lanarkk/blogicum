from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse, reverse_lazy
from django.views.generic import (CreateView, DeleteView, DetailView, ListView,
                                  UpdateView)
from django.views.generic.edit import FormMixin

from blog.models import Category, Comment, Post, User

from .forms import CommentForm, PostForm, UserForm
from .utils import comment_count, get_post, paginating

POSTS_TO_SHOW = 10


class CommentMixin:

    model = Comment
    pk_url_kwarg = 'comment_id'
    template_name = 'blog/comment_form.html'

    def dispatch(self, request, *args, **kwargs):
        if (self.request.user == self.get_object().author):
            return super().dispatch(request, *args, **kwargs)
        return redirect('blog:post_detail', post_id=kwargs['post_id'])

    def get_success_url(self) -> str:
        return reverse(
            'blog:post_detail',
            kwargs={'post_id': self.kwargs.get('post_id', None)}
        )


class PostMixin:

    model = Post
    pk_url_kwarg = 'post_id'
    template_name = 'blog/post_form.html'

    def dispatch(self, request, *args, **kwargs):
        if (self.request.user == self.get_object().author):
            return super().dispatch(request, *args, **kwargs)
        return redirect('blog:post_detail', self.get_object().pk)


class PostListView(ListView):
    """Главная страница проекта.
    На ней расположен список всех постов.
    """

    model = Post
    queryset = comment_count(get_post())
    ordering = '-pub_date'
    paginate_by = POSTS_TO_SHOW


def category_posts(request, category_slug):
    """Страница конкретной категории."""
    category = get_object_or_404(
        Category,
        slug=category_slug,
        is_published=True
    )
    post_list = comment_count(get_post()).filter(
        category=category,
    ).order_by(
        '-pub_date'
    )
    page_obj = paginating(request, post_list)
    context = {
        'category': category,
        'page_obj': page_obj
    }
    return render(request, 'blog/category.html', context)


def profile(request, username):
    """Страница конкретного пользователя. """
    profile = get_object_or_404(User, username=username)
    if request.user == profile:
        post_list = comment_count(
            Post.objects.select_related(
                'category',
                'location',
                'author'
            ).filter(author=profile)
        ).order_by(
            '-pub_date'
        )
    else:
        post_list = comment_count(get_post()).filter(
            author=profile
        ).order_by('-pub_date')
    page_obj = paginating(request, post_list)
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


class PostDetailView(FormMixin, DetailView):
    """Страница конкретного поста. """

    post_obj = None
    model = Post
    form_class = CommentForm
    pk_url_kwarg = 'post_id'

    def get_queryset(self, queryset=None):
        self.post_obj = get_object_or_404(
            Post,
            pk=self.kwargs.get(self.pk_url_kwarg, None)
        )
        if (self.post_obj.author != self.request.user):
            self.post_obj = get_object_or_404(
                get_post(),
                pk=self.kwargs.get(self.pk_url_kwarg, None),

            )
        return super().get_queryset()

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
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


class PostUpdateView(LoginRequiredMixin, PostMixin, UpdateView):
    """Страница редактирования поста. """

    raise_exception = False
    form_class = PostForm


class PostDeleteView(LoginRequiredMixin, PostMixin, DeleteView):
    """Страница удаления поста. """

    success_url = reverse_lazy('blog:index')


class CommentCreateView(LoginRequiredMixin, CreateView):
    """Страница создания комментария. """

    model = Comment
    form_class = CommentForm
    pk_url_kwarg = 'post_id'

    def form_valid(self, form):
        form.instance.author = self.request.user
        form.instance.post = get_object_or_404(
            Post,
            pk=self.kwargs.get(self.pk_url_kwarg, None)
        )
        return super().form_valid(form)

    def get_success_url(self) -> str:
        return reverse(
            'blog:post_detail',
            kwargs={'post_id': self.kwargs.get(self.pk_url_kwarg, None)}
        )


class CommentUpdateView(LoginRequiredMixin, CommentMixin, UpdateView):
    """Страница редактирования комментария. """

    form_class = CommentForm


class CommentDeleteView(LoginRequiredMixin, CommentMixin, DeleteView):
    """Страница удаления комментария. """

    pass
