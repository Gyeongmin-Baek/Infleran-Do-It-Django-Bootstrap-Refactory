from django.db.models import Q
from django.views.generic import DetailView, ListView

from blog.forms.comment import CommentForm
from blog.models import Comment, Post
from blog.views.mixin import CategoryListMixin


class PostList(CategoryListMixin, ListView):
    model = Post
    ordering = "-pk"
    paginate_by = 5


class PostDetail(CategoryListMixin, DetailView):
    model = Post

    def get_context_data(self, **kwargs):
        context = super().get_context_data()
        context["comment_form"] = CommentForm
        post = self.get_object()
        comments = Comment.objects.filter(post=post).order_by("-created_at")
        context["comments"] = comments
        return context


class PostSearch(PostList):
    paginate_by = None

    def get_queryset(self):
        q = self.kwargs["q"]
        post_list = Post.objects.filter(
            Q(title__contains=q) | Q(tags__name__contains=q)
        ).distinct()
        return post_list

    def get_context_data(self, **kwargs):
        context = super().get_context_data()
        q = self.kwargs["q"]
        context["search_info"] = f"Search: {q} ({self.get_queryset().count()})"
        return context
