from django.contrib.auth import get_user_model
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.shortcuts import render, get_object_or_404, redirect, reverse

from .forms import PostForm, CommentForm
from .models import Post, Group, Follow, Comment

User = get_user_model()


def index(request):
    post_list = Post.objects.all()
    paginator = Paginator(post_list, 10)
    page_number = request.GET.get('page')
    page = paginator.get_page(page_number)
    return render(request, 'index.html', {'page': page})


def group_posts(request, slug):
    group = get_object_or_404(Group, slug=slug)
    post_list = group.posts.all()
    paginator = Paginator(post_list, 10)
    page_number = request.GET.get('page')
    page = paginator.get_page(page_number)
    return render(request, 'group.html', {'group': group,
                                          'page': page})


@login_required
def new_post(request):
    form = PostForm(request.POST or None)
    if form.is_valid():
        post = form.save(commit=False)
        post.author = request.user
        post.save()
        return redirect('index')
    return render(request, 'new.html', {'form': form, 'is_edit': False})


@login_required
def post_delete(request, username, post_id):
    post = get_object_or_404(Post, author__username=username, id=post_id)
    redirect_url = reverse('index')
    if post.author != request.user:
        return redirect(redirect_url)
    post.delete()
    return redirect(redirect_url)


def profile(request, username):
    user = User.objects.get(username=username)
    posts = user.posts.all()
    paginator = Paginator(posts, 10)
    page_number = request.GET.get('page')
    page = paginator.get_page(page_number)
    number_of_posts = posts.count()
    number_of_following = user.follower.count()
    number_of_followers = user.following.count()
    following = request.user.is_authenticated and Follow.objects.filter(
        user=request.user,
        author__username=username
    ).exists()
    context = {
        'author': user,
        'number_of_posts': number_of_posts,
        'number_of_followers': number_of_followers,
        'number_of_following': number_of_following,
        'page': page,
        'following': following
    }
    return render(request, 'profile.html', context)


def post_view(request, username, post_id):
    form = CommentForm(request.POST or None)

    single_post = get_object_or_404(Post, author__username=username,
                                    id=post_id)
    comments = single_post.comments.all()
    number_of_posts = single_post.author.posts.count()
    number_of_following = single_post.author.follower.count()
    number_of_followers = single_post.author.following.count()
    context = {
        'number_of_posts': number_of_posts,
        'number_of_followers': number_of_followers,
        'number_of_following': number_of_following,
        'post': single_post,
        'form': form,
        'comments': comments,
        'author': single_post.author,
    }
    return render(request, 'post.html', context)


@login_required
def post_edit(request, username, post_id):
    post = get_object_or_404(Post, author__username=username,
                             id=post_id)
    redirect_url = reverse('post', args=[username, post_id])
    if post.author != request.user:
        return redirect(redirect_url)
    form = PostForm(request.POST or None,
                    files=request.FILES or None,
                    instance=post)
    if request.POST and form.is_valid():
        form.save()
        return redirect(redirect_url)
    return render(request,
                  'new.html',
                  {'form': form,
                   'author': username,
                   'post': post,
                   'is_edit': True, }
                  )


def page_not_found(request, exception):
    return render(
        request,
        "misc/404.html",
        {"path": request.path},
        status=404
    )


def server_error(request):
    return render(request, "misc/500.html", status=500)


@login_required
def add_comment(request, username, post_id):
    post = get_object_or_404(Post, author__username=username, id=post_id)
    form = CommentForm(request.POST or None)
    if form.is_valid():
        comment = form.save(commit=False)
        comment.author = request.user
        comment.post = post
        comment.save()
        return redirect('post', username, post_id)
    return render(request, 'includes/comments.html', {'form': form, 'post':
                  post, 'author': username})


@login_required
def comment_delete(request, username, post_id, comment_id):
    comment = get_object_or_404(
        Comment,
        author__username=request.user.username,
        id=comment_id)
    redirect_url = reverse('post', args=[username, post_id])
    if comment.author != request.user:
        return redirect(redirect_url)
    comment.delete()
    return redirect(redirect_url)


@login_required
def follow_index(request):
    post_list = Post.objects.filter(author__following__user=request.user)
    paginator = Paginator(post_list, 10)
    page_number = request.GET.get('page')
    page = paginator.get_page(page_number)
    return render(request, 'follow.html', {
        'page': page,
        'paginator': paginator})


@login_required
def profile_follow(request, username):
    if username == request.user.username:
        return redirect('follow_index')
    Follow.objects.get_or_create(
        user=request.user,
        author=get_object_or_404(User, username=username)
    )
    return redirect('follow_index')


@login_required
def profile_unfollow(request, username):
    instance = Follow.objects.get(
        user=request.user,
        author=get_object_or_404(User, username=username)
    )
    instance.delete()
    return redirect('follow_index')


def search_results(request):
    if request.method == 'POST':
        searched = request.POST['searched']
        posts = Post.objects.filter(text__contains=searched)
        return render(
            request,
            'search_results.html',
            {'searched': searched, 'posts': posts})
    return render(request, 'search_results.html')
