from .models import Author, Genre, Book, Borrow
from rest_framework import serializers
from django.contrib.auth.models import User

class AuthorSerializer(serializers.ModelSerializer):
    class Meta:
        model = Author
        fields = '__all__'

class GenreSerializer(serializers.ModelSerializer):
    class Meta:
        model = Genre
        fields = '__all__'

class BulkGenreSerializer(serializers.Serializer):
    genres = GenreSerializer(many=True)

    def create(self, validated_data):
        genres_data = validated_data.pop('genres')
        genres = []
        for genre_data in genres_data:
            genre, created = Genre.objects.get_or_create(name=genre_data['name'])
            genres.append(genre)
        return genres

class BookListSerializer(serializers.ModelSerializer):
    class Meta:
        model = Book
        fields = ['id' ,'title', 'isbn']

class BookDetailSerializer(serializers.ModelSerializer):
    authors = AuthorSerializer(many=True, required=False)
    genres = GenreSerializer(many=True, required=False)

    class Meta:
        model = Book
        fields = '__all__'

    def create(self, validated_data):
        authors_data = validated_data.pop('authors', [])
        genres_data = validated_data.pop('genres', [])
        book = Book.objects.create(**validated_data)

        for author_data in authors_data:
            author, created = Author.objects.get_or_create(full_name=author_data['full_name'], defaults=author_data)
            book.authors.add(author)

        for genre_data in genres_data:
            genre, created = Genre.objects.get_or_create(name=genre_data['name'], defaults=genre_data)
            book.genres.add(genre)

        return book

    def update(self, instance, validated_data):
        authors_data = validated_data.pop('authors', None)
        genres_data = validated_data.pop('genres', None)

        instance.title = validated_data.get('title', instance.title)
        instance.description = validated_data.get('description', instance.description)
        instance.isbn = validated_data.get('isbn', instance.isbn)
        instance.quantity = validated_data.get('quantity', instance.quantity)
        instance.save()

        if authors_data is not None:
            instance.authors.clear()
            for author_data in authors_data:
                author, created = Author.objects.get_or_create(full_name=author_data['full_name'], defaults=author_data)
                instance.authors.add(author)

        if genres_data is not None:
            instance.genres.clear()
            for genre_data in genres_data:
                genre, created = Genre.objects.get_or_create(name=genre_data['name'], defaults=genre_data)
                instance.genres.add(genre)

        return instance

    
class BorrowSerializer(serializers.ModelSerializer):
    book = BookListSerializer(read_only=True)
    user_full_name = serializers.SerializerMethodField()
    book_id = serializers.PrimaryKeyRelatedField(queryset=Book.objects.all(), source='book', write_only=True)
    user_id = serializers.PrimaryKeyRelatedField(queryset=User.objects.all(), source='user', write_only=True)

    class Meta:
        model = Borrow
        fields = ['id', 'book', 'book_id', 'user_full_name', 'user_id', 'borrow_date', 'return_date', 'returned']

    def get_user_full_name(self, obj):
        return f"{obj.user.first_name} {obj.user.last_name}"

    