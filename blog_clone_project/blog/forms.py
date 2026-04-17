from django import forms
from blog.models import Post, Comment


class PostForm(forms.ModelForm):
    # Use a model-backed form so Django handles post validation and saving.
    class Meta:
        model = Post
        fields = ("author", "title", "text")
        # Apply CSS classes so the form matches the blog styling and editor setup.
        widgets = {
            "title": forms.TextInput(attrs={"class": "text_input_class"}),
            "text": forms.Textarea(
                attrs={"class": "editable medium-editor-textarea post_content"}
            ),
        }


class CommentForm(forms.ModelForm):
    # Keep comment creation limited to the visitor's name and comment text.
    class Meta:
        model = Comment
        fields = ("author", "text")
        # Reuse the same editor styling as the post form.
        widgets = {
            "author": forms.TextInput(attrs={"class": "text_input_class"}),
            "text": forms.Textarea(attrs={"class": "editable medium-editor-textarea "}),
        }
