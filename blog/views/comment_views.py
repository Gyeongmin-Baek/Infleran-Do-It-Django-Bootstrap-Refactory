from django.contrib import messages
from django.contrib.auth.hashers import check_password
from django.core.exceptions import PermissionDenied
from django.shortcuts import get_object_or_404, redirect
from django.views.decorators.http import require_POST

from blog.forms.comment import CommentForm
from blog.models import Comment, Post


# 댓글 생성
@require_POST
def new_comment(request, pk):
    # 여기서 게스트 닉네임과 패스워드 정보를 가지고 와야 함
    post = get_object_or_404(Post, pk=pk)

    # forms에서 init 지정시 사용
    comment_form = CommentForm(data=request.POST, user=request.user)

    if comment_form.is_valid():
        comment = comment_form.save(post)
        return redirect(comment.get_absolute_url())

    else:
        for error in comment_form.errors.values():
            messages.error(request, error)
        return redirect(post.get_absolute_url())


# 댓글 수정
@require_POST
def update_comment(request, pk):
    comment = get_object_or_404(Comment, pk=pk)
    # 로그인한 사용자의 경우
    if request.user.is_authenticated:
        if request.user != comment.author:
            return redirect(comment.get_absolute_url())
        comment_form = CommentForm(
            data=request.POST, instance=comment, user=request.user
        )
    # 로그인하지 않은 사용자의 경우
    else:
        guest_password = comment.guest_password
        # 수정 시에는 폼에서 패스워드를 가져오는게 아님! inpt 태그인 html 태그에서 가져옴!
        # 입력시 해시 솔트는 필요하지 않음
        password = request.POST.get("guest_password")
        # if not (password == comment.guest_password):
        #     return redirect(comment.post.get_absolute_url())

        guest_name = comment.guest_name
        comment_form = CommentForm(
            data=request.POST,
            instance=comment,
            user=request.user,
            guest_name=guest_name,
            password=password,
        )

    if comment_form.is_valid():
        comment_form.save()
        return redirect(comment.get_absolute_url())

    else:
        for error in comment_form.errors.values():
            messages.error(request, error)
        return redirect(comment.post.get_absolute_url())


# 댓글 삭제
@require_POST
def delete_comment(request, pk):
    comment = get_object_or_404(Comment, pk=pk)
    post = comment.post
    parent = comment.parent

    # 대댓글의 특징 - 부모 아이디가 있음
    if request.user.is_authenticated:
        # 요청한 유저와 댓글의 작성자가 같거나 부모 댓글이 있는 경우 삭제
        if request.user == comment.author or parent.pk:
            comment.delete()
            messages.success(request, "댓글을 정상적으로 삭제했습니다.")
            return redirect(post.get_absolute_url())

        else:
            raise PermissionDenied

    else:
        guest_password = comment.guest_password
        # 수정 시에는 폼에서 패스워드를 가져오는게 아님! inpt 태그인 html 태그에서 가져옴!
        password = request.POST.get("guest_password")

        # 해시 암호화 체크
        if check_password(password, guest_password):
            comment.delete()
            messages.success(request, "댓글을 정상적으로 삭제했습니다.")
            return redirect(post.get_absolute_url())
        else:
            raise PermissionDenied


# 댓글추가
def reply_comment(request, post_id, comment_id):
    post = get_object_or_404(Post, pk=post_id)
    comment = get_object_or_404(Comment, pk=comment_id)
    parent = comment.id

    # 로그인 하지 않은 유저는 접근 불가
    if not request.user.is_authenticated:
        raise PermissionDenied

    # forms에서 init 지정시 사용
    comment_form = CommentForm(data=request.POST, user=request.user, parent=parent)

    if comment_form.is_valid():
        comment = comment_form.save(post)
        return redirect(comment.get_absolute_url())

    else:
        redirect(post.get_absolute_url())
