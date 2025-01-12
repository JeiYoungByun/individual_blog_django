from django.contrib import admin
from .models import Post, Category, Tag

# Post 모델을 기본 설정으로 관리자(admin) 페이지에 등록
admin.site.register(Post)

# Category 모델에 대한 관리자 페이지 설정
class CategoryAdmin(admin.ModelAdmin):
    # slug 필드를 name 필드를 기반으로 자동 생성
    prepopulated_fields = {'slug': ('name', )}

# Tag 모델에 대한 관리자 페이지 설정
class TagAdmin(admin.ModelAdmin):
    # slug 필드를 name 필드를 기반으로 자동 생성
    prepopulated_fields = {'slug': ('name', )}

# Category와 Tag 모델을 관리자 페이지에 등록하면서 커스터마이징한 Admin 클래스를 사용
admin.site.register(Category, CategoryAdmin)
admin.site.register(Tag, TagAdmin)