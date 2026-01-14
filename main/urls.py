from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import AccountViewSet, TradingViewSet

router = DefaultRouter()
router.register(r'accounts', AccountViewSet, basename='account')
router.register(r'trading', TradingViewSet, basename='trading')

urlpatterns = [
    path('', include(router.urls)),
]
