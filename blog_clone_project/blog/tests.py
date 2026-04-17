from datetime import timedelta

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse
from django.utils import timezone

from blog.forms import CommentForm, PostForm
from blog.models import Comment, Post


class BlogTestCase(TestCase):
    def setUp(self):
        # Keep a primary author plus a second user for permission checks.
        self.user = get_user_model().objects.create_user(
            username="author",
            password="testpass123",
        )
        self.other_user = get_user_model().objects.create_user(
            username="other",
            password="testpass123",
        )

    def create_post(self, **kwargs):
        # Provide sensible defaults so tests only override fields they care about.
        defaults = {
            "author": self.user,
            "title": "Test Title",
            "text": "Test body",
        }
        defaults.update(kwargs)
        return Post.objects.create(**defaults)

    @staticmethod
    def create_comment(post, **kwargs):
        # Attach comments to a supplied post while keeping the call sites compact.
        defaults = {
            "post": post,
            "author": "Commenter",
            "text": "Comment text",
        }
        defaults.update(kwargs)
        return Comment.objects.create(**defaults)


class PostModelTests(BlogTestCase):
    def test_publish_sets_published_date(self):
        post = self.create_post(published_date=None)

        post.publish()

        post.refresh_from_db()
        # Compare against "now" defensively in case the test runs across a tick.
        self.assertIsNotNone(post.published_date)
        self.assertLessEqual(post.published_date, timezone.now())

    def test_get_absolute_url_points_to_post_detail(self):
        post = self.create_post()

        self.assertEqual(
            post.get_absolute_url(),
            reverse("blog:post_detail", kwargs={"pk": post.pk}),
        )

    def test_approve_comments_returns_only_approved_comments(self):
        post = self.create_post()
        approved_comment = self.create_comment(post, approved_comments=True)
        self.create_comment(post, approved_comments=False)

        approved_comments = list(post.approve_comments())

        self.assertEqual(approved_comments, [approved_comment])

    def test_comment_approve_comments_marks_comment_as_approved(self):
        post = self.create_post()
        comment = self.create_comment(post, approved_comments=False)

        comment.approve_comments()

        comment.refresh_from_db()
        self.assertTrue(comment.approved_comments)

    def test_comment_string_representation_uses_text(self):
        comment = self.create_comment(self.create_post(), text="Readable comment")

        self.assertEqual(str(comment), "Readable comment")

    def test_post_string_representation_uses_title(self):
        post = self.create_post(title="Readable title")

        self.assertEqual(str(post), "Readable title")


class FormTests(BlogTestCase):
    def test_post_form_uses_expected_fields_and_widgets(self):
        form = PostForm()

        self.assertEqual(list(form.fields.keys()), ["author", "title", "text"])
        self.assertEqual(form.fields["title"].widget.attrs["class"], "text_input_class")
        self.assertIn("editable", form.fields["text"].widget.attrs["class"])
        self.assertIn(
            "medium-editor-textarea", form.fields["text"].widget.attrs["class"]
        )
        self.assertIn("post_content", form.fields["text"].widget.attrs["class"])

    def test_comment_form_uses_expected_fields_and_widgets(self):
        form = CommentForm()

        self.assertEqual(list(form.fields.keys()), ["author", "text"])
        self.assertEqual(
            form.fields["author"].widget.attrs["class"], "text_input_class"
        )
        self.assertIn("editable", form.fields["text"].widget.attrs["class"])
        self.assertIn(
            "medium-editor-textarea", form.fields["text"].widget.attrs["class"]
        )


