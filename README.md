# Infleran-Do-It-Django-Bootstrap-Refactory

## 프로젝트 소개

이 프로젝트는 나만의 블로그 사이트를 만들기 위한 프로젝트입니다. Inflearn-Do-It-Django-Bootstrap의 기능 및 코드를 개선하여 더욱 완성도 높은 블로그 사이트를 구축합니다.

## 사용된 기술 스택

- Python
- Django
- HTML
- CSS
- JavaScript
- Bootstrap

## 기능 개선 사항

1. 회원가입 기능 추가 - 로그인, 소셜로그인, 로그아웃, 회원가입 : 장고에서 제공하는 커스텀 유저와 djangoallauth 라이브러리에서 제공하는 유저 모델 사용, 회원가입 중 필요한 정보에 대해 반드시 기입하도록 users 개선
2. 댓글 서비스 개선 - 로그인 하지 않은 사용자도 닉네임 패스워드를 사용해 자유롭게 의견을 낼 수 있으며, 로그인 한 사용자의 경우 추가로 대댓글 작성 가능
3. 카테고리 추가, 수정, 삭제 - 카테고리 항목에 대해 추가, 카테고리 항목 간 수정을 통해 일괄적인 게시글 카테고리 수정, 카테고리 삭제 기능 추가
4. FBV(함수형 기반 뷰) 뿐 아니라 CBV(클래스 기반 뷰)를 활용해 가독성이 높은 코드로 개선 : 예시 - ModelForm을 활용하고 게시글 생성/수정의 템플릿을 통합하여 일괄적인 수정 가능
5. 그 외 - View의 기능을 줄이기 위해 템플릿 태그를 활용, 게시글 삭제, crispy 라이브러리를 통한 게시글 이미지 추가, admin 침입자 탐지를 위한 honeypot 적용 등 필요한 기능들을 추가

## 설치 및 실행 방법

1. 프로젝트 git clone 후 pip install -r requirements.txt를 통해 필요한 파이썬 라이브러리를 다운
2. python manage.py를 통해 서버를 실행하고 웹 브라우저에서 `http://localhost:8000`으로 접속

## 라이선스

이 프로젝트는 MIT 라이선스를 따릅니다. 자세한 내용은 LICENSE 파일을 참조하세요.

이 프로젝트는 [saintdragon2/do_it_django_a_to_z] https://github.com/saintdragon2/do_it_django_a_to_z 의 코드를 기반으로 하여 리팩토링되었습니다.
