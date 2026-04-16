from django.urls import path

from blog import views

app_name = "blog"

urlpatterns = [
    path("about/", views.AboutView.as_view(), name="about"),
    path("", views.PostListView.as_view(), name="post_list"),
    path("post/<int:pk>/", views.PostDetailView.as_view(), name="post_detail"),
    path("post/new", views.CreatePostView.as_view(), name="post_new"),
    path("post/<int:pk>/update", views.PostUpdateView.as_view(), name="post_update"),
    path("post/<int:pk>/delete", views.PostDeleteView.as_view(), name="post_delete"),
    path("drafts/", views.DraftListView.as_view(), name="draft_list"),
]
