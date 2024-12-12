from django.contrib.auth.models import User
from django.db import models


class Book(models.Model):
    title = models.TextField()
    author = models.TextField()

    def available(self):
        """Checks if the book is available, that means it was never borrowed
        or the last loan was returned"""
        latest_loan = self.loans.order_by('-borrowed_at').first()
        return latest_loan is None or latest_loan.returned_at is not None

    @staticmethod
    def available_books():
        """Returns all available books from the DB."""
        return Book._books_with_no_loans().union(Book._books_with_returned_last_loan())

    @staticmethod
    def _books_with_returned_last_loan():
        """Returns all books with at least one loan, which have the last loan
        returned (that means 'returned_at' value is not null)."""
        # this could be pretty fast, if Django ORM creates a good SQL query
        latest_loans = Loan.objects.filter(
            book=models.OuterRef('pk')
        ).order_by('-borrowed_at').values('returned_at')[:1]
        return Book.objects.annotate(
            latest_return=models.Subquery(latest_loans)
        ).filter(latest_return__isnull=False).values('id', 'title', 'author')

    @staticmethod
    def _books_with_no_loans():
        """Returns all books without any loan."""
        return Book.objects.filter(loans__isnull=True)

class Loan(models.Model):
    book = models.ForeignKey(Book, on_delete=models.PROTECT, related_name='loans')
    user = models.ForeignKey(User, on_delete=models.PROTECT, related_name='loans')
    borrowed_at = models.DateTimeField(auto_now_add=True, null=False, blank=False)
    returned_at = models.DateTimeField(null=True, blank=False)

    class Meta:
        indexes = [
            # for fast checking if a book is available we need to find the last loam of a book
            models.Index(fields=['book', 'borrowed_at'], name='book_borrowed_at_idx'),
        ]
