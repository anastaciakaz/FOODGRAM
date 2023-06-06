# Foodgram
### Это удобный и красивый сервис для обмена интересными рецептами. Пользователи могут публиковать свои собственные рецепты и следить за обновлениями других пользователей, а на самых любимых авторов можно подписаться, чтобы не упускать обновлений!
## Стек технологий
- Python
- Django
- Django REST Framework
- Docker
- Docker-compose
- Nginx

[![foodgram_workflow](https://github.com/anastaciakaz/foodgram-project-react/actions/workflows/foodgram_workflow.yml/badge.svg?branch=master)](https://github.com/anastaciakaz/foodgram-project-react/actions/workflows/foodgram_workflow.yml)

## Проект доступен по ссылке:

``` foodgram-projreact.ddns.net ```

## Подготовка и запуск проекта
Склонировать репозиторий на локально:

```git clone git@github.com:anastaciakaz/foodgram-project-react.git ```

Перейти в репозиторий с docker-compose файлом, используя терминал:

```cd infra/```

Развернуть докер-контейнеры:

``` docker-compose up -d --build ```

Выполнить миграции и собрать статику:

``` docker-compose exec web python manage.py makemigrations ```

``` docker-compose exec web python manage.py migrate ```

``` docker-compose exec web python manage.py collectstatic --no-input ```

Создать суперпользователя:

``` docker-compose exec web python manage.py createsuperuser ```

Наполните базу данных ингредиентами и тегами. Выполняйте команду из дериктории где находится файл manage.py:

```docker-compose exec backend python manage.py load_data```

## Для работы с удаленным сервером (на ubuntu):
- Выполните вход на свой удаленный сервер.
- Установите docker на сервер:

```sudo apt install docker.io ```

- Установите docker-compose на сервер:

```sudo curl -L "https://github.com/docker/compose/releases/download/1.29.2/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose```

```sudo chmod +x /usr/local/bin/docker-compose ```

- Локально отредактируйте файл infra/nginx.conf и в строке server_name впишите свой IP.

- Скопируйте файлы docker-compose.yml и nginx.conf из директории infra на сервер:

```scp docker-compose.yml <username>@<host>:/home/<username>/docker-compose.yml ```

```scp nginx.conf <username>@<host>:/home/<username>/nginx.conf ```

- Предварительно выключите nginx на сервере.

``` sudo systemctl stop nginx ```

- Cоздайте .env файл с данными:

```
DB_ENGINE=<django.db.backends.postgresql>
DB_NAME=<имя базы данных postgres>
DB_USER=<пользователь бд>
DB_PASSWORD=<пароль>
DB_HOST=<db>
DB_PORT=<5432>
SECRET_KEY=<секретный ключ проекта django>
```

- Для работы с Workflow добавьте в Secrets GitHub переменные окружения для работы в директории infra/.

## Примеры запросов:

POST (Создание рецепта, эндпоинт: http://127.0.0.1:8000/api/recipes/)
Request:
``` 
{
  "ingredients": [
    {
      "id": 1123,
      "amount": 10
    }
  ],
  "tags": [
    1,
    2
  ],
  "image": "data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABAgMAAABieywaAAAACVBMVEUAAAD///9fX1/S0ecCAAAACXBIWXMAAA7EAAAOxAGVKw4bAAAACklEQVQImWNoAAAAggCByxOyYQAAAABJRU5ErkJggg==",
  "name": "string",
  "text": "string",
  "cooking_time": 1
}
```

Response:

```
{
  "id": 0,
  "tags": [
    {
      "id": 0,
      "name": "Завтрак",
      "color": "#E26C2D",
      "slug": "breakfast"
    }
  ],
  "author": {
    "email": "user@example.com",
    "id": 0,
    "username": "string",
    "first_name": "Вася",
    "last_name": "Пупкин",
    "is_subscribed": false
  },
  "ingredients": [
    {
      "id": 0,
      "name": "Картофель отварной",
      "measurement_unit": "г",
      "amount": 1
    }
  ],
  "is_favorited": true,
  "is_in_shopping_cart": true,
  "name": "string",
  "image": "http://foodgram.example.org/media/recipes/images/image.jpeg",
  "text": "string",
  "cooking_time": 1
}
```

POST (Подписка на пользователя: http://127.0.0.1:8000/api/users/{id}/subscribe/):
Response:

```
{
  "email": "user@example.com",
  "id": 0,
  "username": "string",
  "first_name": "Вася",
  "last_name": "Пупкин",
  "is_subscribed": true,
  "recipes": [
    {
      "id": 0,
      "name": "string",
      "image": "http://foodgram.example.org/media/recipes/images/image.jpeg",
      "cooking_time": 1
    }
  ],
  "recipes_count": 0
}
```
- Локально Документация доступна по адресу:

```
http://127.0.0.1/api/docs/
```
