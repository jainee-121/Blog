
from django.contrib import admin
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from django.urls import path,include
from rest_framework import routers

# router can only used along ViewSet, wont work along Generics and APIViews

'''
router = routers.DefaultRouter()
router.register(r'posts', PostViewSet, basename="post")

urlpatterns = [
    path('', include(router.urls)),
]
'''

urlpatterns = [
    path('admin/', admin.site.urls),
    path("api/", include("api.urls")),
    path("api/token/", TokenObtainPairView.as_view(), name="get_token"),
    path("api/token/refresh/", TokenRefreshView.as_view(), name="refresh"),
    path("api-auth/", include("rest_framework.urls")),
]
