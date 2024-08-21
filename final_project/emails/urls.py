from django.urls import path
from users.models import User
from . import views
from .views import (
    Email_Inbox_List_View,
    Email_Sent_List_View,
    Email_Archive_List_View,
    Email_Detail_View,
    Email_Compose_View,
    Email_Delete_View,
    Email_Reply_View,
)
app_name = 'emails'
urlpatterns = [
    path('update/email/archive/', views.update_email_archive, name='update_email_archive'),
    path('update/email/unarchive/', views.update_email_unarchive, name='update_email_unarchive'),
    path('delete/<int:pk>/', Email_Delete_View.as_view(), name='email_delete'),
    path('inbox/', Email_Inbox_List_View.as_view(), name='email_inbox'),
    path('sent/', Email_Sent_List_View.as_view(), name='email_sent'),
    path('archive/', Email_Archive_List_View.as_view(), name='email_archive'),
    path('details/<int:pk>/', Email_Detail_View.as_view(), name='email_details'),
    path('compose/', Email_Compose_View.as_view(), name='email_compose'),
    path('reply/<int:email_pk>/', Email_Reply_View.as_view(), name='email_reply'),
]
