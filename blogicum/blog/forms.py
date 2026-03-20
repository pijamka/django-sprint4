from django import forms

from .models import Post, Comment, User


class CommentForm(forms.ModelForm):

    class Meta:
        model = Comment
        fields = ('text',)


class DeletionForm(forms.ModelForm):

    class Meta:
        model = Post
        fields = ('__all__')


class PostForm(forms.ModelForm):
    class Meta:
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


class ProfileForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ('username', 'email', 'first_name', 'last_name')
