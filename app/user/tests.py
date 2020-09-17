from django.test import TestCase
from rest_framework.test import APIClient
from rest_framework import status
from user.models import CustomUser, Transaction, Inn
from user.serializers import TransactionSerializer
from django.urls import reverse
from django.db.models import Sum
import random
import string


URL_TRANS = reverse('create_transaction')


def get_username():
    """
    Функция возвращает случайное имя пользователя из 5 символов
    """
    return ''.join(random.choices(string.ascii_lowercase, k=5))


def create_sample_user(**kwargs):
    """
    Функция создает нового пользователя в БД.
    По умолчанию использутся username, password.
    В функцию обязательно нужно передать inn.
    """
    payload = {
        'username': 'test',
        'password': 'superpass',
    }
    payload.update(kwargs)
    return CustomUser.objects.create(**payload)


def create_sample_inn(number='55555'):
    """
    Функция создает новый ИНН в базе данных.
    По умолчанию используется ИНН равный 55555
    """
    return Inn.objects.create(number=number)


class TestTransaction(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.inn_number = ['111', '222', '333', '444']
        self.inn = [create_sample_inn(num) for num in self.inn_number]
        self.user_by_inn = 2
        self.start_balance = 100
        self.usernames = [get_username()
                          for _ in range(self.user_by_inn * len(self.inn))]
        self.users = []
        i = 0
        for inn in self.inn:
            for _ in range(self.user_by_inn):
                newuser = create_sample_user(
                        username=self.usernames[i],
                        inn=inn
                    )
                self.users.append(newuser)
                i += 1
        self.custom_inn = create_sample_inn()
        self.user_out = create_sample_user(
            balance=self.start_balance,
            inn=self.custom_inn
        )

    def test_success_transaction(self):
        """
        Тест успешного прохождения транзакции
        """
        add = 1
        amount = (len(self.inn_number) - 1) * self.user_by_inn * add
        payload = {
            'inns': ' '.join(self.inn_number[:-1]),
            'out_user': self.user_out.id,
            'amount': amount
        }
        resp = self.client.post(URL_TRANS, payload)
        self.assertEqual(resp.status_code, status.HTTP_201_CREATED)
        self.user_out.refresh_from_db()
        self.assertEqual(self.user_out.balance, self.start_balance - amount)
        for user in self.users[:-self.user_by_inn]:
            user.refresh_from_db()
            self.assertEqual(user.balance, add)
        sum_bal = CustomUser.objects.all().aggregate(Sum('balance'))
        self.assertEqual(sum_bal['balance__sum'], self.start_balance)
        trans = Transaction.objects.filter(
            out_user=self.user_out).filter(amount=amount)
        self.assertTrue(trans.exists())
        ser_trans = TransactionSerializer(trans.first())
        self.assertEqual(ser_trans.data, resp.data)

    def test_low_balance(self):
        """
        Тест неудачной транзакции при нехватке баланса счета
        """
        payload = {
            'inns': ' '.join(self.inn_number),
            'out_user': self.user_out.id,
            'amount': self.start_balance + 1
        }
        resp = self.client.post(URL_TRANS, payload)
        self.assertEqual(resp.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn(
            'Недостаточно средств на счете',
            resp.data.get('non_field_errors')
        )
        self.user_out.refresh_from_db()
        self.assertEqual(self.user_out.balance, self.start_balance)
        for user in self.users:
            user.refresh_from_db()
            self.assertEqual(user.balance, 0)
        trans = Transaction.objects.all()
        self.assertFalse(trans.exists())

    def test_incorrect_inn(self):
        """
        Тест неудачной транзакции при некорректном принимающем ИНН
        """
        incorrect_inn = '1234'
        payload = {
            'inns': ' '.join(self.inn_number + [incorrect_inn]),
            'out_user': self.user_out.id,
            'amount': self.start_balance - 10
        }
        resp = self.client.post(URL_TRANS, payload)
        self.assertEqual(resp.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn(
            f'Инн номера {incorrect_inn} нет в базе данных',
            resp.data.get('non_field_errors')
        )
        self.user_out.refresh_from_db()
        self.assertEqual(self.user_out.balance, self.start_balance)
        for user in self.users:
            user.refresh_from_db()
            self.assertEqual(user.balance, 0)
        trans = Transaction.objects.all()
        self.assertFalse(trans.exists())
