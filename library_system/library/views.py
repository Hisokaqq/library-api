from django.conf import settings
from library_system.permissions import IsLibrarian, IsAdmin
from .models import Author, Book, Genre, Borrow
from rest_framework import viewsets
from .serializers import AuthorSerializer, GenreSerializer, BorrowSerializer, BookDetailSerializer, BookListSerializer, BulkGenreSerializer
from rest_framework.response import Response
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework import status
from rest_framework.views import APIView
import os
import pickle
import random
import pandas as pd

class AuthorViewSet(viewsets.ModelViewSet):
    queryset = Author.objects.all()
    serializer_class = AuthorSerializer
    permission_classes = [IsLibrarian | IsAdmin]

    def get_queryset(self):
        queryset = Author.objects.all()
        full_name = self.request.query_params.get("full_name", None)
        if full_name:
            queryset = queryset.filter(full_name__icontains=full_name)
        return queryset
    
class GenreViewSet(viewsets.ModelViewSet):
    queryset = Genre.objects.all()
    serializer_class = GenreSerializer
    permission_classes = [IsLibrarian | IsAdmin]

    def get_queryset(self):
        queryset = Genre.objects.all()
        name = self.request.query_params.get("name", None)
        if name:
            queryset = queryset.filter(name__icontains=name)
        return queryset
    
class BulkGenreView(APIView):
    def post(self, request, *args, **kwargs):
        serializer = BulkGenreSerializer(data=request.data)
        if serializer.is_valid():
            genres = serializer.save()
            genre_serializer = GenreSerializer(genres, many=True)
            return Response(genre_serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
class BookViewSet(viewsets.ModelViewSet):
    queryset = Book.objects.all()
    permission_classes = [IsLibrarian | IsAdmin]

    def get_permissions(self):
        if self.action in ['list', 'retrieve']:
            permission_classes = [IsAuthenticated]
        else:
            permission_classes = [IsLibrarian | IsAdmin]
        return [permission() for permission in permission_classes]

    def get_serializer_class(self):
        if self.action == 'list':
            return BookListSerializer
        return BookDetailSerializer

    def get_queryset(self):
        queryset = super().get_queryset()
        title = self.request.query_params.get('title', None)
        isbn = self.request.query_params.get('isbn', None)
        genres = self.request.query_params.getlist('genres', None)
        if title:
            queryset = queryset.filter(title__icontains=title)
        if isbn:
            queryset = queryset.filter(isbn=isbn)
        if genres:
            queryset = queryset.filter(genres__name__in=genres).distinct()
        return queryset

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)

    def perform_create(self, serializer):
        serializer.save()

    def update(self, request, *args, **kwargs):
        partial = kwargs.pop('partial', True)  # Allow partial updates
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)
        return Response(serializer.data)

    def perform_update(self, serializer):
        serializer.save()

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        self.perform_destroy(instance)
        return Response(status=status.HTTP_204_NO_CONTENT)

class BorrowViewSet(viewsets.ModelViewSet):
    queryset = Borrow.objects.all()
    serializer_class = BorrowSerializer
    permission_classes = [IsLibrarian | IsAdmin]

    def get_queryset(self):
        queryset = super().get_queryset()
        book_title = self.request.query_params.get("book_title", None)
        user_full_name = self.request.query_params.get("user_full_name", None)
        if book_title:
            queryset = queryset.filter(book__title__icontains=book_title)
        if user_full_name:
            names = user_full_name.split()
            if len(names) == 2:
                queryset = queryset.filter(user__first_name__icontains=names[0], user__last_name__icontains=names[1])
        return queryset

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)

    def perform_create(self, serializer):
        serializer.save()

    def update(self, request, *args, **kwargs):
        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)
        return Response(serializer.data)

    def perform_update(self, serializer):
        serializer.save()

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        self.perform_destroy(instance)
        return Response(status=status.HTTP_204_NO_CONTENT)

class BookRecommendationsView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, *args, **kwargs):
        user = request.user
        # Get the last 5 liked books of the user
        liked_books = user.profile.liked_books.all().order_by('-id')[:5]

        if not liked_books.exists():
            return Response({"message": "No liked books found"}, status=status.HTTP_404_NOT_FOUND)

        # Load the recommendation model
        model_path = os.path.join(settings.BASE_DIR, 'library', 'recommender', 'book_recommender_model.pkl')
        with open(model_path, 'rb') as f:
            recommender_model = pickle.load(f)

        # Get all books
        all_books = Book.objects.all()

        # Get recommendations based on the liked books
        recommendations = []
        for book in liked_books:
            try:
                book_recommendations = self.get_recommendations_for_book(recommender_model, user.id, book.id, all_books)
                recommendations.extend(book_recommendations)
            except Exception as e:
                print(f"Error recommending for book {book.title}: {e}")

        if not recommendations:
            return Response({"message": "No recommendations available"}, status=status.HTTP_404_NOT_FOUND)

        # Select 5 random recommendations from the collected recommendations
        final_recommendations = random.sample(recommendations, min(5, len(recommendations)))

        # Get the book objects for the recommendations
        recommended_books = Book.objects.filter(id__in=final_recommendations)
        serializer = BookListSerializer(recommended_books, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def get_recommendations_for_book(self, model, user_id, book_id, all_books):
        book_recommendations = []
        for other_book in all_books:
            if other_book.id != book_id:
                predicted_rating = model.predict(user_id, other_book.id).est
                book_recommendations.append((other_book.id, predicted_rating))
        
        # Sort by predicted rating and get top 5 recommendations
        book_recommendations.sort(key=lambda x: x[1], reverse=True)
        top_recommendations = [book_id for book_id, _ in book_recommendations[:5]]
        return top_recommendations
