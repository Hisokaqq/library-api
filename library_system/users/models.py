from django.db import models
from django.contrib.auth.models import User
from library.models import Book
class Profile(models.Model):
    class Type(models.TextChoices):
        USER = "USER", "User"
        LIBRARIAN = "LIBRARIAN", "Libarian"
        ADMIN = "ADMIN", "Admin"

    user = models.OneToOneField(User, on_delete=models.CASCADE)
    type = models.CharField(max_length=10, choices=Type.choices, default=Type.USER)
    bio = models.TextField(null=True, blank=True)
    birth_date = models.DateField(null=True, blank=True)
    location = models.CharField(max_length=30, null=True, blank=True)

    liked_books = models.ManyToManyField(Book, related_name="liked_by", blank=True)
    
    def __str__(self):
        return self.user.username