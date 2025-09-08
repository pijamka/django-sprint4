from datetime import datetime
from django.contrib.auth.models import User
from django.contrib.auth.mixins import UserPassesTestMixin
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.db.models import Count
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse_lazy
from django.views.generic import (
    CreateView,
    DetailView,
    DeleteView,
    ListView,
    UpdateView
)

from datetime import datetime

from .forms import CommentForm, PubDateForm
from blog.models import Post, Category, Comment


class OnlyAuthorMixin(UserPassesTestMixin):

    def test_func(self):
        object = self.get_object()
        return object.author == self.request.user


def filter_posts(posts):
    return posts.select_related(
        'author',
        'location',
        'category',
    ).filter(
        is_published=True,
        category__is_published=True,
        pub_date__lt=datetime.now()
    ).annotate(comment_count=Count('comment'))


class IndexListView(ListView):
    model = Post
    queryset = filter_posts(Post.objects)
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
        context['comments'] = self.object.comment.select_related('author')
        return context


class CategoryPostsListView(ListView):
    model = Post
    ordering = 'id'
    paginate_by = 10
    template_name = 'blog/category.html'

    def get_queryset(self):
        return filter_posts(Post.objects).filter(
            category__slug=self.kwargs.get('category_slug'),
        )

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        category = get_object_or_404(
            Category,
            slug=self.kwargs['category_slug'],
            is_published=True,
        )
        context['category'] = category
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
        ).annotate(comment_count=Count('comment'))
        paginator = Paginator(posts, 10)
        context['page_obj'] = paginator.get_page(self.request.GET.get('page'))
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
    form = CommentForm(request.POST)
    if form.is_valid():
        comment = form.save(commit=False)
        comment.author = request.user
        comment.comment = post
        comment.save()
    return redirect('blog:post_detail', pk=pk)


@login_required
def edit_comment(request, post_id, comment_id):
    comment = get_object_or_404(Comment, pk=comment_id)
    if request.user != comment.author and not request.user.is_staff:
        return render(request, 'pages/403.html')
    if request.method == 'POST':
        form = CommentForm(request.POST, instance=comment)
        if form.is_valid():
            form.save()
            return redirect(f'/posts/{post_id}/')
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
    comment = Comment.objects.get(pk=comment_id)
    if request.user != comment.author and not request.user.is_staff:
        return render(request, 'pages/403.html')
    comment.delete()
    return redirect(f'/posts/{post_id}/')
