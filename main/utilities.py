import datetime
from os.path import splitext

from django.core.signing import Signer
from django.template.loader import render_to_string

from bboard.settings import ALLOWED_HOSTS

signer = Signer()


def send_activation_notification(user):
    if ALLOWED_HOSTS:
        host = 'http://' + ALLOWED_HOSTS[0]

    else:
        host = 'http://localhost:8000'
    context = {'user': user, 'host': host, 'sign': signer.sign(user.username)}
    subject = render_to_string('email/activation_letter_subject.txt', context)
    body_text = render_to_string('email/activation_letter_body.txt', context)
    '''Класс User, реализующий модель пользователя, предлагает метод email_user(),
        отправляющий письмо текущему зарегистрированному пользователю:'''
    user.email_user(subject, body_text)


def get_timestamp_path(instance, filename):
    return '%s%s' % (datetime.datetime.now().timestamp(), splitext(filename)[1])