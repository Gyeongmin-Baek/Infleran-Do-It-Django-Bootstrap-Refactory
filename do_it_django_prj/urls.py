"""do_it_django_prj URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import include, path, re_path
from django.views.generic import RedirectView

# user 모델이 2개이기에 login, logout, signup과 같은 기본적인 유저
urlpatterns = [
    path("admin/", include("admin_honeypot.urls", namespace="admin_honeypot")),
    path("secret/", admin.site.urls),
    path("", include("single_pages.urls")),
    path("users/", include("users.urls")),
    # url reverse를 하지 않고 직접 지정할 경우 reverse_lazy가 필요 없음
    # url 리버싱과 직접 지정하는 것은 클래스 기반 뷰에서 호출되는 시점이 다름
    re_path(
        r"^(?P<prefix>\w+)/(?P<suffix>login|signup|logout)/$",
        RedirectView.as_view(url="/users/%(suffix)s/"),
    ),
    path("blog/", include("blog.urls")),
    path("markdownx/", include("markdownx.urls")),
    path("accounts/", include("allauth.urls")),
]

urlpatterns += static(prefix=settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
urlpatterns += static(prefix=settings.STATIC_URL, document_root=settings.STATIC_ROOT)
