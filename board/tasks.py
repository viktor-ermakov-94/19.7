from django.conf import settings
from django.core.mail import send_mail
from .models import Reply


def notify_new_reply(pk):
    reply = Reply.objects.get(id=pk)
    send_mail(
        subject=f'MMORPG - Новый отклик на ваше объявление!',
        message=f'Привет, {reply.post.author}!\n'
                f'На ваше объявление "{reply.post.title}" есть новый отклик.\n'
                f'Автор, {reply.author} ответил следующее:\n "{reply.text}", ',
        from_email=settings.DEFAULT_FROM_EMAIL,
        recipient_list=[reply.post.author.email, ],
    )


def notify_accept_reply(pk):
    reply = Reply.objects.get(id=pk)
    send_mail(
        subject=f'MMORPG - Ваш отклик принят!',
        message=f'Привет, {reply.author}!\n'
                f'Ваш отклик на объявление "{reply.post.title}" принят.\n'
                f'Посмотреть объявление целиком можно по ссылке:\n'
                f'http://127.0.0.1:8000/{reply.post.id}',
        from_email=settings.DEFAULT_FROM_EMAIL,
        recipient_list=[reply.author.email, ],
    )

