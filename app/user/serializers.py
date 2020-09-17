from rest_framework.serializers import (ModelSerializer,
                                        CharField,
                                        ValidationError,
                                        PrimaryKeyRelatedField,
                                        SerializerMethodField)
from user.models import Transaction, CustomUser, Inn


class UserSerializer(ModelSerializer):
    class Meta:
        model = CustomUser
        fields = ('username', 'balance')


class TransactionSerializer(ModelSerializer):
    """
    Сериалайзер для создания новой транзакции
    """
    inns = CharField(write_only=True)
    in_users = UserSerializer(read_only=True, many=True)
    out_user = PrimaryKeyRelatedField(
        write_only=True,
        queryset=CustomUser.objects.all()
    )
    out_user_info = SerializerMethodField()

    def get_out_user_info(self, instance):
        instance.out_user.refresh_from_db()
        return UserSerializer(instance.out_user).data

    class Meta:
        model = Transaction
        fields = ('id', 'inns', 'out_user',
                  'out_user_info', 'in_users', 'amount')

    def validate(self, data):
        """
        Проверка достаточного количества денег на счете для проведения
        транзакции, проверка наличия заданных ИНН в БД
        """
        user = CustomUser.objects.get(pk=data.get('out_user').pk)
        if user.balance < data.get('amount'):
            raise ValidationError('Недостаточно средств на счете')
        inn_items = data.get('inns').split(' ')
        for inn in inn_items:
            query = Inn.objects.filter(number=inn)
            if not query.exists():
                raise ValidationError(f'Инн номера {inn} нет в базе данных')
        return data

    def create(self, validated_data):
        """
        Создание новой транзакции в БД
        """
        inns_items = validated_data.pop('inns').split(' ')
        transaction = Transaction.objects.create(**validated_data)
        inns_query = Inn.objects.filter(number__in=inns_items)
        user_in_query = CustomUser.objects.filter(inn__in=inns_query)
        transaction.in_users.add(*[user for user in user_in_query])
        return transaction
