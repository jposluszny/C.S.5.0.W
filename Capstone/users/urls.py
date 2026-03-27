from . import views
from django.urls import path, include
from users import views as user_views
from django.contrib.auth import views as auth_views


app_name = 'users'

urlpatterns = [
    path(
        'password_change/',
        user_views.UserPasswordChangeView.as_view(
            template_name='users/password_change.html'),
        name='password_change'
    ),
    path(
        'password_change_done/',
        auth_views.PasswordChangeDoneView.as_view(
            template_name='users/password_change_done.html'),
        name='password_change_done'
    ),
    path('update/<int:pk>/', user_views.User_Update_View.as_view(), name='update'),
    path('profile/<int:pk>/', user_views.User_Detail_View.as_view(), name='profile'),
    path('login/', auth_views.LoginView.as_view(template_name='users/login.html'), name='login'),
    path('logout/', auth_views.LogoutView.as_view(template_name='users/logout.html'), name='logout'),
    path('registration/', user_views.User_Registration_View.as_view(), name='registration'),
    path('delete/<int:pk>/', user_views.User_Delete_View.as_view(), name='delete'),
]
