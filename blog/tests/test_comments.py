from bs4 import BeautifulSoup
from django.contrib import auth

from blog.models import Comment, Post
from django.contrib.auth import get_user_model

from blog.tests.base_setup import BaseTestCase

# Create your tests here.
User = get_user_model()


class TestComment(BaseTestCase):
    def get_comment_area(self, post):
        response = self.client.get(post.get_absolute_url())
        self.assertEqual(response.status_code, 200)
        soup = BeautifulSoup(response.content, "html.parser")
        return soup.find("div", id="comment-area")

    # 로그인 한 상태에서 댓글쓰기
    def test_comment_login_user(self):
        self.client.login(username="obama", password="somepassword")
        response = self.client.get(self.post_001.get_absolute_url())
        self.assertEqual(response.status_code, 200)

        soup = BeautifulSoup(response.content, "html.parser")

        comment_area = soup.find("div", id="comment-area")
        comment_form = comment_area.find("form", id="comment-form")
        self.assertNotIn("Guestname", comment_form.text)
        self.assertIn("Log Out", comment_area.text)

        response = self.client.post(
            self.post_001.get_absolute_url() + "new_comment/",
            {"content": "오바마의 댓글입니다."},
            follow=True,
        )

        self.assertEqual(response.status_code, 200)

        self.assertEqual(Comment.objects.count(), 3)

        new_comment = Comment.objects.last()
        soup = BeautifulSoup(response.content, "html.parser")
        self.assertIn(new_comment.post.title, soup.title.text)

        comment_area = soup.find("div", id="comment-area")
        new_comment_div = comment_area.find("div", id=f"comment-{new_comment.pk}")
        self.assertIn("obama", new_comment_div.text)
        self.assertIn("오바마의 댓글입니다.", new_comment_div.text)

    # 로그인 하지 않은 사용자의 댓글 생성
    def test_comment_any_user(self):
        response = self.client.get(self.post_001.get_absolute_url())
        user = auth.get_user(self.client)
        self.assertFalse(user.is_authenticated)
        soup = BeautifulSoup(response.content, "html.parser")
        comment_area = soup.find("div", id="comment-area")
        comment_form = comment_area.find("form", id="comment-form")
        self.assertIn("Guestname", comment_form.text)
        response = self.client.post(
            self.post_001.get_absolute_url() + "new_comment/",
            {
                "guest_name": "kkk",
                "guest_password": "123456",
                "content": "로그인 하지 않은 사용자의 댓글입니다",
            },
            follow=True,
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(Comment.objects.count(), 3)

        new_comment = Comment.objects.last()
        soup = BeautifulSoup(response.content, "html.parser")
        self.assertIn(new_comment.post.title, soup.title.text)

        comment_area = soup.find("div", id="comment-area")
        new_comment_div = comment_area.find("div", id=f"comment-{new_comment.pk}")
        self.assertIn("kkk", new_comment_div.text)
        self.assertIn("로그인 하지 않은 사용자의 댓글입니다", new_comment_div.text)

    # 로그인 한 사용자의 댓글 수정
    def test_comment_update(self):
        comment_by_trump = Comment.objects.create(
            post=self.post_001, author=self.user_trump, content="트럼프의 댓글입니다.",
        )

        comment_area = self.get_comment_area(self.post_001)

        self.assertFalse(comment_area.find("a", id="comment-1-update-btn"))
        self.assertFalse(comment_area.find("a", id="comment-2-update-btn"))

        # obama로 로그인 한 상태
        self.client.login(username="obama", password="somepassword")

        comment_area = self.get_comment_area(self.post_001)

        self.assertTrue(comment_area.find("a", id="comment-1-update-btn"))
        self.assertFalse(comment_area.find("a", id="comment-2-update-btn"))

        comment_001_update_btn = comment_area.find("a", id="comment-1-update-btn")
        self.assertIn("댓글수정", comment_001_update_btn.text)

        # 댓글 수정 확인
        response = self.client.post(
            "/blog/update_comment/1/", {"content": "오바마의 댓글을 수정합니다.",}, follow=True
        )

        self.assertEqual(response.status_code, 200)
        soup = BeautifulSoup(response.content, "html.parser")
        comment_001_div = soup.find("div", id="comment-1")
        self.assertIn("오바마의 댓글을 수정합니다.", comment_001_div.text)
        # self.assertIn("Updated: ", comment_001_div.text)

    # 로그인 하지 않은 사용자의 댓글 수정
    # def test_comment_no_user_update(self):
    #     # 로그인 하지 않은 사용자 댓글 추가
    #     # 테스트 코드 작성보다 먼저 브라우저에서 확인을 먼저 하였음
    #     # 추후 작성 예정
    #     pass

    # 로그인 한 사람의 댓글 삭제
    def test_comment_delete(self):
        # 1. 다른 유저가 로그인하여 댓글을 삭제하는 경우는 삭제 취소
        comment_by_trump = Comment.objects.create(
            post=self.post_001, author=self.user_trump, content="트럼프의 댓글 입니다."
        )

        self.assertEqual(Comment.objects.count(), 3)
        self.assertEqual(self.post_001.comment_set.count(), 3)

        # 로그인 하지 않은 상태
        response = self.client.get(self.post_001.get_absolute_url())
        self.assertEqual(response.status_code, 200)
        soup = BeautifulSoup(response.content, "html.parser")

        comment_area = soup.find("div", id="comment-area")
        self.assertFalse(comment_area.find("a", id="comment-1-delete-btn"))
        self.assertFalse(comment_area.find("a", id="comment-3-delete-btn"))

        # trump로 로그인 한 상태
        self.client.login(username="trump", password="somepassword")
        login_success = self.client.login(username="trump", password="somepassword")
        self.assertTrue(login_success)
        response = self.client.get(self.post_001.get_absolute_url())
        self.assertEqual(response.status_code, 200)
        soup = BeautifulSoup(response.content, "html.parser")

        comment_area = soup.find("div", id="comment-area")
        self.assertTrue(comment_area.find("a", id="comment-3-delete-btn"))

        comment_003_delete_modal_btn = comment_area.find("a", id="comment-3-delete-btn")
        self.assertIn("댓글삭제", comment_003_delete_modal_btn.text)

        self.assertEqual(
            comment_003_delete_modal_btn.attrs["data-target"], "#deleteCommentModal-3"
        )

        delete_comment_modal_003 = soup.find("div", id="deleteCommentModal-3")
        self.assertIn("정말 댓글을 삭제하시겠습니까?", delete_comment_modal_003.text)
        really_delete_btn_003 = delete_comment_modal_003.find("button")
        self.assertIn("삭제", delete_comment_modal_003.text)

        form = delete_comment_modal_003.find("form")
        action_url = form.get("action")

        # 링크를 변경해야 함
        self.assertEqual("/blog/delete_comment/3/", action_url)
        response = self.client.post("/blog/delete_comment/3/", follow=True)
        self.assertEqual(response.status_code, 200)
        soup = BeautifulSoup(response.content, "html.parser")
        self.assertIn(self.post_001.title, soup.title.text)
        comment_area = soup.find("div", id="comment-area")
        self.assertNotIn("트럼프의 댓글입니다.", comment_area.text)
        self.assertEqual(self.post_001.comment_set.count(), 2)
