from rest_framework import serializers
from .models import Book, Checkout


class BookSerializer(serializers.ModelSerializer):
    class Meta:
        model = Book
        fields = ['book_id', 'isbn', 'title', 'author', 'publisher',
                  'publication_year', 'category', 'location', 'copies_total',
                  'copies_available', 'status', 'description']


class CheckoutSerializer(serializers.ModelSerializer):
    book_title = serializers.CharField(source='book.title', read_only=True)
    book_author = serializers.CharField(source='book.author', read_only=True)
    is_overdue = serializers.ReadOnlyField()
    days_overdue = serializers.ReadOnlyField()

    class Meta:
        model = Checkout
        fields = ['checkout_id', 'book', 'book_title', 'book_author',
                  'student', 'student_name', 'checkout_date', 'due_date',
                  'return_date', 'status', 'fine_amount', 'is_overdue',
                  'days_overdue']
        read_only_fields = ['checkout_id', 'fine_amount']
