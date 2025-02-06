from django.contrib import admin
from markdownx.admin import MarkdownxModelAdmin
from .models import Post, Category, Tag, Comment
from mptt.admin import MPTTModelAdmin

# Post 모델을 기본 설정으로 관리자(admin) 페이지에 등록
admin.site.register(Post, MarkdownxModelAdmin)


# Category 모델에 대한 관리자 페이지 설정
class CategoryAdmin(admin.ModelAdmin):
    # slug 필드를 name 필드를 기반으로 자동 생성
    prepopulated_fields = {'slug': ('name', )}

# Tag 모델에 대한 관리자 페이지 설정
class TagAdmin(admin.ModelAdmin):
    # slug 필드를 name 필드를 기반으로 자동 생성
    prepopulated_fields = {'slug': ('name', )}

class CommentAdmin(MPTTModelAdmin):
    mptt_level_indent = 20  # 트리 구조에서 들여쓰기 설정

# Category와 Tag 모델을 관리자 페이지에 등록하면서 커스터마이징한 Admin 클래스를 사용
admin.site.register(Category, CategoryAdmin)
admin.site.register(Tag, TagAdmin)
admin.site.register(Comment, CommentAdmin)



