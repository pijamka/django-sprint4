from datetime import datetime

from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.core.paginator import Paginator
from django.db.models import Count
from django.shortcuts import get_object_or_404, render, redirect
from django.urls import reverse_lazy, reverse
from django.views.generic import (
    CreateView, DeleteView, DetailView, ListView, UpdateView,
)

from .models import Post, Category, Comment, User
from .forms import CommentForm, DeletionForm, PostForm, ProfileForm

POSTS_ON_THE_PAGE = 10
POSTS = Post.objects


def get_posts(queryset, skip_filter=None):
    default_filters = {
        'is_published': True,
        'category__is_published': True,
        'pub_date__lt': datetime.now()
    }
    if skip_filter:
        default_filters = {}
    return queryset.select_related(
        'category',
        'location',
        'author'
    ).filter(
        **default_filters
    ).annotate(
        comment_count=Count('comments')
    ).order_by(*queryset.model._meta.ordering)


def get_paginate(queryset, request):
    return Paginator(
        queryset,
        POSTS_ON_THE_PAGE
    ).get_page(request.GET.get('page'))


class IndexListView(ListView):
    model = Post
    paginate_by = POSTS_ON_THE_PAGE
    template_name = 'blog/index.html'
    queryset = get_posts(POSTS)


class PostDetailDetailView(DetailView):
    model = Post
    template_name = 'blog/detail.html'
    pk_url_kwarg = 'post_id'

    def get_object(self):
        post = super().get_object()
        if self.request.user == post.author:
            return post
        return super().get_object(
            self.get_queryset().filter(is_published=True)
        )

    def get_context_data(self, **kwargs):
        return super().get_context_data(
            **kwargs,
            form=CommentForm(),
            comments=self.object.comments.select_related('author')
        )


class PostCreateView(LoginRequiredMixin, CreateView):
    model = Post
    form_class = PostForm
    template_name = 'blog/create.html'

    def form_valid(self, form):
        form.instance.author = self.request.user
        return super().form_valid(form)

    def get_success_url(self):
        return reverse(
            'blog:profile',
            args=[self.request.user.username]
        )


class BaseClass(LoginRequiredMixin, UserPassesTestMixin):
    model = Post
    template_name = 'blog/create.html'
    pk_url_kwarg = 'post_id'

    def test_func(self):
        return self.request.user == self.get_object().author


class PostUpdateView(BaseClass, UpdateView):
    form_class = PostForm

    def get_success_url(self):
        return reverse(
            'blog:post_detail',
            args=[self.kwargs[self.pk_url_kwarg]]
        )

    def handle_no_permission(self):
        return redirect(
            reverse('blog:post_detail', args=[self.kwargs[self.pk_url_kwarg]])
        )


class PostDeleteView(BaseClass, DeleteView):
    success_url = reverse_lazy('blog:index')

    def get_context_data(self, **kwargs):
        return super().get_context_data(
            **kwargs,
            form=DeletionForm(instance=get_object_or_404(
                Post,
                pk=self.kwargs['post_id']))
        )


class CategoryPostsListView(ListView):
    model = Post
    paginate_by = POSTS_ON_THE_PAGE
    template_name = 'blog/category.html'

    def get_category(self, model, category_slug):
        return get_object_or_404(
            model,
            slug=category_slug,
            is_published=True,
        )

    def get_queryset(self):
        return get_posts(self.get_category(
            Category,
            self.kwargs.get('category_slug')
        ).posts.all()
        )

    def get_context_data(self, **kwargs):
        return super().get_context_data(
            **kwargs,
            category=self.get_category(Category, self.kwargs['category_slug'])
        )


class UserProfileDetailView(DetailView):
    model = User
    template_name = 'blog/profile.html'
    context_object_name = 'profile'

    def get_context_data(self, **kwargs):
        if self.request.user.username != self.kwargs['username']:
            return super().get_context_data(
                **kwargs,
                page_obj=get_paginate(get_posts(
                    POSTS
                ).filter(
                    author__username=self.kwargs['username']),
                    self.request
                )
            )
        return super().get_context_data(
            **kwargs,
            page_obj=get_paginate(get_posts(
                POSTS,
                skip_filter=True
            ).filter(
                author__username=self.kwargs['username']),
                self.request
            )
        )

    def get_object(self, queryset=None):
        return get_object_or_404(self.model, username=self.kwargs['username'])


class UserEditProfileUpdateView(
    LoginRequiredMixin,
    UserPassesTestMixin,
    UpdateView
):
    model = User
    form_class = ProfileForm
    template_name = 'blog/user.html'
    success_url = reverse_lazy('blog:index')

    def get_object(self):
        return self.request.user

    def test_func(self):
        return self.get_object() == self.request.user


@login_required
def add_comment(request, post_id):
    form = CommentForm(request.POST)
    if form.is_valid():
        comment = form.save(commit=False)
        comment.author = request.user
        comment.post = get_object_or_404(Post, pk=post_id)
        comment.save()
    return redirect('blog:post_detail', post_id)


@login_required
def edit_comment(request, post_id, comment_id):
    comment = get_object_or_404(Comment, pk=comment_id)
    if request.user != comment.author:
        return redirect('blog:post_detail', post_id)
    form = CommentForm(request.POST or None, instance=comment)
    if form.is_valid():
        form.save()
        return redirect('blog:post_detail', post_id)
    return render(
        request,
        'blog/comment.html',
        {'form': form,
            'comment': comment}
    )


@login_required
def delete_comment(request, post_id, comment_id):
    comment = get_object_or_404(Comment, pk=comment_id)
    if request.user == comment.author:
        if request.method == 'POST':
            comment.delete()
            return redirect('blog:post_detail', post_id)
        context = {'comment': comment}
        return render(request, 'blog/comment.html', context)
    return redirect('blog:post_detail', post_id)


def delete_comment(request, post_id, comment_id):
    comment = get_object_or_404(Comment, pk=comment_id)
    context = {'comment': comment}
    if request.method == 'POST':
        if request.user != comment.author:
            return redirect('blog:post_detail', post_id)
        comment.delete()
        return redirect('blog:post_detail', post_id)
    return render(request, 'blog/comment.html', context)
