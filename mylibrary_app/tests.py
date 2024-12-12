from django.test import TestCase

from .models import Book, Loan, User


class TestBorrowingReturningBook(TestCase):
    def setUp(self):
        self.book = Book.objects.create(title="Test Book", author="Author")
        self.user = User.objects.create_user(username='testuser', password='somepass')

    def test_borrow_book(self):
        # we borrow a book
        response = self.client.post(f'/loans/{self.book.id}/borrow/',
                                    headers={'X-User-Id': self.user.id})
        self.assertEqual(response.status_code, 201)

        # the book is not available now
        self.book.refresh_from_db()
        self.assertFalse(self.book.available())

        # we try to borrow the same book again, but it is not possible
        response = self.client.post(f'/loans/{self.book.id}/borrow/',
                                    headers={'X-User-Id': self.user.id})
        self.assertEqual(response.status_code, 400)

    def test_return_book(self):
        # we create a book loan in the DB
        loan = Loan.objects.create(book=self.book, user=self.user)

        # we return the book
        response = self.client.post(f'/loans/{self.book.id}/return_book/',
                                    headers={'X-User-Id': self.user.id})
        self.assertEqual(response.status_code, 200)

        # the book is available again
        self.book.refresh_from_db()
        self.assertTrue(self.book.available())

        # the book cannot be returned now, but can be borrowed again
        response = self.client.post(f'/loans/{self.book.id}/return_book/',
                                    headers={'X-User-Id': self.user.id})
        self.assertEqual(response.status_code, 400)
        response = self.client.post(f'/loans/{self.book.id}/borrow/',
                                    headers={'X-User-Id': self.user.id})
        self.assertEqual(response.status_code, 201)

        # the book loan has a return date
        loan.refresh_from_db()
        self.assertIsNotNone(loan.returned_at)

class TestAvailableBooks(TestCase):
    def setUp(self):
        self.book1 = Book.objects.create(title="Test Book 1", author="Author 1")
        self.book2 = Book.objects.create(title="Test Book 2", author="Author 2")
        self.book3 = Book.objects.create(title="Test Book 3", author="Author 3")
        self.user = User.objects.create_user(username='testuser', password='somepass')

    def test_available_books(self):
        # There should be 3 available books at the start
        response = self.client.get(f'/available-books/')
        self.assertEqual(len(response.json()), 3)

        # we borrow a book
        self.client.post(f'/loans/{self.book1.id}/borrow/',
                         headers={'X-User-Id': self.user.id})

        # There should be 2 available books now
        response = self.client.get(f'/available-books/')
        self.assertEqual(len(response.json()), 2)

        # We return the first book and borrow another
        self.client.post(f'/loans/{self.book1.id}/return_book/',
                         headers={'X-User-Id': self.user.id})
        self.client.post(f'/loans/{self.book2.id}/borrow/',
                         headers={'X-User-Id': self.user.id})

        # There should be 2 available books now
        response = self.client.get(f'/available-books/')
        self.assertEqual(len(response.json()), 2)

        # We borrow the rest of the books
        self.client.post(f'/loans/{self.book1.id}/borrow/',
                         headers={'X-User-Id': self.user.id})
        self.client.post(f'/loans/{self.book3.id}/borrow/',
                         headers={'X-User-Id': self.user.id})

        # There should be no available books
        response = self.client.get(f'/available-books/')
        self.assertEqual(len(response.json()), 0)
