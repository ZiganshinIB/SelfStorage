# Проект "SelfStorage"
![img.png](git_media/img.png)

![img.png](git_media/img2.png)
## Требовании:
Для работы проекта требуется Python 3.9 и старше 

### 1. Скачивания проекта
```shell
git clone https://github.com/ZiganshinIB/SelfStorage.git
cd SelfStorage
```
**Важно!** Возможно, вместо команды `python` здесь и в остальных инструкциях этого README придётся использовать `python3`. Зависит это от операционной системы и от того, установлен ли у вас Python старой второй версии.
### 2. В каталоге проекта создайте виртуальное окружение:
```sh
python -m venv .venv
```
Активируйте его. На разных операционных системах это делается разными командами:

- Windows: `.\.venv\Scripts\activate`
- MacOS/Linux: `source .venv/bin/activate`

### 3. Установка зависимостей
```shell
pip install -r requirements.txt
```
### 4. Объявление переменных среды (необходимо для запуска пректа)
В файле settings.py есть настройка `SECRET_KEY` — это секретный ключ, применяемое для защиты от [CSRF атак](https://learn.javascript.ru/csrf).
<br> По этой причине ключ хранится в переменной окружение. 
<br> Для этого необходимо создать файл `.env` в директории с проектом
```shell
nano .env
```
И определите следующие переменые среды в этом файле
DJANGO_DEBUG=true
export DJANGO_ALLOWED_HOSTS=yourhostname.com,127.0.0.1
```shell
export SECRET_KEY=django-insecure
export DEBUG=false
export ALLOWED_HOSTS=HOST_NAME,HOST_IP,...
```
export SECRET_KEY=django-insecure
export DEBUG=false
export ALLOWED_HOSTS=HOST_NAME,HOST_IP,...

### 5. Миграция базы данных
```shell
python3 manage.py migrate
```
### 6. Добаление администратора сайта (superusre) для входа в панель администратора
```shell
pyhton3 manage.py createsuperuser
```
### 7. Запуск проектка
```shell
python3 manage.py runserver
```