import argparse
import logging
import time
from datetime import datetime
from logging.handlers import RotatingFileHandler

import requests
import telegram
from environs import Env
from requests.exceptions import ConnectionError, ReadTimeout

LOG_FILE_MAX_LEN = 10000000
LOG_FORMAT = '%(asctime)s %(levelname)s:%(message)s'
LOG_DATE_FORMAT = '%Y-%m-%d %H:%M:%S'


class AdminLogsHandler(logging.Handler):

    def emit(self, record):
        log_entry = self.format(record)
        tg_bot.send_message(chat_id=tg_admin, text=log_entry)


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

    parser = argparse.ArgumentParser()
    parser.add_argument('telegram_id', type=str, help='id пользователя Телеграм')
    args = parser.parse_args()

    tg_user = args.telegram_id
    tg_token = env('TG_TOKEN')
    tg_admin = env('TG_ADMIN_USERID')

    devman_token = env('DEVMAM_TOKEN')
    devman_url = env('DEVMAN_URL')

    logger = logging.getLogger("devman_radar")
    logger.setLevel(logging.DEBUG)

    file_handler = RotatingFileHandler(
        filename='devman_radar.log', encoding='utf-8', maxBytes=LOG_FILE_MAX_LEN, backupCount=10)
    file_handler.setFormatter(logging.Formatter(fmt=LOG_FORMAT, datefmt=LOG_DATE_FORMAT))
    file_handler.setLevel(logging.INFO)
    logger.addHandler(file_handler)

    tg_bot = telegram.Bot(tg_token)
    tg_handler = AdminLogsHandler()
    tg_handler.setLevel(logging.DEBUG)
    logger.addHandler(tg_handler)

    logger.info('Мониторинг изменения статуса работ запущен')
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
                logger.info(format_answers(lesson_review['new_attempts']))
        except ConnectionError as e:
            logger.error(f'Ошибка соединения: {e}')
            time.sleep(300)
        except ReadTimeout as e:
            logger.error(f'Ошибка ожидания ответа: {e}')
        except Exception as e:
            logger.error(f'Прочие ошибки: {e}')
