from django.core.management.base import BaseCommand
from library.models import Book, Author, Genre
import pandas as pd

class Command(BaseCommand):
    help = 'Upload 1000 random books from random_books_with_genres.csv'

    def handle(self, *args, **kwargs):
        file_path = 'library/management/commands/random_books_with_genres.csv'
        books_df = pd.read_csv(file_path)

        # Limit to 1000 books
        books_df = books_df.head(1000)

        for _, row in books_df.iterrows():
            try:
                # Create genres if they don't exist
                genres = []
                for genre_name in eval(row['genres']):
                    genre, created = Genre.objects.get_or_create(name=genre_name)
                    genres.append(genre)

                # Truncate the full_name if it's too long
                full_name = row['authors'][:100]

                # Create authors if they don't exist
                author, created = Author.objects.get_or_create(
                    full_name=full_name,
                    defaults={
                        'date_of_birth': '1900-01-01',  # Placeholder date, adjust as necessary
                        'date_of_death': None
                    }
                )

                # Truncate the title if it's too long
                title = row['title'][:255]

                # Create the book
                book, created = Book.objects.get_or_create(
                    title=title,
                    defaults={
                        'description': 'Description not available',  # Placeholder, adjust as necessary
                        'isbn': row['isbn'],
                        'quantity': 10  # Placeholder, adjust as necessary
                    }
                )

                # Associate genres and author with the book
                book.genres.set(genres)
                book.authors.set([author])

                self.stdout.write(self.style.SUCCESS(f'Successfully created book: {book.title}'))
            except Exception as e:
                self.stdout.write(self.style.ERROR(f'Error creating book: {row["title"]}. Error: {e}'))
