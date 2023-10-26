from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.cache import cache
from django.http import HttpResponse
from django.urls import reverse_lazy
from django.utils import timezone

from django.shortcuts import redirect
from django.contrib.auth.models import User

from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView

from .forms import ReplyForm, PostForm
from .models import Post, Reply
from .filters import ReplyFilter
from .tasks import notify_accept_reply, notify_new_reply


class PostListView(ListView):
    model = Post
    template_name = 'board/posts.html'
    context_object_name = 'posts'
    ordering = ['-dateCreation']
    paginate_by = 3

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['time_now'] = timezone.localtime(timezone.now())  # добавим переменную текущей даты time_now
        context['posts_count'] = Post.objects.all().count()  # добавим переменную кол-во постов
        return context


class PostDetailView(DetailView, CreateView):
    model = Post
    form_class = ReplyForm
    template_name = 'board/post_detail.html'
    context_object_name = 'post'

    def form_valid(self, form):
        reply = form.save(commit=False)
        reply.author = User.objects.get(id=self.request.user.id)
        reply.post = Post.objects.get(id=self.kwargs.get('pk'))
        reply.save()
        notify_new_reply(reply.id)
        return redirect('board:posts')

    # D7.4 Кэширование на низком уровне (смотри еще модель Post метод save)
    def get_object(self, *args, **kwargs):  # переопределяем метод получения объекта, как ни странно
        obj = cache.get(f'post-{self.kwargs["pk"]}', None)  # кэш очень похож на словарь, и
        # метод get действует также. Он забирает значение по ключу, если его нет, то забирает None.

        # если объекта нет в кэше, то получаем его и записываем в кэш
        if not obj:
            obj = super().get_object(queryset=self.queryset)
            cache.set(f'post-{self.kwargs["pk"]}', obj)
        return obj


class PostCreateView(LoginRequiredMixin, CreateView):
    template_name = 'board/post_create.html'
    form_class = PostForm

    def form_valid(self, form):
        post = form.save(commit=False)
        post.author = User.objects.get(id=self.request.user.id)
        post.save()
        return redirect('board:posts')


class PostUpdateView(LoginRequiredMixin, UpdateView):
    template_name = 'board/post_update.html'
    form_class = PostForm

    def get_object(self, **kwargs):
        id_pk = self.kwargs.get('pk')
        return Post.objects.get(pk=id_pk)

    def dispatch(self, request, *args, **kwargs):
        if self.request.user == Post.objects.get(pk=self.kwargs.get('pk')).author:
            return super().dispatch(request, *args, **kwargs)
        else:
            return HttpResponse('<h3>ACCESS DENIED!</h3>Изменять или удалять можно только свои объявления!')


class PostDeleteView(LoginRequiredMixin, DeleteView):
    template_name = 'board/post_delete.html'
    queryset = Post.objects.all()
    success_url = reverse_lazy('board:posts')
    permission_required = ('board.delete_post',)

    def dispatch(self, request, *args, **kwargs):
        if self.request.user == Post.objects.get(pk=self.kwargs.get('pk')).author:
            return super().dispatch(request, *args, **kwargs)
        else:
            return HttpResponse('<h3>ACCESS DENIED!</h3>Изменять или удалять можно только свои объявления!')


class CategoryDetailView(ListView):
    model = Post
    template_name = 'board/posts.html'
    context_object_name = 'posts'
    ordering = ['-id']
    paginate_by = 3

    def get_queryset(self):
        cat_key = self.kwargs['cat_key']
        queryset = Post.objects.filter(category=cat_key)
        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        cat_key = self.kwargs['cat_key']
        cat_display = self.kwargs['cat_disp']
        context['category'] = cat_display
        context['posts_count'] = Post.objects.filter(category=cat_key).count()  # добавим переменную кол-во постов
        context['time_now'] = timezone.localtime(timezone.now())  # добавим переменную текущей даты time_now
        return context


class AuthorPostsListView(ListView):
    model = Post
    template_name = 'board/posts.html'
    context_object_name = 'posts'
    ordering = ['-id']
    paginate_by = 3

    def get_queryset(self):
        author_pk = self.kwargs['author_pk']
        queryset = Post.objects.filter(author_id=author_pk)
        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        author_pk = self.kwargs['author_pk']
        context['author'] = User.objects.get(pk=author_pk)
        context['posts_count'] = Post.objects.filter(author_id=author_pk).count()  # добавим переменную кол-во постов
        context['time_now'] = timezone.localtime(timezone.now())  # добавим переменную текущей даты time_now
        return context


class ReplyListView(ListView):
    model = Reply
    template_name = 'board/show_replies.html'
    context_object_name = 'replies'

    def get_queryset(self):
        return super().get_queryset().filter(post_id__author_id=self.request.user)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['filter'] = ReplyFilter(self.request.GET, queryset=self.get_queryset())
        return context


def accept_reply(*args, **kwargs):
    reply = Reply.objects.get(id=kwargs.get('pk'))
    reply.accepted = True
    reply.save()
    notify_accept_reply(reply.id)
    return redirect('board:show_replies')


def delete_reply(*args, **kwargs):
    reply = Reply.objects.get(id=kwargs.get('pk'))
    reply.delete()
    return redirect('board:show_replies')


