# FastAI

Сервис для генерации HTML-страниц с помощью AI

## Быстрый запуск проекта

Инструкция для быстрого запуска проекта (проверялось на ubuntu 22.04). За подробной инcтрукцией запуска для разработчиков обращаться к документу `CONTRIBUTING.md`.

### Необходимое ПО

Для работы проекта в системе должны быть установлены следующие программы:

- [Git SCM](https://git-scm.com/) - система контроля версий
- [uv](https://docs.astral.sh/uv/#tools) - менеджер пакетов
- [MinIO](https://www.min.io/) - S3 сервис (bucket)

Способ установки указанных программ на Ubuntu:

```shell
sudo apt update && sudo apt install -y git # git
curl -LsSf https://astral.sh/uv/install.sh | sh # uv
```

Проверка, если программа установлена, в терминал должна вывестись её версия:

```shell
git --version
# git version 2.55.0

uv --version
# uv 0.12.5 (x86_64-unknown-linux-gnu)

minio --version
# minio version RELEASE.2025-10-15T17-29-55Z ...
```
Про установку `MinIO` будет рассказано ниже

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

1. Создайте файл `.env` с переменными окружениями в корне проекта:
```shell
touch .env
```

> файл `.env` должен быть обязательно добавлен в `.gitignore` т.к. содержит чувствительные данные

2. Вставьте следующий шаблон в `.env` и поменяйте значения на свои в соответствии с ниже приведенной таблицей, без этих переменных проект не запустится. Инструкция расчитана на быстрый запуск, для более индивидуальной настройки обращайте к `CONTRIBUTING.md`

```
DEEPSEEK__API_KEY='API-ключ аутентификации от ИИ'
DEEPSEEK__BASE_URL='URL-адрес альтернативной инсталляции для запросов к API'
DEEPSEEK__MODEL='название альтернативной модели.'
UNSPLASH__CLIENT_ID='Access Key созданного Unsplash приложения'
S3__ACCESS_KEY='логин от bucket'
S3__SECRET_KEY='пароль от bucket'
S3__BUCKET_NAME='имя bucket'
```

| Переменная | Default | Где взять |
|---|---|---|
| `DEEPSEEK__API_KEY` | - | В ЛК [DeepSeek](https://platform.deepseek.com/api_keys) или в агрегаторе, которым пользуетесь
| `DEEPSEEK__BASE_URL` | `https://api.deepseek.com` | базовый url агрегатора, которым пользуетесь(обычно в ЛК) |
| `DEEPSEEK__MODEL` | `deepseek-chat` | название модели, которой пользуетесь, уточняйте на сайте агрегатора |
| `UNSPLASH__CLIENT_ID` | - | `https://unsplash.com/developers` -> New App -> страница с созданным приложением -> Access Key |
| `S3__ACCESS_KEY` | - | логин от бакета (в MinIO - `MINIO_ROOT_USER`) |
| `S3__SECRET_KEY` | - | пароль от бакета (в MinIO - `MINIO_ROOT_PASSWORD`) |
| `S3__BUCKET_NAME` | - | имя бакета в MinIO (например `fastai-html`) |

3. После настройки переходите к запуску проекта, при запуске, если все указано правильно, Вы увидетев терминале все инициализированные переменные в таком формате:

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
  ...
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