import datetime
import logging

from django.conf import settings

from apscheduler.schedulers.blocking import BlockingScheduler
from apscheduler.triggers.cron import CronTrigger
from django.contrib.auth.models import User
from django.core.mail import send_mail
from django.core.management.base import BaseCommand
from django_apscheduler.jobstores import DjangoJobStore
from django_apscheduler.models import DjangoJobExecution
from datetime import timedelta

from ...models import Post

logger = logging.getLogger(__name__)


def sending_weekly_news():
    start_date = datetime.date.today() - timedelta(days=6)
    users = User.objects.all()
    posts = Post.objects.filter(date_c__gte=start_date)
    email_list = [user.email for user in users]
    news_list = ''

    for post in posts:
        news_list += f'{post.title} http://127.0.0.1:8000/{post.id}\n'

    send_mail(
        subject=f'MMORPG - news for the week',
        message=f'Добрый день, уважаемый пользователь портала MMORPG!\n'
                f'Вот новые объявления за последнюю неделю:\n'
                f'{news_list}',
        from_email=settings.DEFAULT_FROM_EMAIL,
        recipient_list=email_list,
    )


# функция которая будет удалять неактуальные задачи
def delete_old_job_executions(max_age=604_800):
    """This job deletes all apscheduler job executions older than `max_age` from the database."""
    DjangoJobExecution.objects.delete_old_job_executions(max_age)


class Command(BaseCommand):
    help = "Runs apscheduler."

    def handle(self, *args, **options):
        scheduler = BlockingScheduler(timezone=settings.TIME_ZONE)
        scheduler.add_jobstore(DjangoJobStore(), "default")

        scheduler.add_job(
            sending_weekly_news,
            trigger=CronTrigger(week="*/1"),
            id="sending_weekly_news",
            max_instances=1,
            replace_existing=True,
        )
        logger.info("Added job 'sending_weekly_news'.")

        scheduler.add_job(
            delete_old_job_executions,
            trigger=CronTrigger(
                day_of_week="mon", hour="00", minute="00"
            ),
            # Каждую неделю будут удаляться старые задачи, которые либо не удалось выполнить, либо уже выполнять не надо.
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
