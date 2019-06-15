from django.db import models

# Create your models here.


class Orig(models.Model):
    roam = models.CharField(max_length=20)
    host = models.CharField(max_length=20)
    msisdn = models.BigIntegerField()
    imsi = models.BigIntegerField()
    day = models.CharField(max_length=20)


class RoamIn(models.Model):
    msisdn = models.CharField(max_length=20)
    host = models.CharField(max_length=20)
    day = models.CharField(max_length=20)


class RoamOut(models.Model):
    msisdn = models.CharField(max_length=20)
    month = models.CharField(max_length=20)
    for i in range(32):
        locals()['day' + str(i)] = models.CharField(max_length=20)
