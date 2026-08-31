# FastAI

Сервис для генерации HTML-страниц с помощью AI

## Быстрый запуск проекта

Инструкция для быстрого запуска проекта (проверялось на ubuntu 22.04). За подробной инcтрукцией запуска для разработчиков обращаться к документу `CONTRIBUTING.md`.

### Необходимое ПО

Для работы проекта в системе должны быть установлены следующие программы:

- Git - система контроля версий
- Make - утилита для автоматизации преобразования файлов из одной формы в другую
- uv - менеджер пакетов
- MinIO - S3 сервис (bucket)


Способ установки указанных программ на Ubuntu:

```shell
sudo apt update && sudo apt install -y git make # git, make
curl -LsSf https://astral.sh/uv/install.sh | sh # uv
```

Проверка, если программа установлена, в терминал должна вывестись её версия:

```shell
git --version
make --version
uv --version
```

### Клонирование репозитория и настройка окружения

Для того чтобы склонировать репозиторий, используйте команду:

```shell
git clone https://github.com/KamenskiyIlya/fastai.git 
git clone git@github.com:KamenskiyIlya/fastai.git # через SSH
```
После того как репозиторий склонирован - зайдите в папку и настройте окружение:

```shell
cd fastai
uv sync # создает окружение, устанавливает зависимости и нужную версию python
source .venv/bin/activate # активируем окружение
pre-commit install # Настройка pre-commit хуков чтобы автоматически запускать линтеры и автотесты при коммитах
# вывод должнен быть pre-commit installed at .git/hooks/pre-commit
```

### Установка и запуск MinIO (кратко, для больших подробностей см. CONTRIBUTING.md)

Проект хранит ссылки на сайты и скриншоты в S3 хранилище, поэтому без запущенного MinIO backend не работает.
Кратко для Ubuntu 22.04:

1. Скачайте и установите сервер:

```shell
wget https://dl.min.io/server/minio/release/linux-amd64/minio.deb
sudo dpkg -i minio.deb
sudo mkdir -p /var/lib/minio
sudo chown -R minio-user:minio-user /var/lib/minio
```
2. Запишите конфиг в `/etc/default/minio`:

```shell
MINIO_ROOT_USER="ваш_логин"
MINIO_ROOT_PASSWORD="ваш_пароль"
MINIO_VOLUMES="/var/lib/minio"
MINIO_OPTS="--address :9000 --console-address :9001"
```
3. Запустите сервис:

```shell
sudo systemctl enable --now minio
```
4. Создайте бакет и сделайте его публичным (через веб-интерфейс http://127.0.0.1:9001 или клиент `mcli`). Подробная инструкция в CONTRIBUTING.md.

### Настройка переменных окружения (.env)

1. Скопируйте шаблон `example.env` и откройте режим редактирования в терминале(или в любом удобном редакторе):
```shell
cp example.env .env
nano .env
```
> файл `.env` должен быть обязательно добавлен в `.gitignore` т.к. содержит чувствительные данные

2. Заполните обязательные переменные - без них проект не запустится, не обязательные при необходимости, если знаете зачем:

| Переменная | Обязательная | Default | Где взять |
|---|---|---|---|
| `DEEPSEEK__API_KEY` | да | - | В ЛК [DeepSeek](https://platform.deepseek.com/api_keys) или в агрегаторе, которым пользуетесь
| `UNSPLASH__CLIENT_ID` | да | - | `https://unsplash.com/developers` -> New App -> страница с созданным приложением -> Access Key |
| `DEEPSEEK__BASE_URL` | нет (если default) | `https://api.deepseek.com` | базовый url агрегатора, которым пользуетесь(обычно в ЛК) |
| `DEEPSEEK__MODEL` | нет (если default) | `deepseek-chat` | модель, которой пользуетесь, уточняйте на сайте агрегатора |
| `S3__ACCESS_KEY` | да | - | логин от бакета (в MinIO - `MINIO_ROOT_USER`) |
| `S3__SECRET_KEY` | да | - | пароль от бакета (в MinIO - `MINIO_ROOT_PASSWORD`) |
| `S3__BUCKET_NAME` | да | - | имя бакета в MinIO (например `fastai-html`) |
| `S3__BUCKET_URL` | нет (если default) | `http://127.0.0.1:9000` | endpoint сервера с портом |
| `S3__REGION_NAME` | нет | `us-east-1` | регион бакета (по умолчанию `us-east-1`, если не задавали явно) |
| `S3__MAX_POOL_CONNECTIONS` | нет | `10` | лимит одновременных подключений к бакету |
| `S3__CONNECT_TIMEOUT` | нет | `20` | таймаут подключения к бакету, сек |
| `S3__READ_TIMEOUT` | нет | `30` | таймаут чтения из бакета, сек |
| `DEBUG` | нет | `False` | `True` или `False` - отвечает за дебаг режим |

После настройке переходите к запуску проекта, при запуске, если все указано правильно, Вы увидетев терминале все инициализированные переменные в таком формате:
```json
{
  "deepseek": {
    "api_key": "**********",
    "base_url": "https://openai.bothub.ru/v1",
    "model": "deepseek-v4-flash-0731",
    "max_connections": 10
  },
  "unsplash": {
    "client_id": "**********",
    "max_connections": 10,
    "timeout": 30
  },
  "s3": {
    "access_key": "**********",
    "secret_key": "**********",
    "bucket_name": "fastai-html",
    "bucket_url": "http://127.0.0.1:9000",
    "region_name": "us-east-1",
    "max_pool_connections": 9,
    "connect_timeout": 19,
    "read_timeout": 29
  },
  "debug": true
}
```
### Подключение фронтенда

Backend раздаёт фронтенд из папки `frontend/`, но она добавлена в `.gitignore`, её нужно руками положить в локальную папку с проектом. Без этой папки проект не будет работать.

1. Скачайте [архив фронтенда](https://dvmn.org/filer/canonical/1750917110/1035/)
2. Распакуйте архив в корень проекта:
```shell
unzip .../frontend.zip -d .
```
3. Создайте и настройте frontend/frontend-settings.json:
```shell
touch frontend/frontend-settings.json
```
и запишите в него:
```json
{
    "backendBaseUrl": "/"
}
```

### Запуск

```shell
fastapi dev src/main.py
```

Как понять что запуск прошел успешно:

- в терминале появилось сообщение `Server started at http://127.0.0.1:8000`
- внизу в logs нет сообщений об ошибках.

Для того чтобы остановить сервер - нажмите сочетание клавиш `Ctrl+C`.