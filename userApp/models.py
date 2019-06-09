from django.db import models

# Create your models here.


class Orig(models.Model):
    roam = models.CharField(max_length=20)
    host = models.CharField(max_length=20)
    msisdn = models.BigIntegerField()
    imsi = models.BigIntegerField()
    day = models.DateField()

    # class Meta:
    #     abstract = True


# class Student(Orig):
#     class Meta(Orig.Meta):
#         db_table = 'aaa'
#         db_table = 'bbb'
#         db_table = 'ccc'


class RoamIn(models.Model):
    msisdn = models.CharField(max_length=20)
    host = models.CharField(max_length=20)
    date = models.DateField()


class RoamOut(models.Model):
    msisdn = models.CharField(max_length=20)
    month = models.CharField(max_length=20)
    for i in range(32):
        locals()['day' + str(i)] = models.CharField(max_length=20)
