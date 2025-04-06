from appmail.models import AppmailMessage, EmailTemplate

from config.celery_app import app


@app.task(name="tasks.send_email")
def send_email(template_name, context, receiver):
    message = AppmailMessage(
        template=EmailTemplate.objects.current(template_name),
        context=context,
        to=receiver,
    )
    message.send()
