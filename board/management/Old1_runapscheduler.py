import logging
from django.conf import settings

from apscheduler.schedulers.blocking import BlockingScheduler
from apscheduler.triggers.cron import CronTrigger
from django.contrib.auth.models import User
from django.core.mail import EmailMultiAlternatives
from django.core.management.base import BaseCommand
from django.template.loader import render_to_string
from django_apscheduler.jobstores import DjangoJobStore
from django_apscheduler.models import DjangoJobExecution

from django.utils import timezone
import datetime

from board.models import Post

logger = logging.getLogger(__name__)


def weekly_notice():
    """Weekly notification of the latest news by subscribed categories"""
    users = User.objects.all()
    start_date = timezone.now() - datetime.timedelta(weeks=1)
    posts = Post.objects.filter(dateCreation__gte=start_date)
    email_list = [user.email for user in users]

    html_content = render_to_string(
        template_name='mail/weekly_notice.html',
        context={
            'posts': posts,
        },
    )
    msg = EmailMultiAlternatives(
        subject=f'Недельные новости MMORPG',
        body='',
        from_email=settings.DEFAULT_FROM_EMAIL,
        to=email_list,
    )
    msg.attach_alternative(html_content, 'text/html')
    msg.send()


# функция, которая будет удалять неактуальные задачи
def delete_old_job_executions(max_age=604_800):
    """This job deletes all apscheduler job executions older than `max_age` from the database."""
    DjangoJobExecution.objects.delete_old_job_executions(max_age)


class Command(BaseCommand):
    help = "Runs apscheduler."

    def handle(self, *args, **options):
        scheduler = BlockingScheduler(timezone=settings.TIME_ZONE)
        scheduler.add_jobstore(DjangoJobStore(), "default")

        # добавляем работу нашему задачнику
        scheduler.add_job(
            weekly_notice,
            # trigger=CronTrigger(week="*/1"),  # Включение для теста
            trigger=CronTrigger(second="*/10"),  # Включение для теста
            id="weekly_notice",  # уникальный айди
            max_instances=1,
            replace_existing=True,
        )
        logger.info("Added job 'weekly_notice'.")

        scheduler.add_job(
            delete_old_job_executions,
            trigger=CronTrigger(
                day_of_week="mon", hour="00", minute="00"
            ),
            # Каждую неделю будут удаляться старые задачи, которые либо не удалось выполнить,
            # либо уже выполнять не надо.
            id="delete_old_job_executions",
            max_instances=1,
            replace_existing=True,
        )
        logger.info(
            "Added weekly job: 'delete_old_job_executions'."
        )

        try:
            logger.info("Starting scheduler...")
            scheduler.start()
        except KeyboardInterrupt:
            logger.info("Stopping scheduler...")
            scheduler.shutdown()
            logger.info("Scheduler shut down successfully!")