class PublicViewTests(BlogTestCase):
    def test_about_page_renders(self):
        response = self.client.get(reverse("blog:about"))

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "blog/about.html")

    def test_post_list_shows_only_published_posts_in_descending_order(self):
        # Mix published, draft, and future posts so filtering and ordering are
        # verified in a single request.
        older_post = self.create_post(
            title="Older post",
            published_date=timezone.now() - timedelta(days=2),
        )
        newer_post = self.create_post(
            title="Newer post",
            published_date=timezone.now() - timedelta(days=1),
        )
        self.create_post(title="Draft post", published_date=None)
        self.create_post(
            title="Future post",
            published_date=timezone.now() + timedelta(days=1),
        )

        response = self.client.get(reverse("blog:post_list"))

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "blog/post_list.html")
        self.assertQuerySetEqual(
            response.context["post_list"],
            [newer_post, older_post],
            transform=lambda post: post,
        )
        self.assertContains(response, "Newer post")
        self.assertContains(response, "Older post")
        self.assertNotContains(response, "Draft post")
        self.assertNotContains(response, "Future post")

    def test_post_detail_shows_post(self):
        post = self.create_post(
            title="Visible post",
            published_date=timezone.now(),
        )

        response = self.client.get(reverse("blog:post_detail", kwargs={"pk": post.pk}))

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "blog/post_detail.html")
        self.assertEqual(response.context["post"], post)
        self.assertContains(response, "Visible post")

    def test_post_detail_returns_404_for_missing_post(self):
        response = self.client.get(reverse("blog:post_detail", kwargs={"pk": 9999}))

        self.assertEqual(response.status_code, 404)


class AuthProtectionTests(BlogTestCase):
    def test_create_post_requires_login(self):
        response = self.client.get(reverse("blog:post_new"))

        self.assertRedirects(response, "/accounts/login/?next=/post/new/")

    def test_draft_list_requires_login(self):
        response = self.client.get(reverse("blog:draft_list"))

        self.assertRedirects(response, "/accounts/login/?next=/drafts/")

    def test_add_comment_requires_login(self):
        post = self.create_post(published_date=timezone.now())

        response = self.client.get(
            reverse("blog:add_comment_to_post", kwargs={"pk": post.pk})
        )

        self.assertRedirects(
            response,
            f"/accounts/login/?next=/post/{post.pk}/comment/",
        )

    def test_publish_requires_login(self):
        post = self.create_post(published_date=None)

        response = self.client.get(reverse("blog:post_publish", kwargs={"pk": post.pk}))

        self.assertRedirects(
            response,
            f"/accounts/login/?next=/post/{post.pk}/publish/",
        )

    def test_comment_moderation_requires_login(self):
        post = self.create_post(published_date=timezone.now())
        comment = self.create_comment(post)

        approve_response = self.client.get(
            reverse("blog:comment_approve", kwargs={"pk": comment.pk})
        )
        remove_response = self.client.get(
            reverse("blog:comment_remove", kwargs={"pk": comment.pk})
        )

        self.assertRedirects(
            approve_response,
            f"/accounts/login/?next=/comment/{comment.pk}/approve/",
        )
        self.assertRedirects(
            remove_response,
            f"/accounts/login/?next=/comment/{comment.pk}/remove/",
        )


