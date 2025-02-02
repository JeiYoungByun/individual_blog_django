from django.db import models
from django.contrib.auth.models import User
from markdownx.models import MarkdownxField
from markdownx.utils import markdown
import os


# 모델을 생성하는 코드입니다.
class Category(models.Model):
    name = models.CharField(max_length=50, unique=True)  # 카테고리 이름 (최대 50자, 고유값 설정)
    slug = models.SlugField(max_length=200, unique=True, allow_unicode=True)  # URL에 사용할 슬러그 (유니코드 허용)

    def __str__(self):
        return self.name  # 카테고리 이름을 문자열로 반환

    def get_absolute_url(self):
        return f'/blog/category/{self.slug}/'  # 특정 카테고리로 이동하는 URL 반환

    class Meta:
        verbose_name_plural = 'Categories'  # Admin 페이지에서 복수형 이름 설정

class Tag(models.Model):
    name = models.CharField(max_length=50, unique=True)  # 카테고리 이름 (최대 50자, 고유값 설정)
    slug = models.SlugField(max_length=200, unique=True, allow_unicode=True)  # URL에 사용할 슬러그 (유니코드 허용)

    def __str__(self):
        return self.name  # 카테고리 이름을 문자열로 반환

    def get_absolute_url(self):
        return f'/blog/tag/{self.slug}/'  # 특정 카테고리로 이동하는 URL 반환


class Post(models.Model):
    title = models.CharField(max_length=30)  # 게시글 제목 (최대 30자)
    hook_text = models.CharField(max_length=100, blank=True)  # 게시글 소개 글 (최대 100자, 선택 사항)
    content = MarkdownxField()  # 게시글 내용

    head_image = models.ImageField(upload_to='blog/images/%Y/%m/%d/', blank=True)  # 헤더 이미지 (선택 사항)
    file_upload = models.FileField(upload_to='blog/files/%Y/%m/%d/', blank=True)  # 파일 업로드 (선택 사항)

    created_at = models.DateTimeField(auto_now_add=True)  # 생성 시간 (자동 기록)
    updated_at = models.DateTimeField(auto_now=True)  # 수정 시간 (자동 업데이트)

    author = models.ForeignKey(User, null=True, on_delete=models.SET_NULL)  # 작성자 (User 모델과 연결, 삭제 시 Null 처리)

    category = models.ForeignKey(Category, null=True, blank=True, on_delete=models.SET_NULL)  # 카테고리 (선택 사항)

    tags = models.ManyToManyField(Tag, blank=True) # manytomanyfields로 tag을 다대다관계로 구현

    def __str__(self):
        return f'[{self.pk}]{self.title} :: {self.author}'  # 게시글 ID와 제목, 작성자 정보 반환

    def get_absolute_url(self):
        return f'/blog/{self.pk}/'  # 특정 게시글로 이동하는 URL 반환

    def get_file_name(self):
        return os.path.basename(self.file_upload.name)  # 업로드된 파일의 이름 반환

    def get_file_ext(self):
        return self.get_file_name().split('.')[-1]  # 업로드된 파일의 확장자 반환

    def get_content_markdown(self):
        return markdown(self.content)

