from django.core.management import BaseCommand
from user.models import Inn, CustomUser
import random
import string


def rnd_dig(k):
    return ''.join(random.choices(string.digits, k=k))


def rnd(k):
    return ''.join(random.choices(string.digits+string.ascii_lowercase, k=k))


class Command(BaseCommand):
    def add_arguments(self, parser):
        parser.add_argument('inns', type=int)
        parser.add_argument('users', type=int)

    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS('Start update shares in DB....'))
        self.stdout.write('Create {0} INNs'.format(str(options.get('inns'))))
        inn_items = [Inn(number=rnd_dig(10))
                     for _ in range(options.get('inns'))]
        self.stdout.write('Create INNs complete')
        self.stdout.write('Create {0} users'.format(str(options.get('users'))))
        Inn.objects.bulk_create(inn_items)
        inns = Inn.objects.all()
        users = [CustomUser(
                    username=rnd(15),
                    password=rnd(8),
                    inn=random.choice(inns)
                )
                 for _ in range(options.get('users'))]
        CustomUser.objects.bulk_create(users)
        self.stdout.write('Create users complete')
