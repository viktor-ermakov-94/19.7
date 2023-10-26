from django import forms
from ckeditor.widgets import CKEditorWidget
from .models import Post, Reply


class PostForm(forms.ModelForm):
    class Meta:
        model = Post
        fields = [
            'category',
            'title',
            'content',
        ]
        widgets = {
            'content': forms.CharField(widget=CKEditorWidget()),
        }


class ReplyForm(forms.ModelForm):
    class Meta:
        model = Reply
        fields = ['text', ]
        widgets = {
          'text': forms.Textarea(attrs={'rows': 4, 'cols': 70}),
        }

