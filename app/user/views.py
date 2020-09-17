from rest_framework.generics import CreateAPIView
from user.serializers import TransactionSerializer
from user.models import Inn, CustomUser
from django.db.models import F


class CreateTransaction(CreateAPIView):
    serializer_class = TransactionSerializer

    def perform_create(self, serializer):
        """
        Функция выполняет обновление балансов пользователя,
        с которого списываются деньги и балансов пользователей,
        на которые зачисляются деньги
        """
        user = CustomUser.objects.filter(
            pk=serializer.validated_data.get('out_user').pk
        )
        user.update(
            balance=F('balance') - serializer.validated_data.get('amount')
        )
        inn_items = serializer.validated_data.get('inns').split(' ')
        inns_query = Inn.objects.filter(number__in=inn_items)
        users_query = CustomUser.objects.filter(inn__in=inns_query)
        number_users = users_query.count()
        add_balance = serializer.validated_data.get('amount') / number_users
        users_query.update(balance=F('balance') + add_balance)
        serializer.save()
