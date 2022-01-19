from django.contrib.auth import get_user_model
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect, render

from .forms import CommentForm, PostForm
from .models import Comment, Follow, Group, Post
from .utils import get_page_obj

User = get_user_model()


def index(request):
    post_list = Post.objects.select_related('group').all()
    context = {
        'page_obj': get_page_obj(post_list, request),
        'page': request.GET.get('page'),
        'index': True,
    }
    return render(request, 'posts/index.html', context)


def group_posts(request, slug):
    group = get_object_or_404(Group, slug=slug)
    post_list = Post.objects.filter(group=group)
    context = {
        'group': group,
        'page_obj': get_page_obj(post_list, request),
    }
    return render(request, 'posts/group_list.html', context)


def profile(request, username):
    author = get_object_or_404(User, username=username)
    user = request.user if request.user.is_authenticated else None
    following = True if Follow.objects.filter(
        user=user,
        author=author
    ).exists() else False
    post_list = Post.objects.filter(author=author)
    context = {
        'author': author,
        'page_obj': get_page_obj(post_list, request),
        'following': following
    }
    return render(request, 'posts/profile.html', context)


def post_detail(request, post_id):
    post = get_object_or_404(Post, pk=post_id)
    form = CommentForm()
    comments = Comment.objects.filter(post=post)
    context = {
        'post': post,
        'form': form,
        'comments': comments,
    }
    return render(request, 'posts/post_detail.html', context)


@login_required
def post_create(request):
    form = PostForm(
        request.POST or None,
        files=request.FILES or None,
    )
    user = request.user
    if form.is_valid():
        new_post = form.save(commit=False)
        new_post.author_id = user.id
        new_post.save()
        return redirect('posts:profile', username=user.username)
    return render(request, 'posts/create_post.html', {'form': form})


@login_required
def post_edit(request, post_id):
    post = get_object_or_404(Post, pk=post_id)
    user = request.user
    if user != post.author:
        return redirect('posts:post_detail', post_id=post.pk)
    form = PostForm(
        request.POST or None,
        files=request.FILES or None,
        instance=post
    )
    if form.is_valid():
        form.save()
        return redirect('posts:post_detail', post_id=post.pk)
    return render(request, 'posts/create_post.html', {'form': form,
                                                      'is_edit': True,
                                                      'post_id': post.pk,
                                                      })


@login_required
def add_comment(request, post_id):
    post = get_object_or_404(Post, pk=post_id)
    form = CommentForm(request.POST or None)
    if form.is_valid:
        comment = form.save(commit=False)
        comment.author = request.user
        comment.post = post
        comment.save()
    return redirect('posts:post_detail', post_id=post_id)


@login_required
def follow_index(request):
    author_list = User.objects.filter(
        following__in=request.user.follower.all()
    )
    post_list = Post.objects.select_related('group').filter(
        author__in=author_list
    )
    context = {
        'page_obj': get_page_obj(post_list, request),
        'follow': True
    }
    return render(request, 'posts/follow.html', context)


@login_required
def profile_follow(request, username):
    author = get_object_or_404(User, username=username)
    user = request.user
    if user == author:
        return redirect('posts:profile', username=username)
    Follow.objects.get_or_create(
        user=user,
        author=author
    )
    return redirect('posts:profile', username=username)


@login_required
def profile_unfollow(request, username):
    author = get_object_or_404(User, username=username)
    user = request.user
    Follow.objects.filter(user=user, author=author).delete()
    return redirect('posts:profile', username=username)
