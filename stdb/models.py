import datetime

from django.db import models

# Create your models here.
from django.utils import timezone


class Dataset(models.Model):
    name = models.CharField(max_length=200)
    flask_name = models.CharField(max_length=200)
    machine = models.CharField(max_length=200)
    operator = models.CharField(max_length=200)
    measure_date = models.DateTimeField('date measured')

    def __str__(self):
        return self.name

    def was_measured_recently(self):
        now = timezone.now()
        return now - datetime.timedelta(days=7) <= self.measure_date <= now

    was_measured_recently.admin_order_field = 'measure_date'
    was_measured_recently.boolean = True
    was_measured_recently.short_description = 'Measured recently?'


class RefineResult(models.Model):
    dataset = models.ForeignKey(Dataset, on_delete=models.CASCADE, default=0)
    struct_name = models.CharField(max_length=200)
    cell_a = models.FloatField(max_length=8, default=0)
    cell_a.short_description = 'Unit Cell Parameter a'
    cell_b = models.FloatField(max_length=8, default=0)
    cell_b.short_description = 'Unit Cell Parameter b'
    cell_c = models.FloatField(max_length=8, default=0)
    cell_c.short_description = 'Unit Cell Parameter c'

    def __str__(self):
        return self.struct_name

