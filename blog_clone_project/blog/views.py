from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.shortcuts import render, get_object_or_404, redirect
from django.urls import reverse_lazy
from django.views.generic import (
    TemplateView,
    ListView,
    DetailView,
    CreateView,
    UpdateView,
    DeleteView,
)
from django.utils import timezone

from blog.forms import PostForm, CommentForm
from blog.models import Post, Comment


class AboutView(TemplateView):
    # Render the static about page.
    template_name = "blog/about.html"


class PostListView(ListView):
    # Display only published posts, newest first.
    model = Post

    def get_queryset(self):
        return Post.objects.filter(published_date__lte=timezone.now()).order_by(
            "-published_date"
        )


class PostDetailView(DetailView):
    # Show one post with its related comments.
    model = Post


class CreatePostView(LoginRequiredMixin, CreateView):
    # Require login before allowing a user to create a new post.
    model = Post
    login_url = reverse_lazy("login")
    form_class = PostForm


class PostUpdateView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    # Reuse the post form when editing an existing post.
    model = Post
    login_url = reverse_lazy("login")
    form_class = PostForm

    def test_func(self):
        # Get the specific post the user is trying to update
        post = self.get_object()
        # Check if the current logged-in user is the author
        if self.request.user == post.author:
            return True
        return False


class PostDeleteView(LoginRequiredMixin, UserPassesTestMixin, DeleteView):
    # After deletion, return the user to the post list.
    model = Post
    success_url = reverse_lazy("blog:post_list")

    def test_func(self):
        # Get the specific post the user is trying to delete
        post = self.get_object()
        # Check if the current logged-in user is the author
        if self.request.user == post.author:
            return True
        return False


class DraftListView(LoginRequiredMixin, ListView):
    # List posts that have been created but not published yet.
    login_url = reverse_lazy("login")
    template_name = "blog/post_draft_list.html"
    context_object_name = "posts"

    def get_queryset(self):
        return Post.objects.filter(published_date__isnull=True).order_by(
            "-created_date"
        )


@login_required
def add_comment_to_post(request, pk):
    # Bind the submitted comment to the selected post before saving it.
    post = get_object_or_404(Post, pk=pk)
    if request.method == "POST":
        form = CommentForm(request.POST)
        if form.is_valid():
            comment = form.save(commit=False)
            comment.post = post
            comment.save()
            return redirect("blog:post_detail", pk=post.pk)
    else:
        form = CommentForm()

    return render(request, "blog/comment_form.html", {"form": form})


@login_required
def comment_approve(request, pk):
    # Approve a comment and return to the related post.
    comment = get_object_or_404(Comment, pk=pk)
    comment.approve_comments()
    return redirect("blog:post_detail", pk=comment.post.pk)


@login_required
def comment_remove(request, pk):
    # Delete the comment, then redirect using the saved post id.
    comment = get_object_or_404(Comment, pk=pk)
    post_pk = comment.post.pk
    comment.delete()
    return redirect("blog:post_detail", pk=post_pk)


@login_required
def post_publish(request, pk):
    # Publish a draft post and open its detail page.
    post = get_object_or_404(Post, pk=pk)
    post.publish()
    return redirect("blog:post_detail", pk=post.pk)
