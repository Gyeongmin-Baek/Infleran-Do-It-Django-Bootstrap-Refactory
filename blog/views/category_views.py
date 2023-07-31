from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.db import transaction
from django.http import HttpResponseRedirect
from django.shortcuts import redirect
from django.urls import reverse_lazy
from django.views.generic import CreateView, FormView

from blog.forms.category import (
    CategoryForm,
    CreateCategoryForm,
    DeleteCategoryForm,
    UpdateCategoryForm,
)
from blog.models import Category, Post


# 카테고리의 생성, 수정 삭제를 담당하는 클래스 뷰
class CategoryManagement(LoginRequiredMixin, UserPassesTestMixin, FormView):
    model = Category
    form_class = CategoryForm
    success_url = reverse_lazy("blog:index")
    template_name = "blog/category_management/category_form.html"

    def test_func(self):
        return self.request.user.is_superuser

    def handle_no_permission(self):
        messages.error(self.request, "관리자만 접근 가능합니다.")
        return super().handle_no_permission()

    # post메소드를 오버라이드 하여 form.is_valid를 호출하지 않았기 때문에
    # 폼의 유효성 검사는 수행되지 않음
    def post(self, request, *args, **kwargs):
        action = request.POST.get("action")
        if action == "create":
            CategoryCreateView.as_view()(request)
        elif action == "update":
            CategoryUpdateView.as_view()(request)
        elif action == "delete":
            CategoryDeleteView.as_view()(request)
        return redirect(self.success_url)


# 카테고리 생성을 담당하는 클래스 뷰
class CategoryCreateView(CreateView):
    model = Category
    form_class = CreateCategoryForm
    success_message = "카테고리가 성공적으로 추가되었습니다."
    success_url = reverse_lazy("blog:index")

    template_name = "blog/category_management/category_form.html"
    # 만약 오버라이딩된 메소드에서 부모 클래스를 호출한다면 form_valid의 경우 save 메서드를 호출함
    # 따라서 save를 객체에서 하게 되면 2중 저장이 되어서 무결성 에러가 발생!
    def form_valid(self, form):
        name = form.cleaned_data["name"]
        category = Category(name=name)
        category.save()
        if self.success_message:
            messages.success(self.request, f"{name} :: {self.success_message}")
        return HttpResponseRedirect(self.success_url)

    def form_invalid(self, form):
        name = form.data.get("name")
        for field, errors in form.errors.items():
            for error in errors:
                messages.error(self.request, f"{name} :: {error}")
        return super().form_invalid(form)


# 카테고리 수정을 담당하는 클래스 뷰
# 카테고리 수정의 경우는 체크되어 있는 값 들을 모두 동일한 카테고리로 수정해야 함
class CategoryUpdateView(FormView):
    model = Category
    form_class = UpdateCategoryForm
    success_url = reverse_lazy("blog:index")
    template_name = "blog/category_management/category_update_form.html"
    # 체크 박스의 아이템을 가져오고 싶을 때 post 또는 form_valid를 사용해서 가져올 수 있음
    def post(self, request, *args, **kwargs):
        # 체크박스의 값을 사용하는 코드
        selected_categories = request.POST.getlist("items")
        self.selected_categories = selected_categories  # 선택된 카테고리를 self에 저장
        return super().post(request, *args, **kwargs)

    @transaction.atomic
    def form_valid(self, form):
        name = form.cleaned_data["name"]
        new_category, is_category_created = Category.objects.get_or_create(name=name)
        if is_category_created:
            new_category.save()
        for category in self.selected_categories:
            category = Category.objects.get(name=category)
            posts = Post.objects.filter(category=category)
            for post in posts:
                post.category = new_category
                post.save()
        return super().form_valid(form)

    def form_invalid(self, form):
        name = form.data.get("name")
        print(form.errors)
        for field, errors in form.errors.items():
            for error in errors:
                messages.error(self.request, f"{name} :: {error}")
        return super().form_invalid(form)


# 카테고리 삭제를 담당하는 뷰
class CategoryDeleteView(FormView):
    model = Category
    form_class = DeleteCategoryForm
    success_url = reverse_lazy("blog:index")
    template_name = "blog/category_management/category_delete_form.html"

    def post(self, request, *args, **kwargs):
        # 체크박스의 값을 사용하는 코드
        selected_categories = request.POST.getlist("items")
        self.selected_categories = selected_categories  # 선택된 카테고리를 self에 저장
        return super().post(request, *args, **kwargs)

    def form_valid(self, form):
        for category in self.selected_categories:
            category = Category.objects.get(name=category)
            posts = Post.objects.filter(category=category)
            for post in posts:
                post.category = None
                post.save()
            category.delete()
        return super().form_valid(form)

    def form_invalid(self, form):
        return super().form_invalid(form)
