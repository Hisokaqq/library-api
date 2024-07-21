from django.db import models
from django.contrib.auth.models import User

class Author(models.Model):
    full_name = models.CharField(max_length=100)
    date_of_birth = models.DateField(blank=True, null=True)
    date_of_death = models.DateField(blank=True, null=True)

    def __str__(self):
        return self.full_name

class Genre(models.Model):
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name

class Book(models.Model):
    title = models.CharField(max_length=255)
    description = models.TextField()
    isbn = models.CharField(max_length=13, unique=True)
    quantity = models.PositiveIntegerField(default=1)
    genres = models.ManyToManyField(Genre, related_name='books')
    authors = models.ManyToManyField(Author, related_name='books')


class Borrow(models.Model):
    book = models.ForeignKey(Book, on_delete=models.SET_NULL, null=True)
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    borrow_date = models.DateField()
    return_date = models.DateField()
    returned = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.user.username if self.user else 'Unknown user'} borrowed {self.book.title if self.book else 'Unknown book'}"

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=['book', 'user', 'borrow_date'], name='unique_borrow')
        ]

