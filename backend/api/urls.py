from django.urls import include, path
from drf_yasg import openapi
from drf_yasg.views import get_schema_view
from rest_framework import permissions
from rest_framework.routers import DefaultRouter

from api.views import IngredientViewSet, RecipeViewSet, TagViewSet, UserViewSet


schema_view = get_schema_view(
    openapi.Info(
        title='Foodgram API',
        default_version='v1',
        description='Документация для проекта Foodgram',
        contact=openapi.Contact(email='admin@foodgram.ru'),
        license=openapi.License(name='BSD License'),
    ),
    public=True,
    permission_classes=(permissions.AllowAny,),
)

router = DefaultRouter()
router.register("ingredients", IngredientViewSet, basename="ingredients")
router.register("recipes", RecipeViewSet, basename="recipes")
router.register("tags", TagViewSet, basename="tags")
router.register("users", UserViewSet, basename="users")


urlpatterns = [
    path("", include(router.urls)),
    path("auth/", include("djoser.urls.authtoken")),
    path(
        "docs",
        schema_view.with_ui('redoc', cache_timeout=0),
        name='schema-redoc'
    ),
]
