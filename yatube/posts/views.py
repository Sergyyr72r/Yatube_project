from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.db.models import F
from django.shortcuts import get_object_or_404, redirect, render

from .utils import paginator
from .forms import CommentForm, PostForm
from .models import Group, Post, Follow


def index(request):
    posts_list = Post.objects.select_related('group', 'author').all()
    context = {
        'page_obj': paginator(posts_list, request),
    }
    return render(request, 'posts/index.html', context)


def group_posts(request, slug):
    group = get_object_or_404(Group, slug=slug)
    posts_list = group.posts.select_related('author').all()
    page_obj = paginator(posts_list, request)
    context = {
        'group': group,
        'page_obj': page_obj,
    }
    return render(request, 'posts/group_list.html', context)


def profile(request, username):
    author = get_object_or_404(User, username=username)
    posts = author.posts.select_related('group').all()
    page_obj = paginator(posts, request)
    following = request.user.is_authenticated and Follow.objects.filter(
        author=author, user=request.user.pk).exists()
    context = {
        'page_obj': page_obj,
        'author': author,
        'following': following,
    }
    return render(request, 'posts/profile.html', context)


def post_detail(request, post_id):
    post = get_object_or_404(Post, pk=post_id)
    form = CommentForm()
    if request.method in ['DELETE', 'POST'] and request.user == post.author:
        post.delete()
        return redirect('posts:profile', username=request.user)
    Post.objects.filter(pk=post.pk).update(views=F('views') + 1)
    return render(request, 'posts/post_detail.html',
                  {'post': post,
                   'form': form,
                   'comments': post.comments.all}
                  )


@login_required
def post_create(request):
    form = PostForm(request.POST or None, files=request.FILES or None)
    if not form.is_valid():
        return render(request, 'posts/create_post.html', {'form': form})
    post = form.save(commit=False)
    post.author = request.user
    post.save()
    return redirect('posts:profile', username=request.user)


@login_required
def post_edit(request, post_id):
    post = get_object_or_404(Post, pk=post_id)
    if not request.user == post.author:
        return redirect('posts:post_detail', post_id)
    form = PostForm(request.POST or None,
                    instance=post,
                    files=request.FILES or None
                    )
    if form.is_valid():
        form.save()
        return redirect('posts:post_detail', post_id)
    return render(request, 'posts/create_post.html', {'form': form})


@login_required
def add_comment(request, post_id):
    form = CommentForm(request.POST or None)
    post = Post.objects.get(id=post_id)
    if form.is_valid():
        comment = form.save(commit=False)
        comment.author = request.user
        comment.post = post
        comment.save()
    return redirect('posts:post_detail', post_id=post_id)


@login_required
def follow_index(request):
    user = request.user
    posts_list = Post.objects.select_related('author', 'group').filter(
        author__following__user=user
    )
    page_obj = paginator(posts_list, request)
    context = {
        'page_obj': page_obj
    }
    return render(request, 'posts/follow.html', context)


@login_required
def profile_follow(request, username):
    author = get_object_or_404(User, username=username)
    if request.user != author:
        Follow.objects.get_or_create(
            user=request.user,
            author=author,
        )
    return redirect('posts:profile', username=username)


@login_required
def profile_unfollow(request, username):
    Follow.objects.filter(author__username=username).delete()
    return redirect('posts:profile', username=username)
