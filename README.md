# Foodgram
### It's an easy and beautiful service for exchanging recipes. Users can post their own recipes and follow other users for updates, and you can follow your favorite authors to stay updated!
## Technology stack:
- Python
- Django REST Framework
- Docker
- Docker-compose
- Nginx

[![foodgram_workflow](https://github.com/anastaciakaz/foodgram-project-react/actions/workflows/foodgram_workflow.yml/badge.svg?branch=master)](https://github.com/anastaciakaz/foodgram-project-react/actions/workflows/foodgram_workflow.yml)

## The project is available via the links:

``` foodgram-projreact.ddns.net ``` 

```http://158.160.105.204/```
```http://158.160.105.204/admin/```
```http://158.160.105.204/api/docs```

## Preparation and launch of the project:
Clone the repository locally:

```git@github.com:anastaciakaz/FOODGRAM.git ```

Go to repository with docker-compose file using terminal:

```cd infra/```

Build containers:

``` docker-compose up -d --build ```

Run migrations and collect static:

``` docker-compose exec backend python manage.py makemigrations ```

``` docker-compose backend python manage.py migrate ```

``` docker-compose backend python manage.py collectstatic --no-input ```

Create a superuser:

``` docker-compose backend python manage.py createsuperuser ```

Load data into database. Run the command from the directory where the manage.py file is located:

```docker-compose exec backend python manage.py load_data```

## To work with a remote server (ubuntu):
- Log in to your remote server.
- Set up docker on your remote server:

```sudo apt install docker.io ```

- Set up docker-compose on your remote server:

```sudo curl -L "https://github.com/docker/compose/releases/download/1.29.2/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose```

```sudo chmod +x /usr/local/bin/docker-compose ```

- Edit 'infra/nginx.conf' file locally and type your IP in the server_name line.

- Cope files 'docker-compose.yml' and 'nginx.conf' to your server from 'infra' directory:

```scp docker-compose.yml <username>@<host>:/home/<username>/docker-compose.yml ```

```scp nginx.conf <username>@<host>:/home/<username>/nginx.conf ```

- Do not forget to stop nginx on your server before executing these commands:

``` sudo systemctl stop nginx ```

- Create '.env' file with your data:

```
DB_ENGINE=<django.db.backends.postgresql>
DB_NAME=<postgres database name>
DB_USER=<database user>
DB_PASSWORD=<password>
DB_HOST=<db>
DB_PORT=<5432>
SECRET_KEY=<django project secret key>
```

- For working with Workflow add environmental variables (from '/infra' directory) to Secrets GitHub.

## Request examples:

POST (Recipe creating, endpoint: http://127.0.0.1:8000/api/recipes/)
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
    "first_name": "Dave",
    "last_name": "Jones",
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

POST (To subscribe: http://127.0.0.1:8000/api/users/{id}/subscribe/):
Response:

```
{
  "email": "user@example.com",
  "id": 0,
  "username": "string",
  "first_name": "Dave",
  "last_name": "Jones",
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
- Documentation (local access):

```
http://127.0.0.1/api/docs/
```
