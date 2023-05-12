from django.contrib.auth.models import AbstractUser
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from django.core import validators
from django.db import models
from django.db.models.signals import post_save
from django.dispatch import Signal, receiver

from main.utilities import send_activation_notification, get_timestamp_path


# Create your models here.
class AdvUser(AbstractUser):
    is_activated = models.BooleanField(default=True, db_index=True, verbose_name='Прошёл активацию?')
    send_messages = models.BooleanField(default=True, verbose_name='Слать оповещения о новых комментариях?')

    def delete(self, *args, **kwargs):
        '''
        В разд. 34.2.1 мы сделали так, чтобы при удалении объявления явно удалялись все
        связанные с ним дополнительные иллюстрации. Это нужно для того, чтобы прило
        жение django_cleanup удалило хранящие их файлы.
        Теперь сделаем так, чтобы при удалении пользователя удалялись оставленные им
        объявления. Для этого добавим в код модели AdvUser следующий фрагмент:
        '''
        for bb in self.bb_set.all():
            bb.delete()
        super().delete(*args, **kwargs)

    class Meta(AbstractUser.Meta):
        pass


class Rubric(models.Model):
    name = models.CharField(max_length=20, db_index=True, unique=True, verbose_name='Название')
    order = models.SmallIntegerField(default=0, db_index=True, verbose_name='Порядок')
    super_rubric = models.ForeignKey('SuperRubric', on_delete=models.PROTECT, null=True, blank=True,
                                     verbose_name='Надрубрика')


class SuperRubricManager(models.Manager):
    def get_queryset(self):
        return super().get_queryset().filter(super_rubric__isnull=True)


class SuperRubric(Rubric):
    objects = SuperRubricManager()

    class Meta:
        proxy = True
        ordering = ['order', 'name']
        verbose_name = 'Надрубрика'
        verbose_name_plural = 'Надрубрики'


class SubRubricManager(models.Manager):
    def get_queryset(self):
        return super().get_queryset().filter(super_rubric__isnull=False)


class SubRubric(Rubric):
    objects = SubRubricManager()

    def __str__(self):
        return '%s - %s' % (self.super_rubric.name, self.name)

    class Meta:
        proxy = True
        ordering = ('super_rubric__order', 'super_rubric__name', 'order', 'name')
        verbose_name = 'Подрубрика'
        verbose_name_plural = 'Подрубрики'


class Bb(models.Model):
    rubric = models.ForeignKey(SubRubric, on_delete=models.PROTECT,
                               verbose_name='Рубрика',
                               )
    title = models.CharField(max_length=40, verbose_name='Товар',
                             help_text='Товар должен быть не более 40 символов',
                             validators=[
                                 validators.RegexValidator('')
                             ]
                             )
    content = models.TextField(verbose_name='Описание')
    price = models.FloatField(default=0, verbose_name='Цена')
    contacts = models.TextField(verbose_name='Контакты')
    image = models.ImageField(blank=True, upload_to=get_timestamp_path,
                              verbose_name='Изображение')
    author = models.ForeignKey(AdvUser, on_delete=models.CASCADE,
                               verbose_name='Автор объявления')
    is_active = models.BooleanField(default=True, db_index=True,
                                    verbose_name='Выводить в списке?')
    created_at = models.DateTimeField(auto_now_add=True, db_index=True,
                                      verbose_name='Опубликовано')

    def delete(self, *args, **kwargs):
        '''
        В переопределенном методе delete () перед удалением текущей записи мы перебираем
        и вызовом метода delete () удаляем все связанные дополнительные иллюстрации.
        При вызове метода delete () возникает сигнал post delete, обрабатываемый
        приложением django cieanup, которое в ответ удалит все файлы, хранящиеся
        в удаленной записи
        '''
        for ai in self.additionalimage_set.all():
            ai.delete()
        super().delete(*args, **kwargs)

    class Meta:
        verbose_name_plural = 'Объявления'
        verbose_name = 'Объявление'
        ordering = ['-created_at']


class AdditionalImage(models.Model):
    bb = models.ForeignKey(Bb, on_delete=models.CASCADE,
                           verbose_name='Объявление')
    image = models.ImageField(upload_to=get_timestamp_path,
                              verbose_name='Изображение', help_text='Подгружать надо аккуратно')

    class Meta:
        verbose_name_plural = 'Дополнительные иллюстрации'
        verbose_name = 'Дополнительная иллюстрация'


class Comment(models.Model):
    bb = models.ForeignKey(Bb, on_delete=models.CASCADE, verbose_name='Объявление')
    author = models.CharField(max_length=30, verbose_name='Автор')
    content = models.TextField(verbose_name='Содержание')
    is_active = models.BooleanField(default=True, db_index=True, verbose_name='Выводить на экран?')
    created_at = models.DateTimeField(auto_now_add=True, db_index=True, verbose_name='Опубликован')

    class Meta:
        verbose_name_plural = 'Комментарии'
        verbose_name = 'Комментарий'
        ordering = ['-created_at']


user_registered = Signal()


class Note(models.Model):
    '''
     Пример создания маодели которая несёт полиморфную связь(каждая запись этой модели
     может связаться с записью любой другой мадели)
     К сожалению, поле полиморфной связи нельзя использовать в условиях фильтра
     ции(но остальные поля этой поддерживают фильтрацию).
    '''
    content = models.TextField()
    contenttype = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    object_id = models.PositiveIntegerField()
    content_object = GenericForeignKey(ct_field='contenttype', fk_field='object_id')

    class Meta:
        pass


def user_registered_dispatcher(sender, **kwargs):
    send_activation_notification(kwargs['instance'])


user_registered.connect(user_registered_dispatcher)


@receiver(post_save, sender=Comment)
def dispatcher_test(instance, **kwargs):
    pass
