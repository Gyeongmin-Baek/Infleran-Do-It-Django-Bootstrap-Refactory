from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.exceptions import PermissionDenied
from django.http import HttpResponseRedirect
from django.shortcuts import redirect
from django.urls import reverse_lazy
from django.views.generic import CreateView, DeleteView, UpdateView

from blog.forms.post import PostForm
from blog.models import Post
from blog.views.mixin import PostFormValidMixin
from django.contrib import messages


class PostCreate(LoginRequiredMixin, PostFormValidMixin, CreateView):
    model = Post
    form_class = PostForm
    success_message = "포스팅이 성공적으로 작성되었습니다."
    # 포스팅 작성 후 리다이렉트 url
    # 기본 설정은 get_absolute_url이므로 다르게 리다이렉트를 하고 싶으면 form_valid 메소드에서 경로 수정 필요
    success_url = reverse_lazy("blog:index")

    # get_form_kwargs 메소드는 폼 인스턴스를 생성할 때 전달할 인수들을 반환하는 메소드
    # form_valid 메소드는 폼이 유효할 때만 호출되므로 author는 폼 인스턴스가 생성될 때 가져오자
    # Mixin으로 이동
    # def get_form_kwargs(self):
    #     kwargs = super().get_form_kwargs()
    #     kwargs["author_pk"] = self.request.user.pk
    #     return kwargs

    # handle_no_permission 메소드는 로그인하지 않은 사용자가 뷰에 접근할 경우 호출되는 메소드
    # 기본 설정은 로그인페이지로 리다이렉트
    # def handle_no_permission(self):
    #     return redirect("blog:index")

    """
    dispatch 함수는 뷰의 진입점(GET, POST)이므로
    이 함수를 오버라이드하여 뷰에 대한 접근 제어, 인증, 권한 검사 등의 전처리 작업을 수행할 수 있는 메소드
    유저의 상태(일반, staff, super)인지 확인하고 일반 유저인 경우 redirect
    UserPassesTestMixin의 test_func 보다 dispatch를 사용하여 복잡한 로직을 처리
    """

    def dispatch(self, request, *args, **kwargs):
        if not (request.user.is_staff or request.user.is_superuser):
            return redirect("blog:index")
        return super().dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["view_name"] = "create"
        return context

    def form_valid(self, form):
        response = super().form_valid(form)
        if self.success_message:
            title = self.object.title
            messages.success(self.request, f"{title} {self.success_message}")
        # 명시적으로 리다이렉트를 해 주지 않으면 기본값 get_absolute_url로 리다이렉트
        return HttpResponseRedirect(self.get_success_url())


class PostUpdate(LoginRequiredMixin, PostFormValidMixin, UpdateView):
    model = Post
    form_class = PostForm
    success_message = "포스팅이 성공적으로 수정되었습니다."

    # 폼의 초기값을 가져올 때 사용
    def get_initial(self):
        initial = super().get_initial()
        tags = self.object.tags.all().values_list("name", flat=True)
        initial["Tags"] = "; ".join(tags)
        return initial

    # 뷰에서 폼 인스턴스를 생성할 때 전달되는 키워드 인수를 반환하는 데 사용
    # Mixin으로 이동
    # def get_form_kwargs(self):
    #     kwargs = super().get_form_kwargs()
    #     kwargs["author_pk"] = self.request.user.pk
    #     return kwargs

    # 메소드는 뷰에서 HTTP 메소드에 따라 요청을 처리하는 메소드를 결정하는 데 사용됩니다.
    # 이 메소드는 뷰가 호출될 때마다 실행되며, 요청의 HTTP 메소드에 따라 적절한 핸들러 메소드를 호출합니다.
    # 예를 들어, GET 요청의 경우 get 메소드가 호출되고, POST 요청의 경우 post 메소드가 호출됩니다.
    def dispatch(self, request, *args, **kwargs):
        if request.user.is_authenticated and request.user == self.get_object().author:
            return super().dispatch(request, *args, **kwargs)
        else:
            raise PermissionDenied

    # 메소드는 템플릿에 전달되는 컨텍스트 데이터를 설정하는 데 사용됩니다.
    # 이 메소드는 뷰가 렌더링될 때마다 호출되어, 템플릿에서 사용할 수 있는 변수를 설정
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["view_name"] = "update"
        return context

    def form_valid(self, form):
        self.object.tags.clear()
        response = super().form_valid(form)
        if self.success_message:
            messages.success(self.request, self.success_message)
        return response


# 게시글 삭제 시에는 Form class를 불러오지 않아도 됨
class PostDelete(LoginRequiredMixin, DeleteView):
    model = Post
    success_url = reverse_lazy("blog:index")
    template_name = "blog/post_confirm_delete.html"
    success_message = "포스팅을 성공적으로 삭제했습니다."

    # 유저가 삭제할 수 있는 포스팅의 범위를 제한
    def get_queryset(self):
        return Post.objects.filter(author=self.request.user)

    # 포스팅을 가져오는데 해당 유저가 맞는지 확인
    def get_object(self, queryset=None):
        obj = super().get_object()
        if not obj.author == self.request.user:
            raise PermissionDenied
        return obj

    # delete 메소드는 최대한 건드리지 않기위해 get 요청시 메시지를 저장!
    # 이 메소드는 삭제확인 페이지가 렌더링 되기 전 호출
    def get(self, request, *args, **kwargs):
        obj = self.get_object()
        success_message = f"{obj.title} :: {self.success_message}"
        messages.success(request, success_message)
        return super().get(request, *args, **kwargs)
