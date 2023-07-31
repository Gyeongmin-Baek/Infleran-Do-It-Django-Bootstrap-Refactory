# from django import forms
# from django.contrib.auth.hashers import check_password, make_password
#
# from .models import Category, Comment, Post
#
#
# class PostForm(forms.ModelForm):
#     def __init__(self, *args, **kwargs):
#         # ModelForm의 init에 author_pk를 저장하지 않음
#         self.author_pk = kwargs.pop("author_pk", None)
#         super().__init__(*args, **kwargs)
#
#     Tags = forms.CharField(
#         required=False,
#         widget=forms.TextInput(
#             attrs={
#                 "placeholder": "태그 (태그 간 띄워쓰기 및 태그 구분은 `,` 또는 `;`로 해주세요. 예시: python ; 장고, 기타)",
#             }
#         ),
#         help_text="태그 간 띄워쓰기 및 태그 구분은 `,` 또는 `;`로 해주세요. 예시: python ; 장고, 기타",
#     )
#
#     class Meta:
#         model = Post
#         fields = [
#             "title",
#             "hook_text",
#             "content",
#             "head_image",
#             "file_upload",
#             "category",
#         ]
#
#     # clean을 사용하기 이전 먼저 view에 form_isvalid()가 호출되어야 함
#     def clean_Tags(self):
#         tags_str = self.cleaned_data["Tags"]
#         # 만약 tags_str이 유효하지 않다면, ValidationError를 발생시킵니다.
#         # 예: if not data: raise forms.ValidationError("This field is required.")
#         if tags_str:
#             tags_str = tags_str.strip()
#             tags_str = tags_str.replace(",", ";")
#         return tags_str
#
#     def save(self, commit=True):
#         post = super().save(commit=False)
#         post.author_id = self.author_pk
#         if commit:
#             post.save()
#         return post
#
#
# class CommentForm(forms.Form):
#
#     content = forms.CharField(
#         widget=forms.Textarea(
#             attrs={
#                 "class": "form-control",
#                 "id": "content",
#                 "rows": "2",
#                 "placeholder": "대댓글은 로그인한 사용자만 이용할 수 있습니다",
#             }
#         )
#     )
#
#     def __init__(self, *args, **kwargs):
#         # 폼 자체에 입력을 받지 않기 때문에 인자값에서 pop을 해줌
#         # 폼 생성시 값을 넣는게 아니라 폼 저장시 값을 넣기 때문
#         # 폼 생성시 초기화 값이기에 리다이렉트 후 값이 생기는건 당연함
#         self.user = kwargs.pop("user", None)
#         self.instance = kwargs.pop("instance", None)
#         self.guest_name = kwargs.pop("guest_name", None)
#         self.password = kwargs.pop("password", None)
#         self.parent = kwargs.pop("parent", None)
#         # 대댓글 작성시
#         super().__init__(*args, **kwargs)
#         # 댓글 생성시만 댓글이 있을때 한번 더 초기화 하면 큰일남!
#         # 폼 초기화는 Get 요청 Post 요청 모든 요청이 올 때마다 초기화 됨!
#
#         if not (self.user and self.user.is_authenticated) and self.guest_name is None:
#             self.fields["guest_name"] = forms.CharField(
#                 required=True,
#                 widget=forms.TextInput(
#                     attrs={
#                         "class": "form-control",
#                         "id": "guest_name",
#                         "placeholder": "닉네임은 최대 29자리 이하로 입력해 주세요",
#                     }
#                 ),
#             )
#             self.fields["guest_password"] = forms.CharField(
#                 required=True,
#                 widget=forms.PasswordInput(
#                     attrs={
#                         "class": "form-control",
#                         "id": "guest_password",
#                         "placeholder": "패스워드는 4자리 이상 입력해 주세요",
#                     }
#                 ),
#             )
#
#     def clean_guest_password(self):
#         password = self.cleaned_data.get("guest_password")
#         if len(password) < 4:
#             raise forms.ValidationError("패스워드는 최소 4자리 이상으로 설정해 주세요")
#         return password
#
#     def clean(self):
#         # 로그인 하지 않은 사용자만 해당됨
#         # 로그인 하지 않은 사용자가 새로 댓글을 쓰는 상황
#         # 로그인 하지 않은 사용자가 댓글을 수정하려는 상황
#         # 핵심 : 게스트 네임 정보를 self.guest_name
#         if not (self.user and self.user.is_authenticated):
#             # 댓글 생성시 필요한 정보 기입
#             guest_name = self.cleaned_data.get("guest_name")
#             password = self.cleaned_data.get("guest_password")
#
#             if guest_name:
#                 comment = Comment.objects.filter(guest_name=guest_name).first()
#                 if comment and not check_password(password, comment.guest_password):
#                     raise forms.ValidationError("동일한 이름의 패스워드가 일치하지 않습니다.")
#             # 댓글 수정 요청 시 guest_name이 인자로 들어오지 않으므로 별도 체크
#             if self.guest_name:
#                 comment = Comment.objects.filter(guest_name=self.guest_name).first()
#                 # 수정 시에는 폼에서 패스워드를 가져오는게 아님! inpt 태그인 html 태그에서 가져옴!
#                 # 따라서 당연히 폼의 유효성 검사를 하는 cleaned data에는 password가 없는게 당연함!
#                 if not check_password(self.password, comment.guest_password):
#                     raise forms.ValidationError("수정하려는 내용의 패스워드가 일치하지 않습니다.")
#
#     def save(self, post=None, commit=True):
#         # update 요청
#         if self.instance:
#             comment = self.instance
#             comment.content = self.cleaned_data["content"]
#
#         # create 요청
#         else:
#             comment_data = {"content": self.cleaned_data["content"], "post": post}
#             if self.user and self.user.is_authenticated:
#                 comment_data["author_id"] = self.user.pk
#             else:
#                 comment_data["guest_name"] = self.cleaned_data["guest_name"]
#                 comment_data["guest_password"] = make_password(
#                     self.cleaned_data["guest_password"]
#                 )
#
#             # 대댓글 생성에는 댓글 부모의 id가 있으므로
#             # 댓글 부모의 id가 있는 경우 추가로 comment_data에 저장
#             if self.parent:
#                 comment_data["parent_id"] = self.parent
#
#             comment = Comment(**comment_data)
#
#         if commit:
#             comment.save()
#
#         return comment
