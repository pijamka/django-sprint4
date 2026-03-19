from django import forms

from .models import Post, Comment


class CommentForm(forms.ModelForm):

    class Meta:
        model = Comment
        fields = ('text',)


class DeleteForm(forms.ModelForm):

    class Meta:
        model = Post
        fields = ('__all__')
