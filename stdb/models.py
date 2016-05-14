import datetime

from django.core.validators import MinValueValidator, MaxValueValidator
from django.db import models

# Create your models here.
from django.forms import fields
from django.utils import timezone


class Dataset(models.Model):
    name = models.CharField(max_length=200)
    flask_name = models.CharField(max_length=200)
    machine = models.CharField(max_length=200)
    operator = models.CharField(max_length=200)
    measure_date = models.DateTimeField('date measured')
    crystal_size_x = models.FloatField(max_length=4, default=0,
                                       validators = [MinValueValidator(0), MaxValueValidator(500)])
    crystal_size_y = models.FloatField(max_length=4, default=0,
                                       validators=[MinValueValidator(0), MaxValueValidator(500)])
    crystal_size_z = models.FloatField(max_length=4, default=0,
                                       validators=[MinValueValidator(0), MaxValueValidator(500)])

    def __str__(self):
        return self.name

    def was_measured_recently(self):
        now = timezone.now()
        return now - datetime.timedelta(days=7) <= self.measure_date <= now

    was_measured_recently.admin_order_field = 'measure_date'
    was_measured_recently.boolean = True
    was_measured_recently.short_description = 'Measured recently?'

    def publishable(self):
        return True
        #return RefineResult.objects.get(id('name'), is_publishable=True)

    publishable.boolean = True



class RefineResult(models.Model):
    dataset = models.ForeignKey(Dataset, on_delete=models.CASCADE, default=0)
    is_publishable = models.BooleanField(default=False)
    is_publishable.short_description = 'Is the structure publishable?'
    cell_a = models.FloatField(max_length=8, default=0, verbose_name='a', validators = [MinValueValidator(0), MaxValueValidator(500)])
    cell_b = models.FloatField(max_length=8, default=0, validators=[MinValueValidator(0), MaxValueValidator(500)])
    cell_c = models.FloatField(max_length=8, default=0, validators=[MinValueValidator(0), MaxValueValidator(500)])
    cell_alpha = models.FloatField(max_length=8, default=0, validators = [MinValueValidator(0), MaxValueValidator(180)])
    cell_beta = models.FloatField(max_length=8, default=0, validators = [MinValueValidator(0), MaxValueValidator(180)])
    cell_gamma = models.FloatField(max_length=8, default=0, validators = [MinValueValidator(0), MaxValueValidator(180)])
    cell_a.short_description = 'Unit Cell Parameter a'
    cell_b.short_description = 'Unit Cell Parameter b'
    cell_c.short_description = 'Unit Cell Parameter c'
    cell_alpha.short_description = 'Unit Cell Parameter alpha'
    cell_beta.short_description = 'Unit Cell Parameter beta'
    cell_gamma.short_description = 'Unit Cell Parameter gamma'

    def __str__(self):
        return self.dataset.name+' dataset '+str(self.id)

