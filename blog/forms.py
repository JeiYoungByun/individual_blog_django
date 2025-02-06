from django import forms
from .models import Comment

class CommentForm(forms.ModelForm):
    parent = forms.ModelChoiceField(
        queryset=Comment.objects.all(),
        required=False,  # 최상위 댓글(부모가 없는 댓글)도 가능해야 함
        widget=forms.Select(attrs={'class': 'form-control'})  # 선택 UI 적용
    )

    class Meta:
        model = Comment
        fields = ('content', 'parent')  # 부모 댓글을 선택할 수 있도록 추가

    def __init__(self, *args, **kwargs):
        post = kwargs.pop('post', None)  # 추가된 post 인자를 받아옴
        super().__init__(*args, **kwargs)  # 부모 클래스의 __init__() 실행

        if post:
            # 특정 게시글(post)에 속한 댓글만 부모 댓글 선택 가능
            self.fields['parent'].queryset = Comment.objects.filter(post=post)