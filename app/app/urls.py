from django.contrib import admin
from django.urls import path
from user.views import CreateTransaction

urlpatterns = [
    path('admin/', admin.site.urls),
    path(
        'api/transaction/',
        CreateTransaction.as_view(),
        name='create_transaction'
    )
]
