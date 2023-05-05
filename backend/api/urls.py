from django.urls import include, path
from rest_framework.routers import DefaultRouter

from api.views import (MyUserViewSet, IngredientViewSet, RecipeViewSet,
                       TagViewSet)

router = DefaultRouter()

router.register(r'users', MyUserViewSet)
router.register(r'recipes', RecipeViewSet)
router.register(r'tags', TagViewSet)
router.register(r'ingredients', IngredientViewSet)

urlpatterns = [
    path('', include(router.urls)),
    path('', include('djoser.urls')),
    path('auth/', include('djoser.urls.authtoken')),
]
