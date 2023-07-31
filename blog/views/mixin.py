from django.shortcuts import redirect

from blog.forms.category import CategoryForm
from blog.models import Category, Post, Tag

# texonomy_views


class CategoryListMixin:
    def get_context_data(self, **kwargs):
        context = super().get_context_data()
        context["categories"] = Category.objects.all()
        context["no_category_post_count"] = Post.objects.filter(category=None).count()
        context["category_form"] = CategoryForm()
        context["is_admin"] = (
            self.request.user.is_authenticated and self.request.user.is_superuser
        )
        return context


# post_admin_views
class PostFormValidMixin:

    # get_form_kwargs 메소드는 폼 인스턴스를 생성할 때 전달할 인수들을 반환하는 메소드
    # form_valid 메소드는 폼이 유효할 때만 호출되므로 author는 폼 인스턴스가 생성될 때 가져오자
    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs["author_pk"] = self.request.user.pk
        return kwargs

    def form_valid(self, form):
        # 폼 데이터 가공
        content = form.cleaned_data["content"]
        title = form.cleaned_data["title"]
        tags_str = form.cleaned_data["Tags"]

        # 모델 인스턴스 저장 self.object는 forms 인스턴스 객체를 들고옴
        self.object = form.save()
        # 태그가 있는지 확인하고 있으면 저장
        if tags_str:
            # 빈 문자열에 split을 하게 될 경우 빈 값이 아니라 [""]와 같은 값이 생김
            # 따라서 tag_list를 tags_str 다음 적어주는 것이 아닌 tags_str 체크 후 반영
            # 다대다 관계는 중간 필드가 정의되어야 하기에 tag 저장 후 객체에 tag 저장
            tags_list = tags_str.split(";")
            for tag_name in tags_list:
                tag_name = tag_name.strip()
                tag, is_tag_created = Tag.objects.get_or_create(name=tag_name)
                if is_tag_created:
                    tag.save()
                self.object.tags.add(tag)
        # 리다이렉트 URL 반환
        return redirect("blog:single_page", pk=self.object.pk)