class AuthenticatedViewTests(BlogTestCase):
    def setUp(self):
        super().setUp()
        # Most tests in this class exercise logged-in author workflows.
        self.client.login(username="author", password="testpass123")

    def test_create_post_get_renders_form(self):
        response = self.client.get(reverse("blog:post_new"))

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "blog/post_form.html")
        self.assertIsInstance(response.context["form"], PostForm)

    def test_create_post_post_creates_post_and_redirects(self):
        response = self.client.post(
            reverse("blog:post_new"),
            {
                "author": self.user.pk,
                "title": "Created title",
                "text": "Created text",
            },
        )

        post = Post.objects.get(title="Created title")
        self.assertRedirects(
            response, reverse("blog:post_detail", kwargs={"pk": post.pk})
        )
        self.assertEqual(post.author, self.user)
        self.assertEqual(post.text, "Created text")

    def test_draft_list_shows_unpublished_posts_only(self):
        newest_draft = self.create_post(
            title="Newest draft",
            created_date=timezone.now(),
            published_date=None,
        )
        older_draft = self.create_post(
            title="Older draft",
            created_date=timezone.now() - timedelta(days=1),
            published_date=None,
        )
        self.create_post(title="Published", published_date=timezone.now())

        response = self.client.get(reverse("blog:draft_list"))

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "blog/post_draft_list.html")
        # The view exposes the queryset as object_list even though the template
        # uses the custom "posts" context name.
        self.assertQuerySetEqual(
            response.context["object_list"],
            [newest_draft, older_draft],
            transform=lambda post: post,
        )
        self.assertContains(response, "Newest draft")
        self.assertContains(response, "Older draft")
        self.assertNotContains(response, "Published")

    def test_add_comment_get_renders_form(self):
        post = self.create_post(published_date=timezone.now())

        response = self.client.get(
            reverse("blog:add_comment_to_post", kwargs={"pk": post.pk})
        )

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "blog/comment_form.html")
        self.assertIsInstance(response.context["form"], CommentForm)

    def test_add_comment_post_creates_comment_for_post(self):
        post = self.create_post(published_date=timezone.now())

        response = self.client.post(
            reverse("blog:add_comment_to_post", kwargs={"pk": post.pk}),
            {"author": "Reader", "text": "Nice article"},
        )

        comment = Comment.objects.get(post=post)
        self.assertRedirects(
            response,
            reverse("blog:post_detail", kwargs={"pk": post.pk}),
        )
        self.assertEqual(comment.author, "Reader")
        self.assertEqual(comment.text, "Nice article")
        # New comments should require moderation before appearing publicly.
        self.assertFalse(comment.approved_comments)

    def test_publish_sets_published_date_and_redirects(self):
        post = self.create_post(published_date=None)

        response = self.client.get(reverse("blog:post_publish", kwargs={"pk": post.pk}))

        post.refresh_from_db()
        self.assertRedirects(
            response,
            reverse("blog:post_detail", kwargs={"pk": post.pk}),
        )
        self.assertIsNotNone(post.published_date)

    def test_comment_approve_marks_comment_approved(self):
        post = self.create_post(published_date=timezone.now())
        comment = self.create_comment(post, approved_comments=False)

        response = self.client.get(
            reverse("blog:comment_approve", kwargs={"pk": comment.pk})
        )

        comment.refresh_from_db()
        self.assertRedirects(
            response,
            reverse("blog:post_detail", kwargs={"pk": post.pk}),
        )
        self.assertTrue(comment.approved_comments)

    def test_comment_remove_deletes_comment(self):
        post = self.create_post(published_date=timezone.now())
        comment = self.create_comment(post)

        response = self.client.get(
            reverse("blog:comment_remove", kwargs={"pk": comment.pk})
        )

        self.assertRedirects(
            response,
            reverse("blog:post_detail", kwargs={"pk": post.pk}),
        )
        self.assertFalse(Comment.objects.filter(pk=comment.pk).exists())

    def test_author_can_update_own_post(self):
        post = self.create_post(title="Original", text="Original body")

        response = self.client.post(
            reverse("blog:post_update", kwargs={"pk": post.pk}),
            {
                "author": self.user.pk,
                "title": "Updated",
                "text": "Updated body",
            },
        )

        post.refresh_from_db()
        self.assertRedirects(
            response, reverse("blog:post_detail", kwargs={"pk": post.pk})
        )
        self.assertEqual(post.title, "Updated")
        self.assertEqual(post.text, "Updated body")

    def test_non_author_cannot_update_post(self):
        post = self.create_post()
        self.client.logout()
        self.client.login(username="other", password="testpass123")

        response = self.client.get(reverse("blog:post_update", kwargs={"pk": post.pk}))

        self.assertEqual(response.status_code, 403)

    def test_author_can_delete_own_post(self):
        post = self.create_post()

        response = self.client.post(reverse("blog:post_delete", kwargs={"pk": post.pk}))

        self.assertRedirects(response, reverse("blog:post_list"))
        self.assertFalse(Post.objects.filter(pk=post.pk).exists())

    def test_non_author_cannot_delete_post(self):
        post = self.create_post()
        self.client.logout()
        self.client.login(username="other", password="testpass123")

        response = self.client.post(reverse("blog:post_delete", kwargs={"pk": post.pk}))

        self.assertEqual(response.status_code, 403)
        self.assertTrue(Post.objects.filter(pk=post.pk).exists())
