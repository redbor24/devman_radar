import argparse
import logging
from datetime import datetime

import requests
import telegram
from environs import Env
from requests.exceptions import ConnectionError, ReadTimeout


def check_devman_answers(devmam_token, devman_url, tg_userid):
    moment = datetime.now().timestamp()
    while True:
        try:
            logging.info('Ожидание изменения статуса работ с: '
                         f'{datetime.fromtimestamp(moment).strftime("%Y-%m-%d %H:%M:%S")}')
            headers = {
                'authorization': devmam_token,
                'timestamp': str(moment)
            }
            response = requests.get(devman_url, headers=headers)
            response.raise_for_status()
            resp_data = response.json()
            if resp_data['status'] == 'timeout':
                moment = resp_data['timestamp_to_request']
            if resp_data['status'] == 'found':
                moment = resp_data['last_attempt_timestamp']
                send_message(tg_userid, format_answers(resp_data['new_attempts']))
        except (ReadTimeout, ConnectionError):
            logging.warning('No server answer...')


def format_answers(devman_answers):
    formatted_answer = ''
    for answer in devman_answers:
        answer_text = f'Работа "{answer["lesson_title"]}" проверена.\n{answer["lesson_url"]}'
        if answer['is_negative']:
            answer_result = 'Работа не принята. Перейдите по ссылке, чтобы посмотреть замечания ментора.'
        else:
            answer_result = 'Работа принята!'
        answer_text = answer_text + f'\nРезультат: {answer_result}'
        formatted_answer = f'{formatted_answer} {answer_text}\n'

    return formatted_answer


def send_message(chat_userid, message):
    bot = telegram.Bot(TG_TOKEN)
    bot.send_message(chat_id=chat_userid, text=message)
    logging.info('Отправлено в Телеграм:')
    logging.info(f'  Сообщение: {message}')
    logging.info(f'  Пользователь: {chat_userid}')


if __name__ == '__main__':
    env = Env()
    env.read_env()

    logging.basicConfig(
        filename='devman_radar.log', encoding='utf-8', level=logging.INFO,
        format='%(asctime)s %(levelname)s:%(message)s', datefmt='%Y-%m-%d %H:%M:%S'
    )
    logging.info('Начало работы')
    logging.info('Программа отслеживает изменения статусов работ ученика на сайте devman.org '
                 'и оповещает об этом через Телеграм')
    logging.info('Для завершения работы нажмите Ctrl+C или закройте окно CMD.exe')

    parser = argparse.ArgumentParser()
    parser.add_argument('Telegram_ID', type=str, help='ID пользователя Телеграм')
    args = parser.parse_args()
    TG_USERID = args.Telegram_ID

    TG_TOKEN = env('TG_TOKEN')
    DEVMAM_TOKEN = env('DEVMAM_TOKEN')
    DEVMAN_URL = env('DEVMAN_URL')

    check_devman_answers(DEVMAM_TOKEN, DEVMAN_URL, TG_USERID)
