from django.views.generic import ListView

from blog.models import Category, Post, Tag
from blog.views.mixin import CategoryListMixin


class CategoryList(CategoryListMixin, ListView):

    # slug는 인스턴스 변수에서 넘어오므로 클래스 변수로 정의할 수 없음
    # 따라서 __inint__으로 slug를 정의
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.slug = None

    # dispatch는 get인지 post인지 확인하는 함수
    # 어떤 인자가 들어왔는지도 알수 있기에 slug의 값을 인스턴스 변수로 가져옴
    def dispatch(self, request, *args, **kwargs):
        self.slug = kwargs.get("slug")
        return super().dispatch(request, *args, **kwargs)

    def get_queryset(self):
        # post_list로 리턴값을 주어야 post_list.html에서 post_list 변수에 대입 가능
        # __는 변수의 속성 또는 메서드를 참조할 때 활용 할 수 있음
        if self.slug != "no_category":
            post_list = Post.objects.filter(category__slug=self.slug)
        else:
            post_list = Post.objects.filter(category__slug=None)
        return post_list

    # get_context_data 오버라이딩
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if self.slug != "no_category":
            context["category"] = Category.objects.filter(slug=self.slug).first()
        else:
            context["category"] = "미분류"
        return context


class TagList(CategoryListMixin, ListView):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.slug = None
        self.tag = None

    def dispatch(self, request, *args, **kwargs):
        self.slug = kwargs.get("slug")
        return super().dispatch(request, *args, **kwargs)

    def get_queryset(self):
        self.tag = Tag.objects.get(slug=self.slug)
        post_list = self.tag.post_set.all()
        return post_list

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["tag"] = self.tag
        return context
