from django.urls import path
from django.views.generic.base import TemplateView, RedirectView
from django.urls import reverse
from users.models import User
from . import views
from .views import (
    Book_Add_View,
    Search_List_View,
    Book_Detail_View,
    Book_Delete_View,
    Book_Update_View,
    File_Book_Add_View,
    Home_List_View,
    Loan_Detail_View,
    History_Detail_View,
    Loan_Delete_View,
    Loan_Update_View,
    User_Reviews,
)
app_name = 'library'
urlpatterns = [
    path('', Home_List_View.as_view(),  name='home'),
    path('add/book/', Book_Add_View.as_view(), name='add_book'),
    path('file/add/book/', File_Book_Add_View.as_view(), name='file_add_book'),
    path('book/details/<int:pk>/', Book_Detail_View.as_view(), name='book_details'),
    path('book/delete/<int:pk>/', Book_Delete_View.as_view(), name='book_delete'),
    path('book/update/<int:pk>/', Book_Update_View.as_view(), name='book_update'),
    path('loan/details/<int:pk>/', Loan_Detail_View.as_view(), name='loan_details'),
    path('loan/delete/<int:pk>/', Loan_Delete_View.as_view(), name='loan_delete'),
    path('loan/update/<int:pk>/', Loan_Update_View.as_view(), name='loan_update'),
    path('history/details/<int:pk>/', History_Detail_View.as_view(), name='history_details'),
    path('search/', Search_List_View.as_view(),  name='search'),
    path('borrow/book/', views.borrow_book, name='borrow_book'),
    path('accept/request/', views.accept_request, name='accept_request'),
    path('return/book/', views.return_book, name='return_book'),
    path('reject/request/', views.reject_request, name='reject_request'),
    path('renew/book/', views.renew_book, name='renew_book'),
    path('add/review/', views.add_review, name='add_review'),
    path('edit/review/', views.edit_review, name='edit_review'),
    path('load/reviews/<int:pk>/', views.load_reviews, name='load_reviews'),
    path('del/review/', views.del_review, name='del_review'),
    path('user/reviews/<int:pk>/', User_Reviews.as_view(), name='user_reviews'),

]
