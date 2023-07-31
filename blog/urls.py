from django.urls import path
from blog.views.comment_views import (
    new_comment,
    update_comment,
    delete_comment,
    reply_comment,
)
from blog.views.post_admin_views import PostCreate, PostUpdate, PostDelete
from blog.views.post_views import PostDetail, PostList, PostSearch
from blog.views.taxonomy_views import CategoryList, TagList
from blog.views.category_views import CategoryManagement

app_name = "blog"

urlpatterns = [
    path("", PostList.as_view(), name="index"),
    path("<int:pk>/", PostDetail.as_view(), name="single_page"),
    path("category/<str:slug>/", CategoryList.as_view(), name="category_page"),
    path("category/no_category/", CategoryList.as_view(), name="no_category_page"),
    path("tag/<str:slug>/", TagList.as_view(), name="tag_page"),
    path("create_post/", PostCreate.as_view(), name="create_post"),
    path("update_post/<int:pk>/", PostUpdate.as_view(), name="update_post"),
    path("delete_post/<int:pk>/", PostDelete.as_view(), name="delete_post"),
    path("<int:pk>/new_comment/", new_comment, name="create_comment"),
    path("update_comment/<int:pk>/", update_comment, name="update_comment"),
    path("delete_comment/<int:pk>/", delete_comment, name="delete_comment"),
    path(
        "reply_comment/<int:post_id>/<int:comment_id>",
        reply_comment,
        name="reply_comment",
    ),
    path(
        "category_management/",
        CategoryManagement.as_view(),
        name="category_management",
    ),
    path("search/<str:q>/", PostSearch.as_view()),
]
