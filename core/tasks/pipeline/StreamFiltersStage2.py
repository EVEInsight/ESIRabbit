from core.celery import app
from core.tasks.BaseTasks.BaseTask import BaseTask
from core.models.Mail.Mail import Mail
from core.models.Stream.Stream import Stream
from .StreamFiltersStage3 import StreamFiltersStage3


@app.task(base=BaseTask, bind=True, max_retries=5, default_retry_delay=60, autoretry_for=(Exception,))
def StreamFiltersStage2(self, mail_json, stream_json) -> None:
    m = Mail.from_json(mail_json)
    s = Stream.from_json(stream_json)

    StreamFiltersStage3.apply_async(kwargs={"mail_json": mail_json, "stream_json": stream_json}, ignore_result=True)

