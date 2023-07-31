from django.test import TestCase, Client
from bs4 import BeautifulSoup
from blog.models import Category, Comment, Post, Tag
from django.contrib.auth import get_user_model

# Create your tests here.
User = get_user_model()


# 테스트 시 항상 제일 처음은 test_로 시작!
# setUp만 있을 경우 user_create에 대해 테스트를 수행하지 않음! test_로 시작하는 함수가 있어야 테스트가 수행됨!


class BaseTestCase(TestCase):
    def setUp(self):
        self.client = Client()
        self.user_trump = User.objects.create_user(
            username="trump", password="somepassword", email="trump@whitehouse.test"
        )

        self.user_obama = User.objects.create_user(
            username="obama", password="somepassword", email="obama@whitehouse.test"
        )

        self.user_obama.is_staff = True
        self.user_obama.save()

        self.category_programming = Category.objects.create(
            name="programming", slug="programming",
        )

        self.category_music = Category.objects.create(name="music", slug="music",)

        self.tag_python_kor = Tag.objects.create(name="파이썬 공부", slug="파이썬-공부")

        self.tag_python = Tag.objects.create(name="python", slug="python")

        self.tag_hello = Tag.objects.create(name="hello", slug="hello")

        self.post_001 = Post.objects.create(
            title="첫 번째 포스트 입니다.",
            content="Hello Word. We are the world!",
            author=self.user_trump,
            category=self.category_programming,
        )

        self.post_001.tags.add(self.tag_hello)

        self.post_002 = Post.objects.create(
            title="두번째 포스트 입니다.",
            content="저는 쌀국수를 좋아 합니다.",
            author=self.user_obama,
            category=self.category_music,
        )

        self.post_003 = Post.objects.create(
            title="세번째 포스트 입니다.", content="Category가 없을 수도 있죠", author=self.user_obama
        )

        self.post_003.tags.add(self.tag_python)
        self.post_003.tags.add(self.tag_python_kor)

        self.comment_001 = Comment.objects.create(
            post=self.post_001, author=self.user_obama, content="첫 번째 댓글입니다.",
        )

        self.comment_002 = Comment.objects.create(
            post=self.post_001,
            parent=self.comment_001,
            author=self.user_trump,
            content="첫번째 댓글 의 대댓글입니다.",
        )

    def navbar_test(self, soup):
        # 2.2 포스트 목록 페이지와 똑같은 네비게이션 바가 있다.
        # 2.3 첫 번째 포스트의 제목이 웹 브라우저 탭 타이틀에 들어 있다.
        navbar = soup.nav
        self.assertIn("Blog", navbar.text)
        self.assertIn("About me", navbar.text)

        logo_btn = navbar.find("a", text="Do It Django")
        self.assertEqual(logo_btn.attrs["href"], "/")

        home_btn = navbar.select_one("li.nav-item.active > a")
        self.assertEqual(home_btn.attrs["href"], "/")

        blog_btn = navbar.find("a", text="Blog")
        self.assertEqual(blog_btn.attrs["href"], "/blog/")

        about_me_btn = navbar.find("a", text="About me")
        self.assertEqual(about_me_btn.attrs["href"], "/about_me/")

    def get_blog_list(self):
        # 1.1 포스트 목록 페이지(post list)를 연다.
        response = self.client.get("/blog/")

        # 1.2 정상적으로 페이지가 로드된다.
        self.assertEqual(response.status_code, 200)

        # 1.3 페이지의 타이틀에 Blog라는 문구가 있다.
        soup = BeautifulSoup(response.content, "html.parser")

        return soup

    def category_card_test(self, soup):
        categories_card = soup.find("div", id="categories-card")
        self.assertIn("Categories", categories_card.text)
        self.assertIn(
            f"{self.category_programming} ({self.category_programming.post_set.count()})",
            categories_card.text,
        )

        self.assertIn(
            f"{self.category_music} ({self.category_music.post_set.count()})",
            categories_card.text,
        )

        self.assertIn(
            f"미분류 ({Post.objects.filter(category=None).count()})", categories_card.text
        )
