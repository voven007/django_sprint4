from .forms import PostForm, CommentForm
from blog.models import Post, Category, Comment, User
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Count
from django.http import Http404
from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse
from django.utils import timezone
from django.views.generic import (
    CreateView, DetailView, ListView, DeleteView, UpdateView)

PAGIATE_OF_PAGES = 10


def posts_filter():
    return Post.objects.select_related(
        'author', 'location', 'category',).filter(
        pub_date__lte=timezone.now(),
        is_published=True,
        category__is_published=True,).annotate(
        comment_count=Count('comments')).order_by('-pub_date')


class ActionPostMixin(LoginRequiredMixin):
    def dispatch(self, request, *args, **kwargs):
        if self.get_object().author != request.user:
            return redirect(
                'blog:post_detail',
                pk=self.kwargs['pk']
            )
        return super().dispatch(request, *args, **kwargs)


class ActionCommentMixin(LoginRequiredMixin):
    def dispatch(self, request, *args, **kwargs):
        if self.get_object().author != request.user:
            return redirect(
                'blog:post_detail',
                pk=self.kwargs['post_id']
            )
        return super().dispatch(request, *args, **kwargs)


class RedirectionProfileMixin:
    def get_success_url(self):
        return reverse(
            'blog:profile',
            kwargs={'username': self.request.user}
        )


class RedirectionPostMixin:
    def get_success_url(self):
        return reverse(
            'blog:post_detail',
            kwargs={'pk': self.kwargs['pk']}
        )


class RedirectionCommentPostMixin:
    def get_success_url(self):
        return reverse(
            'blog:post_detail',
            kwargs={'pk': self.kwargs['post_id']}
        )


class CommentBaseMixin(RedirectionCommentPostMixin):
    model = Comment
    template_name = 'blog/comment.html'
    pk_url_kwarg = 'comment_id'


class CommentFormMixin(CommentBaseMixin):
    form_class = CommentForm


class PostListView(ListView):
    model = Post
    template_name = 'blog/index.html'
    paginate_by = PAGIATE_OF_PAGES

    def get_queryset(self):
        return posts_filter()


class PostCreateView(
    LoginRequiredMixin,
    RedirectionProfileMixin,
    CreateView,
):
    model = Post
    template_name = 'blog/create.html'
    form_class = PostForm

    def form_valid(self, form):
        form.instance.author = self.request.user
        return super().form_valid(form)


class PostDetailView(DetailView):
    model = Post
    template_name = 'blog/detail.html'

    def get_object(self, queryset=None):
        post = super().get_object(queryset)
        if post.author != self.request.user and (
            post.is_published is False
            or post.category.is_published is False
            or post.pub_date > timezone.now()
        ):
            raise Http404
        return post

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['form'] = CommentForm()
        context['comments'] = self.object.comments.select_related(
            'author'
        )
        return context


class PostUpdateView(
    ActionPostMixin,
    RedirectionPostMixin,
    UpdateView,
):
    model = Post
    template_name = 'blog/create.html'
    form_class = PostForm


class PostDeleteView(
    ActionPostMixin,
    RedirectionProfileMixin,
    DeleteView,
):
    form_class = PostForm
    model = Post
    template_name = 'blog/create.html'
    instance = None
    form = None

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['form'] = self.form_class(instance=self.object)
        return context


class ProfileListView(ListView):
    template_name = 'blog/profile.html'
    paginate_by = PAGIATE_OF_PAGES

    def get_queryset(self):
        self.author = get_object_or_404(
            User,
            username=self.kwargs['username']
        )
        if self.request.user == self.author:
            return Post.objects.select_related(
            ).filter(
                author=self.author
            ).annotate(
                comment_count=Count('comments')
            ).order_by('-pub_date')
        return Post.objects.select_related(
        ).filter(
            pub_date__lte=timezone.now(),
            is_published=True,
        ).annotate(
            comment_count=Count('comments')
        ).order_by('-pub_date')

    def get_context_data(self, *args, **kwargs):
        context = super().get_context_data(*args, **kwargs)
        context['profile'] = self.author
        return context


class ProfileEditUpdateView(
    LoginRequiredMixin,
    RedirectionProfileMixin,
    UpdateView,
):
    model = User
    template_name = 'blog/user.html'
    fields = ('username', 'first_name', 'last_name', 'email',)

    def get_object(self):
        return self.request.user


class CategoryPostListlView(ListView):
    model = Post
    template_name = 'blog/category.html'
    paginate_by = PAGIATE_OF_PAGES

    def get_queryset(self):
        return posts_filter().filter(
            category__slug=self.kwargs['category_slug'],
        )

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['category'] = get_object_or_404(
            Category,
            is_published=True,
            slug=self.kwargs['category_slug'],
        )
        return context


class CommentCreateView(
    LoginRequiredMixin,
    CommentFormMixin,
    CreateView,
):
    pass

    def form_valid(self, form):
        form.instance.author = self.request.user
        form.instance.post = get_object_or_404(Post, pk=self.kwargs['post_id'])
        return super().form_valid(form)


class CommentUpdateView(
    ActionCommentMixin,
    CommentFormMixin,
    UpdateView,
):
    pass


class CommentDeleteView(
    ActionCommentMixin,
    CommentBaseMixin,
    DeleteView,
):
    pass
