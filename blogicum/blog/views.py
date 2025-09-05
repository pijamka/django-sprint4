from datetime import datetime
from django.contrib.auth.models import User
from django.contrib.auth.mixins import UserPassesTestMixin
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse_lazy
from django.views.generic import (
    CreateView,
    DetailView,
    DeleteView,
    ListView,
    UpdateView
)

from .forms import CommentForm, PubDateForm

from blog.models import Post, Category


class OnlyAuthorMixin(UserPassesTestMixin):

    def test_func(self):
        object = self.get_object()
        return object.author == self.request.user


def filter_posts(posts):
    return posts.select_related(
        'author',
        'location',
        'category'
    ).filter(
        is_published=True,
        category__is_published=True,
        pub_date__lt=datetime.now()
    )


class IndexListView(ListView):
    model = Post
    ordering = 'id'
    paginate_by = 10
    template_name = 'blog/index.html'


class CreatePostCreateView(CreateView):
    model = Post
    form_class = PubDateForm
    template_name = 'blog/create.html'
    success_url = reverse_lazy('blog:index')

    def form_valid(self, form):
        form.instance.author = self.request.user
        return super().form_valid(form)


class EditPostUpdateView(OnlyAuthorMixin, UpdateView):
    model = Post
    fields = (
        'title',
        'text',
        'pub_date',
        'is_published',
        'category',
        'location',
    )
    template_name = 'blog/create.html'
    success_url = reverse_lazy('blog:index')


class DeletePostDeleteView(OnlyAuthorMixin, DeleteView):
    model = Post
    template_name = 'blog/create.html'
    success_url = reverse_lazy('blog:index')


class PostDetailDetailView(DetailView):
    model = Post
    template_name = 'blog/detail.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['form'] = CommentForm()
        context['comment'] = (
            self.object.comment.select_related('author')
        )
        return context


class CategoryPostsListView(ListView):
    model = Post
    ordering = 'id'
    paginate_by = 10
    template_name = 'blog/category.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        category = get_object_or_404(
            Category,
            slug=self.kwargs['category_slug'],
            is_published=True,
        )
        context['category'] = category
        context['page_obj'] = filter_posts(category.posts.all())
        return context


class UserProfileDetailView(DetailView):
    model = User
    template_name = 'blog/profile.html'
    context_object_name = 'profile'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['page_obj'] = Post.objects.filter(author=self.object)
        return context

    def get_object(self, queryset=None):
        return get_object_or_404(self.model, username=self.kwargs['username'])


class UserEditProfileUpdateView(UpdateView):
    model = User
    fields = ('username', 'email', 'first_name', 'last_name')
    template_name = 'blog/user.html'
    success_url = reverse_lazy('blog:index')

    def get_object(self):
        return self.request.user


@login_required
def add_comment(request, pk):
    post = get_object_or_404(Post, pk=pk)
    form = CommentForm(request.Post)
    if form.is_valid():
        comment = form.save(commit=False)
        comment.author = request.user
        comment.post = post
        comment.save()
    return redirect('blog:detail', pk=pk)
