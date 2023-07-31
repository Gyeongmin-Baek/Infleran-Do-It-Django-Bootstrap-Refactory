from bs4 import BeautifulSoup

from blog.models import Post
from django.contrib.auth import get_user_model

from blog.tests.base_setup import BaseTestCase

# Create your tests here.
User = get_user_model()


class TestView(BaseTestCase):
    def test_post_list_with(self):
        # 3.1 만약 게시물이 3개 있다면
        self.assertEqual(Post.objects.count(), 3)

        soup = self.get_blog_list()

        self.assertIn("Blog", soup.title.text)

        # 1.4 NavBar가 있다.
        # 1.5 Blog, About me라는 문구가 Navbar에 있다.
        self.navbar_test(soup)
        self.category_card_test(soup)

        # 3.3 메인 영역에 2개의 타이틀이 존재한다.
        main_area = soup.find("div", id="main-area")
        # 3.4 "아직 게시물이 없습니다"라는 문구가 없어야 한다.
        self.assertNotIn("아직 게시물이 없습니다", main_area.text)

        post_001_card = main_area.find("div", id="post-1")
        self.assertIn(self.post_001.title, post_001_card.text)
        self.assertIn(self.post_001.category.name, post_001_card.text)
        self.assertIn(self.tag_hello.name, post_001_card.text)
        self.assertNotIn(self.tag_python.name, post_001_card.text)
        self.assertNotIn(self.tag_python_kor.name, post_001_card.text)

        post_002_card = main_area.find("div", id="post-2")
        self.assertIn(self.post_002.title, post_002_card.text)
        self.assertIn(self.post_002.category.name, post_002_card.text)
        self.assertNotIn(self.tag_hello.name, post_002_card.text)
        self.assertNotIn(self.tag_python.name, post_002_card.text)
        self.assertNotIn(self.tag_python_kor.name, post_002_card.text)

        post_003_card = main_area.find("div", id="post-3")
        self.assertIn(self.post_003.title, post_003_card.text)
        self.assertIn("미분류", post_003_card.text)
        self.assertNotIn(self.tag_hello.name, post_002_card.text)
        self.assertIn(self.tag_python.name, post_003_card.text)
        self.assertIn(self.tag_python_kor.name, post_003_card.text)

        self.assertIn(self.post_001.author.username.upper(), main_area.text)
        self.assertIn(self.post_002.author.username.upper(), main_area.text)

    def test_post_list_without(self):
        Post.objects.all().delete()
        # 2.1 게시물이 하나도 없을 때
        self.assertEqual(Post.objects.count(), 0)
        # 2.2 메인 영역에 "아직 게시물이 없습니다"라는 문구가 나온다.
        soup = self.get_blog_list()
        main_area = soup.find("div", id="main-area")
        self.assertIn("아직 게시물이 없습니다", main_area.text)

    def test_post_detail(self):

        self.assertEqual(Post.objects.count(), 3)

        # 1.2 그 포스트의 url은 '/blog/1/' 이다.
        self.assertEqual(self.post_001.get_absolute_url(), "/blog/1/")
        # 2. 첫 번째 포스트의 상세 페이지 테스트
        # 2.1 첫 번째 포스트의 url로 접근하면 정상적으로 작동한다(status code: 200)
        response = self.client.get(self.post_001.get_absolute_url())
        self.assertEqual(response.status_code, 200)
        soup = BeautifulSoup(response.content, "html.parser")
        # 2.2 포스트 목록 페이지와 똑같은 네비게이션 바가 있다.
        self.navbar_test(soup)
        self.category_card_test(soup)
        # 2.3 첫 번째 포스트의 제목이 웹 브라우저 탭 타이틀에 들어 있다.
        self.assertIn(self.post_001.title, soup.title.text)
        # 2.4 첫 번째 포스트의 제목이 포스트 영역에 있다.
        post_area = soup.find("div", id="post-area")
        self.assertIn(self.post_001.title, post_area.text)
        self.assertIn(self.post_001.category.name, post_area.text)
        # 2.5 첫 번째 포스트의 작성자(author)가 포스트 영역에 있다.
        self.assertIn(self.user_trump.username.upper(), post_area.text)
        # 2.6 첫 번째 포스트의 내용(content)이 포스트 영역에 있다.
        self.assertIn(self.post_001.content, post_area.text)

        self.assertIn(self.tag_hello.name, post_area.text)
        self.assertNotIn(self.tag_python.name, post_area.text)
        self.assertNotIn(self.tag_python_kor.name, post_area.text)

        comments_area = soup.find("div", id="comment-area")
        comment_001_area = comments_area.find("div", id="comment-1")
        comment_002_area = comments_area.find("div", id="comment-2")
        self.assertIn(self.comment_001.author.username, comment_001_area.text)
        self.assertIn(self.comment_001.content, comment_001_area.text)
        self.assertIn(self.comment_002.author.username, comment_002_area.text)
        self.assertIn(self.comment_002.content, comment_002_area.text)

    def test_category_page(self):
        response = self.client.get(self.category_programming.get_absolute_url())
        self.assertEqual(response.status_code, 200)

        soup = BeautifulSoup(response.content, "html.parser")
        self.navbar_test(soup)
        self.category_card_test(soup)

        main_area = soup.find("div", id="main-area")
        self.assertIn(self.category_programming.name, main_area.h1.text)
        self.assertIn(self.category_programming.name, main_area.text)
        self.assertIn(self.post_001.title, main_area.text)
        self.assertNotIn(self.post_002.title, main_area.text)
        self.assertNotIn(self.post_003.title, main_area.text)

    def test_tag_page(self):
        response = self.client.get(self.tag_hello.get_absolute_url())
        self.assertEqual(response.status_code, 200)
        soup = BeautifulSoup(response.content, "html.parser")
        self.navbar_test(soup)
        self.category_card_test(soup)
        self.assertIn(self.tag_hello.name, soup.h1.text)
        main_area = soup.find("div", id="main-area")
        self.assertIn(self.tag_hello.name, main_area.text)
        self.assertIn(self.post_001.title, main_area.text)
        self.assertNotIn(self.post_002.title, main_area.text)
        self.assertNotIn(self.post_003.title, main_area.text)

    def test_search(self):
        post_about_python = Post.objects.create(
            title="파이썬에 대한 포스트 입니다.",
            content="Hello World, We are the World",
            author=self.user_trump,
        )

        response = self.client.get("/blog/search/파이썬/")
        self.assertEqual(response.status_code, 200)
        soup = BeautifulSoup(response.content, "html.parser")

        main_area = soup.find("div", id="main-area")
        self.assertIn("Search: 파이썬 (2)", main_area.text)
        self.assertNotIn(self.post_001.title, main_area.text)
        self.assertNotIn(self.post_002.title, main_area.text)
        self.assertIn(self.post_003.title, main_area.text)
        self.assertIn(post_about_python.title, main_area.text)
