from django.shortcuts import render, redirect, get_object_or_404
from .models import Post, Category, Tag, Comment
from django.views.generic import ListView, DetailView, CreateView, UpdateView
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.core.exceptions import PermissionDenied
from django.utils.text import slugify
from .forms import CommentForm
from django.db.models import Q

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
    paginate_by = 5

    # 추가적인 컨텍스트 데이터를 템플릿에 전달
    def get_context_data(self, **kwargs):
        # 부모 클래스의 get_context_data를 호출하여 기본 컨텍스트를 가져옴
        context = super(PostList, self).get_context_data()
        context['categories'] = Category.objects.all()  # 모든 카테고리 목록을 컨텍스트에 추가
        context['no_category_post_count'] = Post.objects.filter(category=None).count()  # 카테고리가 없는 게시글 개수를 추가
        return context  # 컨텍스트 반환

# 게시글 상세 내용을 보여주는 클래스형 뷰
class PostDetail(DetailView):
    model = Post

    # 추가적인 컨텍스트 데이터를 템플릿에 전달
    def get_context_data(self, **kwargs):
        # 부모 클래스의 get_context_data를 호출하여 기본 컨텍스트를 가져옴
        context = super(PostDetail, self).get_context_data()
        context['categories'] = Category.objects.all()  # 모든 카테고리 목록을 컨텍스트에 추가
        context['no_category_post_count'] = Post.objects.filter(category=None).count()  # 카테고리가 없는 게시글 개수를 추가

        post = self.get_object()  # 현재 게시글 가져오기

        context['comment_form'] = CommentForm(post=post) # 현재 게시글을 댓글 폼에 전달

        return context  # 컨텍스트 반환


class PostCreate(LoginRequiredMixin, UserPassesTestMixin, CreateView):
    # Post 모델과 연결된 뷰로, 게시글을 생성하는 역할을 합니다.
    model = Post

    # 폼에서 입력받을 필드를 정의합니다.
    fields = ['title', 'hook_text', 'content', 'head_image', 'file_upload', 'category']

    def test_func(self):
        # 사용자가 superuser(관리자)거나 staff(스태프)일 경우 True를 반환합니다.
        # 그렇지 않으면 False를 반환하여 접근을 제한합니다.
        return self.request.user.is_superuser or self.request.user.is_staff

    def form_valid(self, form):
        # 현재 요청을 보낸 사용자를 가져옵니다.
        current_user = self.request.user

        # 사용자가 인증된 상태(로그인 상태)인지 확인하고, 관리자 또는 스태프인지 추가 확인합니다.
        if current_user.is_authenticated and (current_user.is_staff or current_user.is_superuser):
            # 폼의 author 필드에 현재 사용자를 할당합니다.
            form.instance.author = current_user
            # 부모 클래스의 form_valid 메서드를 호출하여 폼 제출을 처리하고 응답을 가져옵니다.
            response = super(PostCreate, self).form_valid(form)

            # POST 요청에서 'tags_str' 값을 가져옵니다.
            tags_str = self.request.POST.get('tags_str')
            if tags_str:
                # 태그 문자열의 앞뒤 공백을 제거합니다.
                tags_str = tags_str.strip()

                # 쉼표를 세미콜론으로 대체하여 구분자를 표준화합니다.
                tags_str = tags_str.replace(',', ';')

                # 세미콜론을 기준으로 태그 문자열을 개별 태그 목록으로 분리합니다.
                tags_list = tags_str.split(';')

                # 각 태그에 대해 반복 처리합니다.
                for t in tags_list:
                    # 태그의 앞뒤 공백을 제거합니다.
                    t = t.strip()

                    # 이름으로 Tag 객체를 가져오거나, 존재하지 않으면 새로 생성합니다.
                    tag, is_tag_created = Tag.objects.get_or_create(name=t)

                    # 새로 생성된 Tag인 경우, 슬러그를 생성하고 저장합니다.
                    if is_tag_created:
                        tag.slug = slugify(t, allow_unicode=True)
                        tag.save()

                    # 해당 태그를 게시물의 태그 필드에 추가합니다.
                    self.object.tags.add(tag)

            # 부모 클래스의 form_valid 메서드에서 반환된 응답을 반환합니다.
            return response

        else:
            # 사용자가 인증되지 않았거나 권한이 없는 경우, 블로그 메인 페이지로 리디렉션합니다.
            return redirect('/blog/')

