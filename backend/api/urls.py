from django.urls import include, path
from rest_framework.routers import DefaultRouter
from djoser import views as djoser_views

from .views import (CustomUserViewSet, IngredientViewSet, RecipeViewSet,
                    TagViewSet)

app_name = 'api'
router_v1 = DefaultRouter()
router_v1.register('ingredients', IngredientViewSet)
router_v1.register('recipes', RecipeViewSet)
router_v1.register('tags', TagViewSet)
router_v1.register('users', CustomUserViewSet)


urlpatterns = [
    path('', include(router_v1.urls)),
    path('', include('djoser.urls')),
    path('auth/', include('djoser.urls.authtoken')),
    path(
        'api/auth/token/login/',
        djoser_views.TokenCreateView.as_view(),
        name='login'
    ),
    path(
        'api/auth/token/logout/',
        djoser_views.TokenDestroyView.as_view(),
        name='logout'
    ),
]
