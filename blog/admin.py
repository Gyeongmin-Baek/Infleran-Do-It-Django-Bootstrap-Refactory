from django.contrib import admin
from django.db.models import ManyToManyField
from django.forms import CheckboxSelectMultiple

from blog.models import Category, Comment, Post, Tag


class CommentInline(admin.TabularInline):
    model = Comment
    extra = 1


# Register your models here.
@admin.register(Post)
class PostAdmin(admin.ModelAdmin):
    # Post 변경 화면에서 ManyToManyField를 Checkbox로 출력
    formfield_overrides = {
        ManyToManyField: {"widget": CheckboxSelectMultiple},
    }

    inlines = [
        CommentInline,
    ]


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    prepopulated_fields = {"slug": ("name",)}


@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    prepopulated_fields = {"slug": ("name",)}


@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    pass
