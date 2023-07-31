from django import forms

from blog.models import Category


class CategoryForm(forms.ModelForm):
    class Meta:
        model = Category
        fields = ["name"]
        widgets = {
            "name": forms.TextInput(
                attrs={"type": "text", "class": "form-control", "id": "textInput"}
            )
        }


# 이거 아직 에러 못찾음!
class CreateCategoryForm(CategoryForm):
    def clean_name(self):
        name = self.cleaned_data["name"]
        if len(name) < 3:
            raise forms.ValidationError("카테고리 이름은 최소 3자 이상으로 설정해 주세요")

        if Category.objects.filter(name=name).exists():
            raise forms.ValidationError("동일한 카테고리가 있습니다. 다른 카테고리를 생성해 주세요.")

        return name


class UpdateCategoryForm(CategoryForm):

    # 여기서는 clean의 본래 기능을 끔 - 모델 필드 정의에 대한 unique=True를 끔
    # 카테고리 포스트들을 이동하기 위함
    def clean(self):
        self._validate_unique = False
        return self.cleaned_data

    # def clean_name(self):
    #     name = self.cleaned_data["name"]
    #     if len(name) < 3:
    #         raise forms.ValidationError("카테고리 이름은 최소 3자 이상으로 설정해 주세요")
    #     return name


class DeleteCategoryForm(CategoryForm):

    # 삭제하는 경우는 선택지가 없음 따라서 폼을 초기화하여 False로 변경
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["name"].required = False
