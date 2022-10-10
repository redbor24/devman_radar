import argparse
import logging
import time
from datetime import datetime

import requests
import telegram
from environs import Env
from requests.exceptions import ConnectionError, ReadTimeout


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
    parser.add_argument('telegram_id', type=str, help='id пользователя Телеграм')
    args = parser.parse_args()

    tg_userid = args.telegram_id
    tg_token = env('TG_TOKEN')

    devman_token = env('DEVMAM_TOKEN')
    devman_url = env('DEVMAN_URL')

    bot = telegram.Bot(tg_token)
    message = 'Мониторинг изменения статуса работ запущен'
    logging.info(message)
    bot.send_message(chat_id=tg_userid, text=message)
    check_from = datetime.now().timestamp()
    while True:
        try:
            headers = {
                'authorization': devman_token,
                'timestamp': str(check_from)
            }
            response = requests.get(devman_url, headers=headers)
            response.raise_for_status()
            lesson_review = response.json()
            if lesson_review['status'] == 'timeout':
                check_from = lesson_review['timestamp_to_request']
            if lesson_review['status'] == 'found':
                check_from = lesson_review['last_attempt_timestamp']
                formatted_message = format_answers(lesson_review['new_attempts'])

                bot.send_message(chat_id=tg_userid, text=formatted_message)
                logging.info('Отправлено в Телеграм:')
                logging.info(f'  Сообщение: {formatted_message}')
                logging.info(f'  Пользователь: {tg_userid}')
        except ConnectionError as e:
            logging.error(f'Ошибка соединения: {e}')
            time.sleep(300)
        except ReadTimeout as e:
            message = f'Ошибка ожидания ответа: {e}'
            logging.error(message)
            bot.send_message(chat_id=tg_userid, text=message)
        except Exception as e:
            message = f'Прочие ошибки: {e}'
            logging.error(message)
            bot.send_message(chat_id=tg_userid, text=message)
