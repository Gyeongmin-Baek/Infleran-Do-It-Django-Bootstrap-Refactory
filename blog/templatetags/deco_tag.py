from django import template
from os.path import basename, splitext

register = template.Library()


# 파일명 가져오기
@register.filter
def filename(value):
    return basename(value)


# 파일 확장자 가져오기
@register.filter
def file_extension(value):
    return splitext(value)[1][1:]


# 파일 확장자 font-awesome 매칭 시키기
FILE_TYPE_ICONS = {
    "txt": "fa-file-alt",
    "pdf": "fa-file-pdf",
    "doc": "fa-file-word",
    "docx": "fa-file-word",
    "xls": "fa-file-excel",
    "xlsx": "fa-file-excel",
    "ppt": "fa-file-powerpoint",
    "pptx": "fa-file-powerpoint",
}

# 파일 확장자에 맞는 형식 가져오기
@register.filter
def file_icon(value):
    file_format = file_extension(value)
    return FILE_TYPE_ICONS.get(file_format, "fa-file")


# 파일 크기 가져오기
@register.filter
def filesize(value):
    return round(value / (1024 ** 2), 2)
