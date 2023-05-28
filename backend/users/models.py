from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    """Модель пользователя."""

    ADMIN = 'admin'
    ANONYMOUS_USER = 'anonymous_user'
    USER = 'user'
    ROLES = [
        (ADMIN, 'Администратор'),
        (ANONYMOUS_USER, 'Гость'),
        (USER, 'Пользователь'),
    ]

    username = models.CharField(
        max_length=100,
        unique=True,
        verbose_name='Имя пользователя'
    )

    email = models.CharField(
        max_length=100,
        unique=True,
        verbose_name='Адрес электронной почты'
    )

    password = models.CharField(
        max_length=30,
        unique=True,
        verbose_name='Пароль'
    )

    last_name = models.CharField(
        max_length=100,
        verbose_name='Фамилия'
    )

    first_name = models.CharField(
        max_length=100,
        verbose_name='Имя'
    )

    role = models.CharField(
        max_length=max(len(value) for value, _ in ROLES),
        choices=ROLES,
        default=USER,
        verbose_name='Роль'
    )

    class Meta:
        verbose_name = 'Пользователь'
        verbose_name_plural = 'Пользователи'

    def __str__(self):
        return self.username

    REQUIRED_FIELDS = ['password', 'email',
                       'first_name', 'last_name']

    @property
    def is_admin(self):
        return (
            self.role == self.ADMIN
            or self.is_staff
        )


class Follow(models.Model):
    """Модель подписки."""

    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='follower',
        verbose_name='Подписчик'
    )

    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='following',
        verbose_name='Подписки'
    )

    class Meta:
        verbose_name = 'Подписка'
        verbose_name_plural = 'Подписки'
        constraints = [
            models.UniqueConstraint(
                fields=['user', 'author'],
                name='unique follow'
            )
        ]
