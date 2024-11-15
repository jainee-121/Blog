from django.urls import path,include
from api.views import CreateUserView, ViewUser, LoginUser
from . import views

urlpatterns = [
    path("notes/", views.BlogList.as_view(), name="blog-list"),
    path("notes/delete/<int:pk>/", views.DeleteBlog.as_view(), name="delete-blog-list"),
    path("notes/update/<int:pk>/", views.UpdateBlog.as_view(), name="update-blog-list"),
    path("user/", CreateUserView.as_view(), name="register"),
    path("login/", LoginUser.as_view(), name="Login"),
    path("user/view/", ViewUser.as_view(), name="user_view"),
]
