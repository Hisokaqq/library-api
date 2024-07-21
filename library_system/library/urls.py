from django.urls import path, include
from .views import BookViewSet, AuthorViewSet, GenreViewSet, BorrowViewSet, BulkGenreView, BookRecommendationsView
from rest_framework.routers import DefaultRouter

router = DefaultRouter()

router.register(r'authors', AuthorViewSet)
router.register(r'genres', GenreViewSet)
router.register(r'books', BookViewSet)
router.register(r'borrows', BorrowViewSet)

urlpatterns = [
    path('', include(router.urls)),
    path('bulk-genres/', BulkGenreView.as_view(), name='bulk-genres'),
    path('recommentations/', BookRecommendationsView.as_view(), name='book_recommendations'),
]
