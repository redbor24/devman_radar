## Скрипт для отслеживания уведомлений о проверке работ на платформе [devman.org](dvmn.org)
На платформе devman.org ученики в процессе обучения выполняют различные задания. По завершению работы над заданием
ученик отправляет его на проверку ментору и ждёт ответа. Однако платформа не предоставляет никакой возможности 
подписаться на уведомления об изменении статуса сданной работы. Данный скрипт исправляет это досадное недоразумение
через Телеграм-бота [DevManRadar_bot](https://t.me/rdbDevManRadar_bot).

### Для кого предназначен скрипт
Скрипт предназначен для учеников, выполняющих задания на платформе [devman.org](dvmn.org)
Остальным он просто не нужен да и токен платформы они получить не смогут...

### Подготовка к работе
Для работы у вас должен быть установлен `Python 3`.

Скачайте проект [devman_radar](https://github.com/redbor24/devman_radar):
```
git clone git@github.com:redbor24/devman_radar.git 
```

Установите зависимости:
```
pip install -r requirements.txt
```

Создайте Телеграм-бота через обращение к [Bot-father](https://t.me/BotFather).
Откройте в Телеграм диалог с ботом и нажмите кнопку "Старт". Это необходимо, чтобы бот "узнал" вас.

[Получите](https://dvmn.org/api/docs/) свой токен для devman-API.

Создайте файл `.env` следующего содержания:
```
DEVMAN_URL=https://dvmn.org/api/long_polling/
TG_TOKEN=<токен, полученный от Bot-father>
TG_ADMIN_USERID=<>
DEVMAM_TOKEN=<devman_API token>
```

Откройте в Телеграм диалог с ботом [Get My ID](https://t.me/getmyid_bot) и запишите "Your user ID".
`TG_ADMIN_USERID` это Id Телеграм-пользователя, которому будут отправляться сообщения о состояинии бота.
Перед использованием бота этому пользователю нужно так же начать диалог с ботом.

### Использование скрипта
Откройте окно CMD.exe, перейдите в каталог скрипта и выполните:
```commandline
python devman_radar.py "Your user ID"
```

Все сообщения, возникающие в процессе работы скрипта, пишутся в файл лога `devman_radar.log` в каталоге скрипта.

Когда сданная на проверку работа будет проверена платформа [devman.org](dvmn.org) сгенерирует сообщение, которое
бот отправит вам в Телеграм.