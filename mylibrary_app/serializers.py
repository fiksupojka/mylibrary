from rest_framework import serializers

from .models import Book, Loan


class BookSerializer(serializers.ModelSerializer):
    class Meta:
        model = Book
        fields = ['id', 'title', 'author']

class LoanSerializer(serializers.ModelSerializer):
    class Meta:
        model = Loan
        fields = ['id', 'book', 'user', 'borrowed_at', 'returned_at']