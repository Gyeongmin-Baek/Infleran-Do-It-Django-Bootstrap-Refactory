import re

from bs4 import BeautifulSoup
from django.urls import reverse

from blog.models import Post, Tag
from blog.tests.base_setup import BaseTestCase


class TestPage(BaseTestCase):
    def test_create_post_without_login(self):
        response = self.client.get("/blog/create_post/")
        self.assertNotEqual(response.status_code, 200)

    def test_create_post_with_login(self):
        self.client.login(username="trump", password="somepassword")
        response = self.client.get("/blog/create_post/")
        self.assertNotEqual(response.status_code, 200)

        self.client.login(username="obama", password="somepassword")
        response = self.client.get("/blog/create_post/")
        self.assertEqual(response.status_code, 200)

        soup = BeautifulSoup(response.content, "html.parser")
        self.assertIn("Create Post - Blog", soup.title.text)
        main_area = soup.find("div", id="main-area")
        self.assertIn("Create a New Post", main_area.text)

        tag_str_input = main_area.find("input", id="id_Tags")
        self.assertTrue(tag_str_input)

        self.assertEqual(Tag.objects.count(), 3)

        self.client.post(
            "/blog/create_post/",
            {
                "title": "Post Form 만들기",
                "content": "Post Form 페이지를 만듭시다",
                "Tags": "new tag, 한글 태그; python",
            },
        )

        last_post = Post.objects.last()

        self.assertEqual(last_post.title, "Post Form 만들기")
        self.assertEqual(last_post.author.username, "obama")

        self.assertEqual(last_post.tags.count(), 3)
        self.assertTrue(Tag.objects.get(name="new tag"))
        self.assertTrue(Tag.objects.get(name="한글 태그"))
        self.assertTrue(Tag.objects.get(name="python"))
        self.assertEqual(Tag.objects.count(), 5)

        response = self.client.post(
            "/blog/create_post/", {"title": "태그가 없어요", "content": "태그가 없어도 되겠죠?",},
        )

        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, reverse("blog:index"))

        last_post = Post.objects.last()
        self.assertEqual(last_post.title, "태그가 없어요")
        self.assertEqual(last_post.author.username, "obama")

    def test_update_post(self):
        post_update_url = f"/blog/update_post/{self.post_003.pk}/"

        # 로그인 하지 않은 상태에서 접근하는 경우
        response = self.client.get(post_update_url)
        self.assertNotEqual(response.status_code, 200)

        # 로그인은 했지만, 작성자가 아닌 경우
        self.assertNotEqual(self.post_003.author, self.user_trump)
        self.client.login(username="trump", password="somepassword")
        response = self.client.get(post_update_url)
        self.assertNotEqual(response.status_code, 200)

        # 작성자(obama)가 접근하는 경우
        self.assertEqual(self.post_003.author, self.user_obama)
        self.client.login(username="obama", password="somepassword")
        response = self.client.get(post_update_url)
        self.assertEqual(response.status_code, 200)

        soup = BeautifulSoup(response.content, "html.parser")
        self.assertIn("Edit Post - Blog", soup.title.text)
        main_area = soup.find("div", id="main-area")
        self.assertIn("Edit Post", main_area.text)

        tag_str_input = main_area.find("input", id="id_Tags")
        self.assertTrue(tag_str_input)
        self.assertIn("파이썬 공부; python", tag_str_input["value"])

        response = self.client.post(
            post_update_url,
            {
                "title": "세 번째 포스트를 수정했습니다.",
                "content": "안녕 세계? 우리는 하나!",
                "category": self.category_music.pk,
                "Tags": "파이썬 공부; 한글 태그; some tag",
            },
            follow=True,
        )

        soup = BeautifulSoup(response.content, "html.parser")
        main_area = soup.find("div", id="main-area")

        self.assertIn("파이썬 공부", main_area.text)
        self.assertIn("한글 태그", main_area.text)
        self.assertIn("some tag", main_area.text)
        self.assertNotIn("python", main_area.text)

        self.assertIn("세 번째 포스트를 수정했습니다.", main_area.text)
        self.assertIn("안녕 세계? 우리는 하나!", main_area.text)
        self.assertIn(self.category_music.name, main_area.text)

    def test_delete_post(self):
        post_delete_url = f"/blog/delete_post/{self.post_003.pk}/"

        # 로그인 하지 않은 상태에서 접근하는 경우
        response = self.client.get(post_delete_url)
        self.assertNotEqual(response.status_code, 200)

        # 로그인은 했지만, 작성자가 아닌 경우
        self.assertNotEqual(self.post_003.author, self.user_trump)
        self.client.login(username="trump", password="somepassword")
        response = self.client.get(post_delete_url)
        self.assertNotEqual(response.status_code, 200)

        # 작성자(obama)가 접근하는 경우
        self.assertEqual(self.post_003.author, self.user_obama)
        self.client.login(username="obama", password="somepassword")
        response = self.client.get(post_delete_url)
        self.assertEqual(response.status_code, 200)

        # 0. 오바마가 접근한 후 포스팅 삭제 확인 페이지가 나와야 함
        soup = BeautifulSoup(response.content, "html.parser")
        main_area = soup.find("div", id="main-area")
        self.assertIn("정말 삭제하시겠습니까?", main_area.text)
        self.assertIn("내용보기", main_area.text)
        self.assertIn("삭제하겠습니다", main_area.text)

        # 1. 내용보기를 누르면 detail page로 redirect
        post_page = main_area.find("a", string=re.compile(r"\s*내용보기\s*"))
        self.assertEqual(post_page["href"], self.post_003.get_absolute_url())
        response_redirect = self.client.get(post_page["href"])
        self.assertEqual(response_redirect.status_code, 200)
        # 2. 삭제를 누른 후 리스트 페이지로 redirect로 이동 하는지 확인
        response = self.client.post(post_delete_url, follow=True)
        # 3. 성공적으로 삭제가 되면 list에 포스팅이 없어야 함
        self.assertEqual(response.status_code, 200)
        soup = BeautifulSoup(response.content, "html.parser")
        main_area = soup.find("div", id="main-area")
        self.assertFalse(Post.objects.filter(pk=self.post_003.pk).exists())
