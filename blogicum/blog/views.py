# from django.contrib.auth.decorators import login_required
# from django.contrib.auth.models import User
# from django.shortcuts import get_object_or_404, render

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


def posts_filter():
    return Post.objects.select_related(
        'author', 'location', 'category',).filter(
        pub_date__lte=timezone.now(),
        is_published=True,
        category__is_published=True,).annotate(
        comment_count=Count('comments')).order_by('-pub_date')


class PostListView(ListView):
    model = Post
    template_name = 'blog/index.html'
    paginate_by = 10

    def get_queryset(self):
        return posts_filter()


class PostCreateView(LoginRequiredMixin, CreateView):
    model = Post
    template_name = 'blog/create.html'
    form_class = PostForm

    def form_valid(self, form):
        form.instance.author = self.request.user
        return super().form_valid(form)

    def get_success_url(self) -> str:
        return reverse(
            'blog:profile',
            kwargs={'username': self.request.user}
        )


class PostDetailView(DetailView):
    model = Post
    template_name = 'blog/detail.html'
    # pk_url_kwarg = 'post_id'

    # def dispatch(self, request, *args, **kwargs):
    #     get_object_or_404(Post, pk=kwargs['pk'], author=request.user)
    #     return super().dispatch(request, *args, **kwargs)

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


class PostUpdateView(LoginRequiredMixin, UpdateView):
    model = Post
    template_name = 'blog/create.html'
    form_class = PostForm
    # pk_url_kwarg = 'post_id'

    def dispatch(self, request, *args, **kwargs):
        # self.posts = get_object_or_404(Post, pk=kwargs.get('post_id'))
        if self.get_object().author != request.user:
            return redirect(
                'blog:post_detail',
                pk=self.kwargs['pk']
            )
        return super().dispatch(request, *args, **kwargs)

    # def form_valid(self, form):
    #     form.instance.author = self.request.user
    #     return super().form_valid(form)

    def get_success_url(self):
        return reverse(
            'blog:post_detail',
            kwargs={'pk': self.kwargs['pk']}
        )


class PostDeleteView(LoginRequiredMixin, DeleteView):
    form_class = PostForm
    model = Post
    template_name = 'blog/create.html'
    instance = None
    form = None
    # pk_url_kwarg = 'post_id'

    def dispatch(self, request, *args, **kwargs):
        if self.get_object().author != request.user:
            return redirect(
                'blog:post_detail',
                pk=self.kwargs['pk']
            )
        return super().dispatch(request, *args, **kwargs)

    # def dispatch(self, request, *args, **kwargs):
    #     self.instance = get_object_or_404(Post, id=kwargs['pk'])
    #     self.form = PostForm(request.POST or None, instance=self.instance)
    #     return super().dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['form'] = self.form_class
        return context

    # def get_context_data(self, **kwargs):
    #     context = super(PostDeleteView, self).get_context_data(**kwargs)
    #     context['form'] = self.form_class(instance=self.object)
    #     return context

    def get_success_url(self):
        return reverse(
            'blog:profile',
            kwargs={'username': self.request.user}
        )


class ProfileListView(ListView):
    template_name = 'blog/profile.html'
    paginate_by = 10

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


class ProfileEditUpdateView(LoginRequiredMixin, UpdateView):
    model = User
    template_name = 'blog/user.html'
    # form_class = ProfileForm
    # fields = '__all__'
    fields = ('username', 'first_name', 'last_name', 'email',)
    # slug_field = 'username'
    # slug_url_kwarg = 'username'

    def get_object(self):
        return self.request.user

    # def dispatch(self, request, *args, **kwargs):
    #     get_object_or_404(User, pk=request.user.id)
    #     return super().dispatch(request, *args, **kwargs)

    # def get_context_data(self, *args, **kwargs):
    #     context = super().get_context_data(*args, **kwargs)
    #     context['profile'] = self.author
    #     return context

    def get_success_url(self):
        return reverse(
            'blog:profile',
            kwargs={'username': self.request.user})


class CategoryPostListlView(ListView):
    model = Post
    template_name = 'blog/category.html'
    paginate_by = 10

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


class CommentCreateView(LoginRequiredMixin, CreateView):
    model = Comment
    template_name = 'blog/comment.html'
    form_class = CommentForm
    ordering = '-created_at'

    def form_valid(self, form):
        form.instance.author = self.request.user
        form.instance.post = get_object_or_404(Post, pk=self.kwargs['post_id'])
        return super().form_valid(form)

    def get_success_url(self):
        return reverse(
            'blog:post_detail',
            kwargs={'pk': self.kwargs['post_id']}
        )


class CommentUpdateView(LoginRequiredMixin, UpdateView):
    model = Comment
    template_name = 'blog/comment.html'
    form_class = CommentForm
    pk_url_kwarg = 'comment_id'

    # def dispatch(self, request, *args, **kwargs):
    #     get_object_or_404(Post, pk=kwargs['post_id'], author=request.user)
    #     return super().dispatch(request, *args, **kwargs)

    def dispatch(self, request, *args, **kwargs):
        # self.posts = get_object_or_404(Post, pk=kwargs.get('post_id'))
        if self.get_object().author != request.user:
            return redirect(
                'blog:post_detail',
                pk=self.kwargs['post_id']
            )
        return super().dispatch(request, *args, **kwargs)

    def get_success_url(self):
        return reverse(
            'blog:post_detail',
            kwargs={'pk': self.kwargs['post_id']}
        )


class CommentDeleteView(LoginRequiredMixin, DeleteView):
    model = Comment
    template_name = 'blog/comment.html'
    pk_url_kwarg = 'comment_id'

    # def dispatch(self, request, *args, **kwargs):
    #     get_object_or_404(Post, pk=kwargs['post_id'], author=request.user)
    #     return super().dispatch(request, *args, **kwargs)

    def dispatch(self, request, *args, **kwargs):
        # self.posts = get_object_or_404(Post, pk=kwargs.get('post_id'))
        if self.get_object().author != request.user:
            return redirect(
                'blog:post_detail',
                pk=self.kwargs['post_id']
            )
        return super().dispatch(request, *args, **kwargs)

    def get_success_url(self):
        return reverse(
            'blog:post_detail',
            kwargs={'pk': self.kwargs['post_id']}
        )
