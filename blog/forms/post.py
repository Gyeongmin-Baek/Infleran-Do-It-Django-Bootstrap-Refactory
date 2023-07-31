from django import forms

from blog.models import Post


class PostForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        # ModelForm의 init에 author_pk를 저장하지 않음
        self.author_pk = kwargs.pop("author_pk", None)
        super().__init__(*args, **kwargs)

    Tags = forms.CharField(
        required=False,
        widget=forms.TextInput(
            attrs={
                "placeholder": "태그 (태그 간 띄워쓰기 및 태그 구분은 `,` 또는 `;`로 해주세요. 예시: python ; 장고, 기타)",
            }
        ),
        help_text="태그 간 띄워쓰기 및 태그 구분은 `,` 또는 `;`로 해주세요. 예시: python ; 장고, 기타",
    )

    class Meta:
        model = Post
        fields = [
            "title",
            "hook_text",
            "content",
            "head_image",
            "file_upload",
            "category",
        ]

    # clean을 사용하기 이전 먼저 view에 form_isvalid()가 호출되어야 함
    def clean_Tags(self):
        tags_str = self.cleaned_data["Tags"]
        # 만약 tags_str이 유효하지 않다면, ValidationError를 발생시킵니다.
        # 예: if not data: raise forms.ValidationError("This field is required.")
        if tags_str:
            tags_str = tags_str.strip()
            tags_str = tags_str.replace(",", ";")
        return tags_str

    def save(self, commit=True):
        post = super().save(commit=False)
        post.author_id = self.author_pk
        if commit:
            post.save()
        return post
