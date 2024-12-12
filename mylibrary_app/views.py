from django.db import transaction
from django.http import JsonResponse
from django.utils import timezone
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response

from .models import Book, Loan, User
from .serializers import BookSerializer, LoanSerializer


class BookViewSet(viewsets.ModelViewSet):
    queryset = Book.objects.all()
    serializer_class = BookSerializer

    @action(detail=False, methods=['get'])
    def available_books(self, request):
        available_books = Book.available_books()
        serializer = BookSerializer(available_books, many=True)
        return JsonResponse(serializer.data, safe=False)


class LoanViewSet(viewsets.ModelViewSet):
    queryset = Loan.objects.all()
    serializer_class = LoanSerializer

    def get_user_from_header(self, request):
        # if majority of requests needs this operation,
        # this should be rather done in the middleware
        user_id = request.headers.get('X-User-Id')
        try:
            return User.objects.get(id=user_id)
        except User.DoesNotExist:
            return None

    @action(detail=True, methods=['post'])
    def borrow_book(self, request, pk=None):
        if not (user := self.get_user_from_header(request)):
            return JsonResponse({'status': 'missing user id'}, status=status.HTTP_403_FORBIDDEN)
        with transaction.atomic():
            book = Book.objects.filter(pk=pk).first()
            if book and book.available():
                Loan.objects.create(book=book, user=user)
                return JsonResponse({'status': 'book borrowed'}, status=status.HTTP_201_CREATED)
        return JsonResponse({'status': 'book not available'}, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=True, methods=['post'])
    def return_book(self, request, pk=None):
        if not (user := self.get_user_from_header(request)):
            return JsonResponse({'status': 'missing user id'}, status=status.HTTP_403_FORBIDDEN)
        latest_loan = Loan.objects.filter(book_id=pk).order_by('-borrowed_at').first()
        if latest_loan and latest_loan.user == user and latest_loan.returned_at is None:
            latest_loan.returned_at = timezone.now()
            latest_loan.save()
            return JsonResponse({'status': 'book returned'}, status=status.HTTP_200_OK)
        return JsonResponse({'status': 'no active loan found'}, status=status.HTTP_400_BAD_REQUEST)


