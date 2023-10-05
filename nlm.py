import eddy_collect
from config import slack_token
import logging

from slack_sdk import WebClient
from slack_sdk.errors import SlackApiError

import time

slack_token = slack_token
client = WebClient(token=slack_token)


channel_id = "CCPT7J0GN"  # nightline
# channel_id = "C05974NHZ96"  # innachannel
# channel_id = "C058PJHTDEH" # innatest


logging.basicConfig(filename='nlm.log', level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def collect_data():
    prosrok = eddy_collect.get_prosrok()
    queue = eddy_collect.get_queue()
    open = eddy_collect.get_open()
    expert = eddy_collect.get_expert()
    message = f''':aaaaaa: _[Быстрая линия]_ Просрок - *{prosrok}*

:bender: _[Быстрая линия]_ Очередь - *{queue}*

:cattytiping: _[Быстрая линия]_ Открытые - *{open}*

:axeleshik: _[Быстрая линия]_ Эксперт - *{expert}*

---
powered by crontab
'''

    return message

retry_counter = 0

def send_message():
    global retry_counter
    logging.info(f'start send_message')

    current_hour = int(time.strftime("%H"))
    if 0 <= current_hour < 15:
        trigger_message = "Reminder: В 9:00 отправить количество открытых чатов в тред"
    else:
        trigger_message = "Reminder: Ровно в 21:00 прислать в тред кол-во открытых чатов + дату изменения самого старого чата"
    try:
        response = client.conversations_history(channel=channel_id)
        messages = response.get("messages",'')
        if messages:
            logging.info(f'conversation history collect successfull')
            for message in messages:
                if message["text"] == trigger_message:
                    parent_message_ts = message["ts"]
                    logging.info('parent message from slack find successfull')
                    hde_counter = collect_data()
                    client.chat_postMessage(channel=channel_id, thread_ts=parent_message_ts, text=hde_counter)
                    logging.info('message to slack send')
                    break
        else:
            logging.error(f'couldnt get slack history. response = {response}')
            raise Exception("Invalid response from Slack API")
    except SlackApiError as e:
        logging.error(f"Error from Slack API: {e.response['error']}")
        retry_counter += 1
        logging.info(f"New launch attempt. Attempt {retry_counter} out of 5.")
        send_message()

