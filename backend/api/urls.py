from django.urls import include
from django.urls import path
from rest_framework.routers import DefaultRouter

from api.views import IngredientViewSet
from api.views import RecipeViewSet
from api.views import TagViewSet
from api.views import UserViewSet

router = DefaultRouter()
router.register("ingredients", IngredientViewSet, basename="ingredients")
router.register("recipes", RecipeViewSet, basename="recipes")
router.register("tags", TagViewSet, basename="tags")
router.register("users", UserViewSet, basename="users")


urlpatterns = [
    path("", include(router.urls)),
    path("auth/", include("djoser.urls.authtoken")),
]
