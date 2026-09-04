# Разработчикам бэкенда

## Схемы приложения FastAI

- [Локальная инсталляция бэкенда](https://gitlab.dvmn.org/root/fastapi-articles/-/wikis/fastai/backend_local_installation.drawio.png)
- [Prod инсталляция бэкенда](https://gitlab.dvmn.org/root/fastapi-articles/-/wikis/fastai/backend_prod_installation.drawio.png)
- [Декомпозиция бэкенда по подсистемам](https://gitlab.dvmn.org/root/fastapi-articles/-/wikis/fastai/backend_decomposition.drawio.png)

## Как развернуть локально

### Необходимое ПО

Для запуска ПО вам понадобятся консольный Git и Make. Инструкции по их установке ищите на
официальных сайтах:

- [Git SCM](https://git-scm.com/) - система контроля версий
- [GNU Make](https://www.gnu.org/software/make/) - утилита для автоматизации преобразования файлов из одной формы в другую
- [uv](https://docs.astral.sh/uv/#tools) - менеджер пакетов
- [MinIO](https://www.min.io/) - S3 сервис (bucket)

Вы можете проверить, установлены ли эти программы с помощью команд:
```shell
git --version
# git version 2.55.0

make --version
# GNU Make 4.4.1

uv --version
# uv 0.12.5 (x86_64-unknown-linux-gnu)

minio --version
# minio version RELEASE.2025-10-15T17-29-55Z ...
```

Для тех, кто использует Windows необходимы также программы **git** и **git bash**. В **git bash** необходимо дополнительно установить
**make**:

- Перейдите на сайт [ezwinports](https://sourceforge.net/projects/ezwinports/files/)
- Скачайте `make-4.4.1-without-guile-w32-bin.zip` (выберите версию без `guile`)
- Извлеките архив
- Скопируйте содержимое архива в `C:\ProgramFiles\Git\mingw64\` **БЕЗ** перезаписи/замены любых вложенных файлов.

Все дальнейшие команды запускать из-под **git bash**.

### Создание виртуального окружения для работы с IDE

IDE для корректной работы подсказок необходимо развернуть виртуальное окружение со всеми установленными зависимостями.

В качестве пакетного менеджера на проекте используется [uv](https://docs.astral.sh/uv/).

[Установите uv](https://gitlab.dvmn.org/root/fastapi-articles/-/wikis/Uv-package-manager#1-%D1%83%D1%81%D1%82%D0%B0%D0%BD%D0%BE%D0%B2%D0%BA%D0%B0-uv) и в корне репозитория выполните команду

```shell
uv sync
```

[uv](https://docs.astral.sh/uv/) создаст виртуальное окружение, установит необходимую версию Python и все необходимые зависимости.

После этого активируйте виртуальное окружение в текущей сессии терминала:

```shell
source .venv/bin/activate  # для Linux
.\.venv\Scripts\activate  # Для Windows
```

### Настройка pre-commit хуков

В репозитории используются хуки [pre-commit](https://pre-commit.com/), чтобы автоматически запускать линтеры и автотесты.

В корне репозитория в **активированном виртуальном окружении** запустите команду для настройки хуков:

```shell
pre-commit install
pre-commit installed at .git/hooks/pre-commit
```

В последующем при коммите автоматически будут запускаться линтеры и другие проверки. Если проверки не пройдут, то коммит прервётся с ошибкой.

Если вам потребуется сделать коммит без проверок, то вы можете отключить их с помощью флага `--no-verify`:
```shell
git commit -m 'Message' --no-verify
git commit -m 'Message' -n # альтернативный флаг
```

### Установка MinIO

Для разработки и работы с бакетом используется локально установленный MinIO. Инcтрукция по установке прописана для системы Ubuntu 22.04. Скачайте и установите официальный .deb-пакет:

```shell
wget https://dl.min.io/server/minio/release/linux-amd64/minio.deb
sudo dpkg -i minio.deb
```
> Пакет создаст пользователя minio-user и systemd-сервис minio.service.

### Настройка конфигурации MinIO

Задайте учётные данные и адреса портов в файле `/etc/default/minio`:

```shell
nano ~/etc/default/minio
```

И настройте следующие параметры:

```shell
MINIO_ROOT_USER="ваш_логин"       # == AWS_ACCESS_KEY
MINIO_ROOT_PASSWORD="ваш_пароль"  # == AWS_SECRET_KEY, не короче 8 символов
MINIO_VOLUMES="/var/lib/minio"
MINIO_OPTS="--address :9000 --console-address :9001"
```
> `:9000` - порт S3 API; `:9001` - порт веб-интерфейса, при обращении к порту 9000 будет перекидывать на веб-интерфейс

### Запуск сервиса MinIO

```shell
sudo systemctl daemon-reload
sudo systemctl enable --now minio
systemctl status minio # сервис должен быть в статусе active (running)
```

### Установка клиента mcli

Клиент MinIO - `mcli` потребуется для управления бакетами из терминала. Если установка прошла правильно - Вы должны увидеть версию.

```shell
wget https://dl.min.io/client/mc/release/linux-amd64/mcli_20250813083541.0.0_amd64.deb
sudo dpkg -i mcli_20250813083541.0.0_amd64.deb
mcli --version
```

### Адреса и авторизация MinIO

- Адрес API MinIO: `http://127.0.0.1:9000` (при открытии в браузере — редирект на веб-интерфейс)
- Адрес веб-интерфейса: `http://127.0.0.1:9001`
- Когда зайдете в веб-интерфейс - авторизуйтесь введя `MINIO_ROOT_USER` из конфига как логин, а `MINIO_ROOT_PASSWORD` как пароль

### Создание бакета

В веб-интерфейсе создайте бакет `fastai-html` и выставите ему доступ `public`.
Либо через `mcli`:

```shell
mcli alias set local http://127.0.0.1:9000 <MINIO_ROOT_USER> <MINIO_ROOT_PASSWORD>
mcli mb local/fastai-html # создает новый бакет с названием fastai-html, можете дать свое
mcli anonymous set public local/fastai-html   # публичный доступ к бакету
mcli anonymous get local/fastai-html # должен быть такой вывод: Access permission for `local/fastai-html` is `public`
```

### Заливка файлов в бакет вручную

Backend возвращает ссылки на файлы из бакета, поэтому в хранилище
должны лежать два файла:

- `index.html` - сгенерированная страница, источник: корень репозитория
- `index.png` — скриншот сайта, источник: корень репозитория

После того как руками их добавили в бакет через веб-интерфейс, можете проверить их доступность по ссылкам:
- http://127.0.0.1:9000/fastai-html/index.html
- http://127.0.0.1:9000/fastai-html/index.png

> Если в бакете не будет файлов, фронтенд будет выглядеть сломанным: страница со списком сайтов не откроет сайт и не отобразит скриншот

### Заливка файлов в бакет через python код
Файлы можно выгружать в бакет использую python и терминал. Для этого в модуле `s3_utils.py` используйте асинхронную
функцию `upload_file()`. Файл для заливки должен лежать в корне проекта, в функцию передаётся только его имя. Выполните в консоле следующие команды:

```shell
python # переведет Вас в консоль python
# импортируем нужные модули
import asyncio
from s3_utils import upload_file

upload_file("название_файла") # загрузит файл в bucket

url = asyncio.run(upload_file("название_файла")) # если ещё нужно узнать ссылку на загруженный файл, но лучше это узнавать через веб-интерфейс
print(url)
```
Функция задаёт файлу заголовок `ContentDisposition="inline"`, благодаря чему файл открывается в браузере, а не скачивается. Также функция автоматически определяем MIME-тип файла, поэтому Вам не нужно об этом беспокоиться.


### Настройка переменных окружения (.env)

1. Скопируйте шаблон `example.env` и откройте режим редактирования в терминале(или в любом удобном редакторе):
```shell
cp example.env .env
nano .env
```
> файл `.env` должен быть обязательно добавлен в `.gitignore` т.к. содержит чувствительные данные

2. Заполните все обязательные переменные(не обязательные по необходимости):

| Переменная | Обязательная | Default | Где взять |
|---|---|---|---|
| `DEEPSEEK__API_KEY` | да | - | В ЛК [DeepSeek](https://platform.deepseek.com/api_keys) или в агрегаторе, которым пользуетесь
| `DEEPSEEK__BASE_URL` | нет (если default) | `https://api.deepseek.com` | базовый url агрегатора, которым пользуетесь(обычно в ЛК) |
| `DEEPSEEK__MODEL` | нет (если default) | `deepseek-chat` | модель, которой пользуетесь, уточняйте на сайте агрегатора |
| `DEEPSEEK__MAX_CONNECTIONS` | нет | None | максимальное кол-во попыток подключиться к ИИ |
| `UNSPLASH__CLIENT_ID` | да | - | `https://unsplash.com/developers` -> New App -> страница с созданным приложением -> Access Key |
| `UNSPLASH__MAX_CONNECTIONS` | нет | None | максимальное кол-во попыток подключиться к Unsplash |
| `UNSPLASH__TIMEOUT` | нет | - | 15 | время на попытку подключиться к Unsplash
| `S3__ACCESS_KEY` | да | - | логин от бакета (в MinIO - `MINIO_ROOT_USER`) |
| `S3__SECRET_KEY` | да | - | пароль от бакета (в MinIO - `MINIO_ROOT_PASSWORD`) |
| `S3__BUCKET_NAME` | да | - | имя бакета в MinIO (например `fastai-html`) |
| `S3__BUCKET_URL` | нет (если default) | `http://127.0.0.1:9000` | endpoint сервера с портом |
| `S3__REGION_NAME` | нет | `us-east-1` | регион бакета (по умолчанию `us-east-1`, если не задавали явно) |
| `S3__MAX_POOL_CONNECTIONS` | нет | `10` | лимит одновременных подключений к бакету |
| `S3__CONNECT_TIMEOUT` | нет | `20` | таймаут подключения к бакету, сек |
| `S3__READ_TIMEOUT` | нет | `30` | таймаут чтения из бакета, сек |
| `GOTENBERG__BASE_URL` | нет | `https://demo.gotenberg.dev` | базовый адрес Gotenberg API |
| `GOTENBERG__SCREENSHOT_WIDTH` | нет | `1000` | ширина скриншота в пикселях |
| `GOTENBERG__SCREENSHOT_FORMAT` | нет | `png` | формат скриншота (`jpeg`, `png`, `webp`) |
| `GOTENBERG__WAIT_DELAY` | нет | `3` | время ожидания завершения анимаций на HTML-странице, сек |
| `GOTENBERG__CONNECT_TIMEOUT` | нет | `20` | таймаут подключения к Gotenberg, сек |
| `GOTENBERG__MAX_POOL_CONNECTIONS` | нет | `10` | лимит одновременных подключений к Gotenberg |
| `DEBUG` | нет | `False` | `True` или `False` - отвечает за дебаг режим |

После настройки переходите к запуску проекта, при запуске, если все указано правильно, Вы увидете в терминале все инициализированные переменные в таком формате:
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
### Подключение фронтенда для локальной отладки

Так как данный в данном репозитории разрабатывается только backend часть, frontend не заливается в git (папка `/frontend` добавлена в `.gitignore`). Для того чтобы настроить frontend часть для разработки backend, проделайте следующее:

1. Скачайте [архив фронтенда](https://dvmn.org/filer/canonical/1750917110/1035/)
2. Распакуйте скачанный архив в корне проекта

```shell
unzip .../fronend.zip -d .
```
3. Создайте и настройте `frontend-settings.json`

```shell
touch frontend/frontend-settings.json
```

Запишите в этот файл следующее:


```json
{
    "backendBaseUrl": "/"
}
```
### Запуск проекта

Код проекта находится в папке `/src`.

Находясь в корневой директории проекта, запустить проект можно командой:

```shell
source .venv/bin/activate
fastapi dev src/main.py
```
Проект будет работать по адресу [http://127.0.0.1:8000](http://127.0.0.1:8000)

> Перед запуском убедитесь, что в корне репозитория есть папка `frontend` (она не хранится в git). Без неё приложение не стартует.

## Как вести разработку

### Как установить python-пакет в виртуальное окружение

В качестве менеджера пакетов используется [uv](https://docs.astral.sh/uv/).

Вот пример как добавить в зависимости библиотеку `beautifulsoup4`.

```shell
uv add beautifulsoup4
uv add beautifulsoup4==1.2.3 # точную версию
uv add "beautifulsoup4>=1.0,<2.0" # диапозон версий
```
Можете командой проверить список всех установленных пакетов:
```shell
uv pip list
```

Конфигурационные файлы `pyproject.toml` и `uv.lock` обновятся автоматически.
Аналогичным образом можно удалять python-пакеты:

```shell
uv remove beautifulsoup4
```

Если необходимо обновить `uv.lock` вручную, то используйте команду:

```shell
uv lock
```
### Проверка кода линтерами (Ruff)

Если внесли изменения и хотите отформатировать код перед `git commit`:

```shell
ruff format --diff .   # посмотреть, что изменится если применить форматирование
ruff format .          # применить форматирование ко всем файлам
ruff check --fix .     # исправить обнаруженные ошибки
```
При успешном выполнении команды, Вы получите в терминал слудующий вывод, в соответствии с командой:

- diff предлагаемых изменений
- список изменённых файлов
- кол-во найденных и пофикшенных ошибок

Шорткаты через make:

```shell
make lint # проверить синтаксис кода с помощью ruff
make format # автофикс всех найденных ошибок
```
Если ошибок не будет найдено, Вы увидете следующее сообщение: `All checks passed!`. Если же обнаружится ошибка, ruff сообщит в каком файле, на какой строчке и что за ошибка обнаружена.

### Команды для быстрого запуска с помощью make

Для вывода списка часто используемых коротких команд используйте команду

```shell
$ make list
...
```