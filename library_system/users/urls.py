from django.urls import path, include
from .views import CreateUserView, UserProfileView, ChangePasswordView, UserListView
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from rest_framework.routers import DefaultRouter

router = DefaultRouter()
router.register(r'users', UserListView, basename='users')

urlpatterns = [
    path('user/register/', CreateUserView.as_view(), name='register'),
    path('token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('auth/', include('rest_framework.urls')),
    
    path('user/profile/', UserProfileView.as_view(), name='user_profile'),
    path('user/change_password/', ChangePasswordView.as_view(), name='change_password'),
    path('', include(router.urls)),
]
