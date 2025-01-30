from django.test import TestCase, Client
from bs4 import BeautifulSoup
from django.contrib.auth.models import User
from .models import Post, Category, Tag

# Create your tests here.
class TestView(TestCase):
    def setUp(self):
        self.client = Client()
        self.user_trump = User.objects.create_user(username='trump', password='somepassword')
        self.user_obama = User.objects.create_user(username='obama', password='somepassword')
        self.user_obama.is_staff = True
        self.user_obama.save()

        self.category_programming = Category.objects.create(name='programming', slug='programming')
        self.category_music = Category.objects.create(name='music', slug='music')

        self.tag_python_kor = Tag.objects.create(name='파이썬 공부', slug='파이썬-공부')
        self.tag_python = Tag.objects.create(name='python', slug='python')
        self.tag_hello = Tag.objects.create(name='hello', slug='helo')

        self.post_001 = Post.objects.create(
            title='첫 번째 포스트입니다.',
            content='Hello World. We are the world',
            category=self.category_programming,
            author=self.user_trump
        )
        self.post_001.tags.add(self.tag_hello)

        self.post_002 = Post.objects.create(
            title='두 번째 포스트입니다.',
            content='1등이 전부는 아니잖아요?',
            category=self.category_music,
            author=self.user_obama
        )

        self.post_003 = Post.objects.create(
            title='세 번째 포스트입니다.',
            content='category가 없을 수도 있죠',
            author=self.user_obama
        )
        self.post_003.tags.add(self.tag_python_kor)
        self.post_003.tags.add(self.tag_python)

    def navbar_test(self, soup):
        navbar = soup.nav
        self.assertIn('Blog', navbar.text)
        self.assertIn('About Me', navbar.text)

        logo_btn = navbar.find('a', text='Do It Django')
        self.assertEqual(logo_btn.attrs['href'], '/')

        home_btn = navbar.find('a', text='Home')
        self.assertEqual(home_btn.attrs['href'], '/')

        blog_btn = navbar.find('a', text='Blog')
        self.assertEqual(blog_btn.attrs['href'], '/blog/')

        about_me_btn = navbar.find('a', text='About Me')
        self.assertEqual(about_me_btn.attrs['href'], '/about_me/')

    def category_card_test(self, soup):
        categories_card = soup.find('div', id='categories-card')
        self.assertIn('Categories', categories_card.text)
        self.assertIn(f'{self.category_programming.name} ({self.category_programming.post_set.count()})', categories_card.text)
        self.assertIn(f'{self.category_music.name} ({self.category_music.post_set.count()})', categories_card.text)
        self.assertIn(f'미분류 (1)', categories_card.text)

    def test_post_list(self):
        #포스트가 있는 경우
        self.assertEqual(Post.objects.count(), 3)

        response = self.client.get('/blog/')
        self.assertEqual(response.status_code, 200)
        soup = BeautifulSoup(response.content, 'html.parser')

        self.navbar_test(soup)
        self.category_card_test(soup)

        main_area = soup.find('div', id='main-area')
        self.assertNotIn('아직 게시물이 없습니다', main_area.text)

        post_001_card = main_area.find('div', id='post-1')
        self.assertIn(self.post_001.title, post_001_card.text)
        self.assertIn(self.post_001.category.name, post_001_card.text)
        self.assertIn(self.post_001.author.username.upper(), post_001_card.text)
        self.assertIn(self.tag_hello.name, post_001_card.text)
        self.assertNotIn(self.tag_python.name, post_001_card.text)
        self.assertNotIn(self.tag_python_kor.name, post_001_card.text)

        post_002_card = main_area.find('div', id='post-2')
        self.assertIn(self.post_002.title, post_002_card.text)
        self.assertIn(self.post_002.category.name, post_002_card.text)
        self.assertIn(self.post_002.author.username.upper(), post_002_card.text)
        self.assertNotIn(self.tag_hello.name, post_002_card.text)
        self.assertNotIn(self.tag_python.name, post_002_card.text)
        self.assertNotIn(self.tag_python_kor.name, post_002_card.text)

        post_003_card = main_area.find('div', id='post-3')
        self.assertIn('미분류', post_003_card.text)
        self.assertIn(self.post_003.title, post_003_card.text)
        self.assertIn(self.post_003.author.username.upper(), post_003_card.text)
        self.assertNotIn(self.tag_hello.name, post_003_card.text)
        self.assertIn(self.tag_python.name, post_003_card.text)
        self.assertIn(self.tag_python_kor.name, post_003_card.text)

        self.assertIn(self.user_trump.username.upper(), main_area.text)
        self.assertIn(self.user_obama.username.upper(), main_area.text)

        # 포스트가 없는 경우
        Post.objects.all().delete()
        self.assertEqual(Post.objects.count(), 0)
        response = self.client.get('/blog/')
        soup = BeautifulSoup(response.content, 'html.parser')

        main_area = soup.find('div', id='main-area')
        self.assertIn('아직 게시물이 없습니다', main_area.text)

    def test_post_detail(self):

        # 1.2. 그 포스트의 url은 '/blog/1/'이다.
        self.assertEqual(self.post_001.get_absolute_url(), '/blog/1/')

        # 2. 첫 번째 포스트의 상세 페이지 테스트

        # 2.1. 첫 번째 포스트의 url로 접근하면 정상적으로 작동한다(status code: 200).
        response = self.client.get(self.post_001.get_absolute_url())
        self.assertEqual(response.status_code, 200)
        soup = BeautifulSoup(response.content, 'html.parser')

        # 2.2. 포스트 목록 페이지와 똑같은 내비게이션 바가 있다.
        self.navbar_test(soup)

        self.category_card_test(soup)

        # 2.3. 첫 번째 포스트의 제목이 웹 브라우저 탭 타이틀에 들어 있다.
        self.assertIn(self.post_001.title, soup.title.text)

        # 2.4. 첫 번째 포스트의 제목이 포스트 영역에 있다.
        main_area = soup.find('div', id='main-area')
        post_area = main_area.find('div', id='post-area')
        self.assertIn(self.post_001.title, post_area.text)

        # 2.5. 첫 번째 포스트의 작성자(author)가 포스트 영역에 있다.
        self.assertIn(self.user_trump.username.upper(), post_area.text)

        # 2.6. 첫 번째 포스트의 내용(content)이 포스트 영역에 있다.
        self.assertIn(self.post_001.content, post_area.text)

        self.assertIn(self.tag_hello.name, post_area.text)
        self.assertNotIn(self.tag_python.name, post_area.text)
        self.assertNotIn(self.tag_python_kor.name, post_area.text)

    def test_category_page(self):
        # self.category_programming의 url을 가져와서 페이지가 잘 열리는지 검사
        response = self.client.get(self.category_programming.get_absolute_url())
        self.assertEqual(response.status_code, 200)

        # html parsing한 후 네비게이션 바와 category card를 테스트
        soup = BeautifulSoup(response.content, 'html.parser')
        self.navbar_test(soup)
        self.category_card_test(soup)

        # 페이지 상단 뱃지 이름이 잘 나타나는지 확인
        self.assertIn(self.category_programming.name, soup.h1.text)

        # main area에 programming있는지 확인하고 post1만 있는지 확인
        main_area = soup.find('div', id='main-area')
        self.assertIn(self.category_programming.name, main_area.text)
        self.assertIn(self.post_001.title, main_area.text)
        self.assertNotIn(self.post_002.title, main_area.text)
        self.assertNotIn(self.post_003.title, main_area.text)

    def test_tag_page(self):
        # tag_hello의 url을 가져와서 페이지가 잘 열리는지 검사
        response = self.client.get(self.tag_hello.get_absolute_url())
        self.assertEqual(response.status_code, 200)

        # html parsing한 후 네비게이션 바와 category card를 테스트
        soup = BeautifulSoup(response.content, 'html.parser')
        self.navbar_test(soup)
        self.category_card_test(soup)

        # 페이지 상단 뱃지 이름이 잘 나타나는지 확인
        self.assertIn(self.tag_hello.name, soup.h1.text)

        # main area에 programming있는지 확인하고 post1만 있는지 확인
        main_area = soup.find('div', id='main-area')
        self.assertIn(self.tag_hello.name, main_area.text)
        self.assertIn(self.post_001.title, main_area.text)
        self.assertNotIn(self.post_002.title, main_area.text)
        self.assertNotIn(self.post_003.title, main_area.text)

    def test_create_post(self):
        # 로그인하지 않으면 statuscode가 200이면 안됨
        response = self.client.get('/blog/create_post/')
        self.assertNotEqual(response.status_code, 200)

        # staff가 아닌 trump가 로그인을 한다.
        self.client.login(username='trump', password='somepassword')
        response = self.client.get('/blog/create_post/')
        self.assertNotEqual(response.status_code, 200)

        # staff인 obama로 로그인한다.
        self.client.login(username='obama', password='somepassword')
        response = self.client.get('/blog/create_post/')
        self.assertEqual(response.status_code, 200)
        soup = BeautifulSoup(response.content, 'html.parser')

        self.assertEqual('Create Post - Blog', soup.title.text)
        main_area = soup.find('div', id='main-area')
        self.assertIn('Create New Post', main_area.text)

        tag_str_input = main_area.find('input', id='id_tags_str')
        self.assertTrue(tag_str_input)

        self.client.post(
            '/blog/create_post/',
            {
                'title' : 'Post Form 만들기',
                'content' : "Post Form 페이지를 만듭시다.",
                'tags_str': 'new tag; 한글 태그, python'
            }
        )
        self.assertEqual(Post.objects.count(), 4)
        last_post = Post.objects.last()
        self.assertEqual(last_post.title, "Post Form 만들기")
        self.assertEqual(last_post.author.username, 'obama')

        self.assertEqual(last_post.tags.count(), 3)
        self.assertTrue(Tag.objects.get(name='new tag'))
        self.assertTrue(Tag.objects.get(name='한글 태그'))
        self.assertEqual(Tag.objects.count(), 5)

    def test_update_post(self):
        update_post_url = f'/blog/update_post/{self.post_003.pk}/'

        # 경우 1: 로그인하지 않은 상태에서 업데이트 페이지에 접근
        response = self.client.get(update_post_url)
        self.assertNotEqual(response.status_code, 200, "인증되지 않은 사용자는 포스트 수정 페이지에 접근할 수 없어야 합니다.")

        # 경우 2: 로그인은 했지만 작성자가 아닌 사용자가 접근
        self.assertNotEqual(self.post_003.author, self.user_trump, "user_trump는 post_003의 작성자가 아니어야 합니다.")
        login_successful = self.client.login(
            username=self.user_trump.username,
            password='somepassword'
        )
        self.assertTrue(login_successful, "user_trump로 로그인하는 데 실패했습니다.")
        response = self.client.get(update_post_url)
        self.assertEqual(response.status_code, 403, "작성자가 아닌 사용자는 403 Forbidden 응답을 받아야 합니다.")

        # 경우 3: 작성자(obama)로 로그인하여 업데이트 페이지에 접근
        login_successful = self.client.login(
            username=self.post_003.author.username,
            password='somepassword'
        )
        self.assertTrue(login_successful, "작성자로 로그인하는 데 실패했습니다.")
        response = self.client.get(update_post_url)
        self.assertEqual(response.status_code, 200, "작성자는 포스트 수정 페이지에 접근할 수 있어야 합니다.")

        # 응답 내용을 BeautifulSoup으로 파싱
        soup = BeautifulSoup(response.content, 'html.parser')

        # 페이지 제목 확인
        self.assertEqual('Edit Post - Blog', soup.title.text, "페이지 제목이 'Edit Post - Blog'이어야 합니다.")

        # 페이지의 메인 영역 찾기
        main_area = soup.find('div', id='main-area')
        self.assertIn('Edit Post', main_area.text, "메인 영역에 'Edit Post'가 포함되어야 합니다.")

        # 메인 영역에 'id_tags_str' ID를 가진 input 요소가 있는지 확인
        tag_str_input = main_area.find('input', id='id_tags_str')
        self.assertTrue(tag_str_input, "메인 영역에 'id_tags_str' ID를 가진 input 요소가 있어야 합니다.")
        self.assertIn('파이썬 공부; python', tag_str_input.attrs['value'], "태그 문자열에 '파이썬 공부; python'이 포함되어야 합니다.")

        # POST 요청을 통해 포스트 수정
        response = self.client.post(
            update_post_url,
            {
                'title': '세 번째 포스트를 수정했습니다.',
                'content': '안녕 세계? 우리는 하나!',
                'category': self.category_music.pk,
                'tags_str': '파이썬 공부; 한글 태그, some tag'
            },
            follow=True
        )

        # POST 요청 후 응답 내용을 다시 파싱
        soup = BeautifulSoup(response.content, 'html.parser')
        main_area = soup.find('div', id='main-area')

        # 수정된 내용이 메인 영역에 포함되어 있는지 확인
        self.assertIn('세 번째 포스트를 수정했습니다.', main_area.text, "수정된 제목이 메인 영역에 포함되어야 합니다.")
        self.assertIn('안녕 세계? 우리는 하나!', main_area.text, "수정된 내용이 메인 영역에 포함되어야 합니다.")
        self.assertIn(self.category_music.name, main_area.text, "수정된 카테고리가 메인 영역에 포함되어야 합니다.")
        self.assertIn('파이썬 공부', main_area.text, "태그 '파이썬 공부'가 메인 영역에 포함되어야 합니다.")
        self.assertIn('한글 태그', main_area.text, "태그 '한글 태그'가 메인 영역에 포함되어야 합니다.")
        self.assertIn('some tag', main_area.text, "태그 'some tag'가 메인 영역에 포함되어야 합니다.")

        # 업데이트 후 'python' 태그가 더 이상 포함되지 않았는지 확인
        self.assertNotIn('python', main_area.text, "업데이트 후 태그 'python'이 더 이상 포함되지 않아야 합니다.")
