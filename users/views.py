from django.contrib import messages
from django.contrib.auth import login, logout
from django.db import transaction
from django.shortcuts import redirect, render

from users.forms import LoginForm, SignupForm
from django.contrib.auth import get_user_model


User = get_user_model()

# Create your views here.
def login_view(request):
    if request.method == "POST":
        # LoginForm 인스턴스를 만들며, 입력 데이터는 request.POST를 사용
        form = LoginForm(data=request.POST)

        if form.is_valid():
            user = form.get_user()
            messages.success(request, "{} 으로 로그인 되었습니다.".format(user.username))
            login(request, user)
            # 로그인 후 next의 인자가 들어올 경우 다시 리다이렉트
            next_url = request.GET.get("next", "blog:index")
            return redirect(next_url)
        else:
            form.add_error(None, "입력한 자격증명에 해당하는 사용자가 없습니다")

    else:
        form = LoginForm()

    context = {"form": form}
    return render(request, "users/login.html", context)


def logout_view(request):
    logout(request)
    next_url = request.GET.get("next", "single_pages:ladning")
    return redirect(next_url)


# 별도의 인증 방식을 하고 있지 않음
# 회원가입 실패시 전체 롤백
@transaction.atomic
def signup(request):
    # POST 요청 시, form이 유효하다면 최종적으로 redirect 처리된다
    if request.method == "POST":
        form = SignupForm(data=request.POST, files=request.FILES)
        if form.is_valid():
            user = form.save()
            # 기본 인증 방식 : 아이디, 패스워드
            # 커스텀해서 이메일을 입력받게 하고 있지만 이메일을 인증하지 않음
            user.backend = "django.contrib.auth.backends.ModelBackend"
            messages.success(request, "{}님 회원 가입을 축하드립니다.".format(user.username))
            login(request, user)
            return redirect("blog:index")
    else:
        form = SignupForm()

    context = {"form": form}
    return render(request, "users/signup.html", context)
