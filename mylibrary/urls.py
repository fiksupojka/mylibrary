from django.contrib import admin
from django.urls import include, path
from rest_framework.routers import DefaultRouter
from mylibrary_app import views


router = DefaultRouter()
router.register(r'books', views.BookViewSet)
router.register(r'loans', views.LoanViewSet)

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include(router.urls)),
    path('loans/<int:pk>/borrow/', views.LoanViewSet.as_view({'post': 'borrow_book'}), name='loan-borrow'),
    path('loans/<int:pk>/return/', views.LoanViewSet.as_view({'post': 'return_book'}), name='loan-return'),
    path('available-books/', views.BookViewSet.as_view({'get': 'available_books'}), name='available-books'),
]
