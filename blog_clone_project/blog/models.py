from django.db import models
from django.utils import timezone
from django.urls import reverse
from django.conf import settings


class Post(models.Model):
    # Link each post to the Django user who created it.
    author = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    # Store the main post content and lifecycle timestamps.
    title = models.CharField(max_length=200)
    text = models.TextField()
    created_date = models.DateTimeField(default=timezone.now)
    published_date = models.DateTimeField(blank=True, null=True)

    def publish(self):
        # Mark the post as published using the current time.
        self.published_date = timezone.now()
        self.save()

    def approve_comments(self):
        # Return only the comments that have been approved for display.
        return self.comments.filter(approved_comments=True)

    def get_absolute_url(self):
        # Send Django back to this post's detail page after create/update actions.
        return reverse("blog:post_detail", kwargs={"pk": self.pk})

    def __str__(self):
        # Use the post title in the admin and shell output.
        return self.title


class Comment(models.Model):
    # Attach each comment to a specific blog post.
    post = models.ForeignKey(Post, related_name="comments", on_delete=models.CASCADE)
    # Store the comment body plus moderation state.
    author = models.CharField(max_length=200)
    text = models.TextField()
    created_date = models.DateTimeField(default=timezone.now)
    approved_comments = models.BooleanField(default=False)

    def approve_comments(self):
        # Mark the comment as approved so it can be shown publicly.
        self.approved_comments = True
        self.save()

    @staticmethod
    def get_absolute_url():
        # Return to the homepage after a comment is submitted.
        return reverse("post_list")

    def __str__(self):
        # Show the comment text in admin lists and debugging output.
        return self.text
