from datetime import datetime
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from django.views.generic import CreateView, DetailView, DeleteView, ListView, UpdateView
from django.shortcuts import get_object_or_404, render, redirect
from django.urls import reverse_lazy

from .forms import CommentForm

from blog.models import Post, Category


class IndexListView(ListView):
    model = Post
    ordering = 'id'
    paginate_by = 10
    template_name = 'blog/index.html'


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





def post_detail(request, post_id):
    return render(
        request,
        'blog/detail.html',
        {
            'post': get_object_or_404(
                filter_posts(
                    Post.objects
                ),
                pk=post_id
            )
        }
    )


class CreatePostCreateView(CreateView):
    model = Post
    fields = '__all__'
    template_name = 'blog/create.html'
    success_url = reverse_lazy('blog:index')

    def form_valid(self, form):
        form.instance.author = self.request.user
        return super().form_valid(form)


def edit_profile(request):
    return render(request, 'blog/profile.html')


class UserProfileListView(ListView):
    model = Post
    ordering = 'id'
    paginate_by = 10
    template_name = 'blog/profile.html'

    def get_queryset(self):
        return Post.objects.filter(author__username=self.kwargs['username'])

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['profile'] = User.objects.get(username=self.kwargs['username'])
        return context


class EditPostUpdateView(UpdateView):
    model = Post
    template_name = 'blog/create.html'


class DeletePostDeleteView(DeleteView):
    model = Post
    template_name = 'blog/create.html'

class PostDetailDetailView(DetailView):
    model = Post
    template_name = 'blog/detail.html' 

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Записываем в переменную form пустой объект формы.
        context['form'] = CommentForm()
        # Запрашиваем все поздравления для выбранного дня рождения.
        context['comment'] = (
            # Дополнительно подгружаем авторов комментариев,
            # чтобы избежать множества запросов к БД.
            self.object.comment.select_related('author')
        )
        return context    


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

def category_posts(request, category_slug):
    category = get_object_or_404(
        Category,
        slug=category_slug,
        is_published=True,
    )
    return render(
        request,
        'blog/category.html',
        {
            'category': category,
            'page_obj': filter_posts(category.posts.all())
        }
    )








'''
def user_profile(request, username):
    profile = User.objects.get(username=username)
    posts =  Post.objects.filter(author__username=username)
    return render(
        request,
        'blog/profile.html',
        {
            'profile': profile,
            'page_obj': posts
        },)
def index(request):
    return render(
        posts = Post.objects.order_by('id')
        paginator = Paginator(posts, 10)
        page_number = request.GET.get('page')

        context = {
            'posts'
        }
        request,
        'blog/index.html',
        {
            'posts': filter_posts(
                Post.objects
            )[:5]
        }
    )



'''