class PostUpdate(LoginRequiredMixin, UpdateView):
    model = Post
    fields = ['title', 'hook_text', 'content', 'head_image', 'file_upload', 'category', 'tags']

    template_name = 'blog/post_update_form.html'

    def get_context_data(self, **kwargs):
        context = super(PostUpdate, self).get_context_data()
        if self.object.tags.exists():
            tags_str_list = list()
            for t in self.object.tags.all():
                tags_str_list.append(t.name)
            context['tags_str_default'] = '; '.join(tags_str_list)

        return context

    def dispatch(self, request, *args, **kwargs):
        # 사용자가 인증되었는지 확인하고, 현재 사용자가 해당 객체의 작성자인지 확인
        if request.user.is_authenticated and request.user == self.get_object().author:
            # 조건이 만족되면, 부모 클래스(PostUpdate)의 dispatch 메서드를 호출하여 요청을 처리
            return super(PostUpdate, self).dispatch(request, *args, **kwargs)
        else:
            # 인증되지 않았거나 작성자가 아닐 경우, PermissionDenied 예외를 발생시켜 접근을 차단
            raise PermissionDenied

    def form_valid(self, form):
        # 부모 클래스(PostUpdate)의 form_valid 메서드를 호출하여 기본 동작 수행
        response = super(PostUpdate, self).form_valid(form)

        # 현재 게시글(self.object)에 연결된 모든 태그를 초기화 (기존 태그 제거)
        self.object.tags.clear()

        # 클라이언트가 입력한 'tags_str' 값을 가져옴 (POST 요청에서 전달된 태그 문자열)
        tags_str = self.request.POST.get('tags_str')

        if tags_str:
            # 앞뒤 공백 제거
            tags_str = tags_str.strip()

            # 쉼표(,)를 세미콜론(;)으로 변경하여 일관된 구분자로 변환
            tags_str = tags_str.replace(',', ';')

            # 세미콜론(;)을 기준으로 문자열을 분리하여 태그 리스트 생성
            tags_list = tags_str.split(';')

            # 태그 리스트를 순회하며 개별 태그 처리
            for t in tags_list:
                # 개별 태그 문자열의 앞뒤 공백 제거
                t = t.strip()

                # 태그 이름을 기준으로 데이터베이스에서 조회하거나 새로 생성
                tag, is_tag_created = Tag.objects.get_or_create(name=t)

                # 새롭게 생성된 태그라면 slug 필드를 설정 후 저장
                if is_tag_created:
                    tag.slug = slugify(t, allow_unicode=True)
                    tag.save()

                # 현재 게시글(self.object)에 태그 추가
                self.object.tags.add(tag)

        # 부모 클래스의 form_valid 메서드에서 반환된 response를 그대로 반환
        return response

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

def new_comment(request, pk):
    # 로그인하지 않은 경우 permissiondenied 발생
    if request.user.is_authenticated:
        post = get_object_or_404(Post, pk=pk)

        # POST 방식으로 전달
        if request.method == 'POST':
            comment_form = CommentForm(request.POST)
            if comment_form.is_valid():
                comment = comment_form.save(commit=False) # 저장 잠시 보류
                comment.post = post # 댓글의 게시물 설정
                comment.author = request.user # 현재 로그인한 사용자로 설정

                # parent가 존재하는 경우 직접 설정
                parent_id = request.POST.get('parent')
                if parent_id:
                    comment.parent = Comment.objects.get(pk=parent_id)

                comment.save() # 데이터베이스에 저장
                return redirect(comment.get_absolute_url())
            else:
                return redirect(post.get_absolute_url())
    else:
        raise PermissionDenied

class CommentUpdate(LoginRequiredMixin, UpdateView):
    model = Comment
    form_class = CommentForm

    def dispatch(self, request, *args, **kwargs):
        if request.user.is_authenticated and request.user == self.get_object().author:
            return super(CommentUpdate, self).dispatch(request, *args, **kwargs)
        else:
            raise PermissionDenied

def delete_comment(request, pk):
    comment = get_object_or_404(Comment, pk=pk)
    post = comment.post
    if request.user.is_authenticated and request.user == comment.author:
        comment.delete()
        return redirect(post.get_absolute_url())
    else:
        raise PermissionDenied

class PostSearch(PostList):
    paginate_by = None

    def get_queryset(self):
        q = self.kwargs['q'] # 검색어를 q에 저장
        post_list = Post.objects.filter(
            Q(title__contains=q) | Q(tags__name__contains=q) # title에 q를 포함했거나 tags의 name에 q를 포함한 post 레코드를 db에서 가져옴
        ).distinct() # distinct()은 중복이 있을 때 한번만 나타나게함
        return post_list

    def get_context_data(self, **kwargs):
        context = super(PostSearch, self).get_context_data()
        q = self.kwargs['q']
        context['search_info'] = f'Search: {q} ({self.get_queryset().count()})'

        return context