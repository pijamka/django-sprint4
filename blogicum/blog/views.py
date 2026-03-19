from datetime import datetime


from django.shortcuts import get_object_or_404, render, redirect
from django.views.generic import (
    CreateView, DeleteView, DetailView, ListView, UpdateView
)
from django.contrib.auth.decorators import login_required
from django.contrib.auth import get_user_model
from django.urls import reverse_lazy, reverse
from django.core.paginator import Paginator
from django.db.models import Count
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.http import Http404

from blog.models import Post, Category, Comment

from .forms import CommentForm, DeleteForm

User = get_user_model()


def filter_posts(posts):
    return posts.filter(
        is_published=True,
        category__is_published=True,
        pub_date__lt=datetime.now()
    )


class IndexListView(ListView):
    model = Post
    ordering = 'id'
    paginate_by = 10
    template_name = 'blog/index.html'

    def get_queryset(self):
        return filter_posts(Post.objects).order_by(
            '-pub_date'
        ).annotate(comment_count=Count('comment'))


class PostDetailDetailView(DetailView):
    model = Post
    template_name = 'blog/detail.html'
    pk_url_kwarg = 'post_id'

    def get_object(self, queryset=None):
        post = super().get_object(queryset)
        if not post.is_published and post.author != self.request.user:
            raise Http404("Этот пост не опубликован или недоступен.")
        return post

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['form'] = CommentForm()
        context['comments'] = self.object.comment.select_related('author')
        return context


class CreatePostCreateView(LoginRequiredMixin, CreateView):
    model = Post
    fields = (
        'title',
        'text',
        'pub_date',
        'is_published',
        'category',
        'location',
        'image'
    )
    template_name = 'blog/create.html'

    def form_valid(self, form):
        form.instance.author = self.request.user
        return super().form_valid(form)

    def get_success_url(self):
        return reverse(
            'blog:profile',
            kwargs={'username': self.request.user.username}
        )


class EditPostUpdateView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    model = Post
    fields = (
        'title',
        'text',
        'pub_date',
        'is_published',
        'category',
        'location',
        'image'
    )
    template_name = 'blog/create.html'
    pk_url_kwarg = 'post_id'

    def get_login_url(self):
        return reverse(
            'blog:post_detail',
            kwargs={'post_id': self.kwargs['post_id']}
        )

    def get_success_url(self):
        return reverse(
            'blog:post_detail',
            kwargs={'post_id': self.kwargs['post_id']}
        )

    def handle_no_permission(self):
        return redirect(self.get_login_url())

    def test_func(self):
        post = self.get_object()
        return self.request.user == post.author


class DeletePostDeleteView(
    LoginRequiredMixin,
    UserPassesTestMixin,
    DeleteView
):
    model = Post
    template_name = 'blog/create.html'
    success_url = reverse_lazy('blog:index')
    pk_url_kwarg = 'post_id'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        post = get_object_or_404(Post, pk=self.kwargs['post_id'])
        context['form'] = DeleteForm(instance=post)
        return context

    def test_func(self):
        post = self.get_object()
        return (
            self.request.user == post.author
            or self.request.user.is_superuser
        )


class CategoryPostsListView(ListView):
    model = Post
    paginate_by = 10
    template_name = 'blog/category.html'

    def get_queryset(self):
        return filter_posts(Post.objects).filter(
            category__slug=self.kwargs.get('category_slug'),
        ).order_by(
            '-pub_date'
        ).annotate(comment_count=Count('comment'))

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['category'] = get_object_or_404(
            Category,
            slug=self.kwargs['category_slug'],
            is_published=True,
        )
        return context


class UserProfileDetailView(DetailView):
    model = User
    template_name = 'blog/profile.html'
    context_object_name = 'profile'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        posts = Post.objects.select_related(
            'category',
            'location',
            'author'
        ).filter(
            author__username=self.kwargs['username']
        ).order_by(
            '-pub_date'
        ).annotate(comment_count=Count('comment'))
        paginator = Paginator(posts, 10)
        context['page_obj'] = paginator.get_page(self.request.GET.get('page'))
        return context

    def get_object(self, queryset=None):
        return get_object_or_404(self.model, username=self.kwargs['username'])


class UserEditProfileUpdateView(
    LoginRequiredMixin,
    UserPassesTestMixin,
    UpdateView
):
    model = User
    fields = ('username', 'email', 'first_name', 'last_name')
    template_name = 'blog/user.html'
    success_url = reverse_lazy('blog:index')

    def get_object(self):
        return self.request.user

    def test_func(self):
        object = self.get_object()
        return object == self.request.user


@login_required
def add_comment(request, post_id):
    post = get_object_or_404(Post, pk=post_id)
    form = CommentForm(request.POST)
    if form.is_valid():
        comment = form.save(commit=False)
        comment.author = request.user
        comment.post = post
        comment.save()
    return redirect('blog:post_detail', post_id=post_id)


@login_required
def edit_comment(request, post_id, comment_id):
    comment = get_object_or_404(Comment, pk=comment_id)
    if request.user != comment.author and not request.user.is_staff:
        return render(request, 'pages/403.html')
    if request.method == 'POST':
        form = CommentForm(request.POST, instance=comment)
        if form.is_valid():
            form.save()
            return redirect('blog:post_detail', post_id=post_id)
    else:
        form = CommentForm(instance=comment)
        return render(
            request,
            'blog/comment.html',
            {'form': form,
             'comment': comment}
        )


@login_required
def delete_comment(request, post_id, comment_id):
    comment = get_object_or_404(Comment, pk=comment_id)
    # form = CommentForm(instance=comment)
    # # context = {'form': form, 'comment': comment}
    context = {'comment': comment}
    if request.method == 'POST':
        if request.user != comment.author and not request.user.is_staff:
            return render(request, 'pages/403.html')
        comment.delete()
        return redirect('blog:post_detail', post_id=post_id)
    return render(request, 'blog/comment.html', context)
