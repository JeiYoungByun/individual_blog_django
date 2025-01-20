from django.shortcuts import render
from .models import Post, Category, Tag
from django.views.generic import ListView, DetailView

# FBV
# def index(request):
#    posts = Post.objects.all().order_by('-pk')
#
#      return render(
#          request,
#          'blog/post_list.html',
#          {
#             'posts' : posts,
#         }
#     )
#
# def single_post_page(request, pk):
#     post = Post.objects.get(pk=pk)
#
#     return render(
#         request,
#     'blog/post_detail.html',
#     {
#         'post' : post,
#         }
#     )

#CBV
# 게시글 목록을 보여주는 클래스형 뷰
class PostList(ListView):
    model = Post  # Post 모델과 연결
    # template_name = 'blog/post_list.html'  # 기본 템플릿 파일 이름 (주석 처리된 경우, 기본값은 post_list.html)
    ordering = '-pk'  # 게시글을 pk(기본 키) 역순으로 정렬

    # 추가적인 컨텍스트 데이터를 템플릿에 전달
    def get_context_data(self, **kwargs):
        # 부모 클래스의 get_context_data를 호출하여 기본 컨텍스트를 가져옴
        context = super(PostList, self).get_context_data()
        context['categories'] = Category.objects.all()  # 모든 카테고리 목록을 컨텍스트에 추가
        context['no_category_post_count'] = Post.objects.filter(category=None).count()  # 카테고리가 없는 게시글 개수를 추가
        return context  # 컨텍스트 반환

# 특정 카테고리의 게시글 목록을 보여주는 함수형 뷰
def category_page(request, slug):
    if slug == 'no_category':
        # 'no_category' slug가 들어오면 '미분류'로 카테고리를 설정하고, 카테고리가 없는 게시글을 필터링합니다.
        category = '미분류'
        post_list = Post.objects.filter(category=None)
    else:
        # slug 값을 이용하여 해당 카테고리를 가져옵니다.
        category = Category.objects.get(slug=slug)
        post_list = Post.objects.filter(category=category)

    # 페이지를 렌더링하며 필요한 데이터를 전달합니다.
    return render(
        request,
        'blog/post_list.html',  # 렌더링할 템플릿 파일 경로
        {
            'post_list': post_list,  # 현재 카테고리에 해당하는 게시글 목록을 템플릿에 전달
            'categories': Category.objects.all(),  # 모든 카테고리 목록을 템플릿에 전달
            'no_category_post_count': Post.objects.filter(category=None).count(),  # 카테고리가 없는 게시글의 개수를 템플릿에 전달
            'category': category,  # 현재 카테고리 객체를 템플릿에 전달
            }
    )

# 특정 태그페이지를 보여주는 함수형 뷰
def tag_page(request, slug):
    #url에서 인자로 넘어온 slug와 동일한 slug를 쿼리셋에서 가져와 tag에 저장, 태그와 연결된 전체 포스트를 post_list에 저장
    tag = Tag.objects.get(slug=slug)
    post_list = tag.post_set.all()

    # 페이지를 렌더링하며 필요한 데이터를 전달합니다.
    return render(
        request,
        'blog/post_list.html',  # 렌더링할 템플릿 파일 경로
        {
            'post_list': post_list,  # 현재 카테고리에 해당하는 게시글 목록을 템플릿에 전달
            'categories': Category.objects.all(),  # 모든 카테고리 목록을 템플릿에 전달
            'no_category_post_count': Post.objects.filter(category=None).count(),  # 카테고리가 없는 게시글의 개수를 템플릿에 전달
            'tag' : tag,  # 현재 태그 객체를 템플릿에 전달
        }
    )

# 게시글 상세 내용을 보여주는 클래스형 뷰
class PostDetail(DetailView):
    model = Post  # Post 모델과 연결

    # 추가적인 컨텍스트 데이터를 템플릿에 전달
    def get_context_data(self, **kwargs):
        # 부모 클래스의 get_context_data를 호출하여 기본 컨텍스트를 가져옴
        context = super(PostDetail, self).get_context_data()
        context['categories'] = Category.objects.all()  # 모든 카테고리 목록을 컨텍스트에 추가
        context['no_category_post_count'] = Post.objects.filter(category=None).count()  # 카테고리가 없는 게시글 개수를 추가
        return context  # 컨텍스트 반환

