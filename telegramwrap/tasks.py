from datetime import datetime

from telethon.events import NewMessage
from telethon.tl.types import UpdateNewMessage

from telegramwrap.celery import app
from telegramwrap.models import WebhookUrl, TelegramAuthorization
from telegramwrap.utils import Telegram
import requests
from django.core.cache import cache



@app.task
def get_webhooks():
    objs = list(WebhookUrl.objects.values_list('url', flat=True))
    return objs



@app.task
def attach_messagehook(phone):
    if cache.get('taskId') is not None:
        print("revoking {0}".format(cache.get("taskId")))
        app.control.revoke(cache.get("taskId"), terminate=True)
    else:
        print("not revoking", cache.get("taskId"))
    client = Telegram.get_client(phone)
    auth = TelegramAuthorization.objects.get(phone=phone)
    if not auth.telegram_id:
        auth.telegram_id = client.get_me().id
        auth.save()
    client.updates.workers = 1
    client.add_event_handler(handler, event=NewMessage, authobj=auth)
    client.idle()


@app.task
def handler(event, auth):
    headers = {'Content-type': 'application/json', 'Accept': 'application/json'}
    try:
        #print(event.message.to_dict())
        data = {
            "messages": [
                {
                    "id": event.message.id,
                    "body": event.message.message or event.message,
                    "from": event.message.from_id,
                    "chat": {"id": event.chat.id,
                             "first_name": event.chat.first_name,
                             "last_name": event.chat.last_name,
                             "username": event.chat.username,
                             "phone": event.chat.phone},
                    "time": str(int(datetime.timestamp(event.message.date))),
                    "to": {"id": auth.telegram_id,
                           "phone": auth.phone},
                    "fromMe": event.out,
                    "type": "chat"
                }
            ]
        }
        print(data)
        for url in get_webhooks():
            r = requests.post(url, json=data, headers=headers)
            print(r.status_code, r.text)
    except Exception as exc:
        print(exc)

