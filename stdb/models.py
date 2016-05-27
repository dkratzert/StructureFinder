import datetime
import os

from django.core.urlresolvers import reverse
from django.core.validators import MinValueValidator, MaxValueValidator
from django.db import models

# Create your models here.
from django.utils.html import escape
from django.utils.safestring import mark_safe




class Dataset(models.Model):
    name = models.CharField(max_length=200, unique=True)
    flask_name = models.CharField(max_length=200)
    formula = models.CharField(max_length=200)
    machine = models.CharField(max_length=200)
    operator = models.CharField(max_length=200, verbose_name='Who measured the structure?')
    picked_at = models.IntegerField(verbose_name='Crystals picked at which temperature?', default=0)
    measure_date = models.DateField(verbose_name='date measured')
    received = models.DateField(verbose_name='date received', blank=True, null=True)
    output = models.DateField(verbose_name='date outgoing', blank=True, null=True)
    crystal_size_x = models.FloatField(max_length=4, default=0, blank=True,
                                       validators=[MinValueValidator(0), MaxValueValidator(500)])
    crystal_size_y = models.FloatField(max_length=4, default=0, blank=True,
                                       validators=[MinValueValidator(0), MaxValueValidator(500)])
    crystal_size_z = models.FloatField(max_length=4, default=0, blank=True,
                                       validators=[MinValueValidator(0), MaxValueValidator(500)])
    colour = models.CharField(max_length=20, blank=True)
    is_publishable = models.BooleanField(default=False)
    service_structure = models.BooleanField(default=False)
    comment = models.TextField(max_length=2000, blank=True)
    cell_a = models.FloatField(max_length=8, default=0, verbose_name='a', validators=[MinValueValidator(0),
                                                                                      MaxValueValidator(500)])
    cell_b = models.FloatField(max_length=8, default=0, verbose_name='b', validators=[MinValueValidator(0),
                                                                                      MaxValueValidator(500)])
    cell_c = models.FloatField(max_length=8, default=0, verbose_name='c', validators=[MinValueValidator(0),
                                                                                      MaxValueValidator(500)])
    alpha = models.FloatField(max_length=8, default=0, validators=[MinValueValidator(0), MaxValueValidator(180)])
    beta = models.FloatField(max_length=8, default=0, validators=[MinValueValidator(0), MaxValueValidator(180)])
    gamma = models.FloatField(max_length=8, default=0, validators=[MinValueValidator(0), MaxValueValidator(180)])
    R1_all = models.FloatField(max_length=5, validators=[MinValueValidator(0),
                                                         MaxValueValidator(1)], blank=True, null=True)
    wR2_all = models.FloatField(max_length=5, validators=[MinValueValidator(0),
                                                          MaxValueValidator(1)], blank=True, null=True)
    R1_2s = models.FloatField(max_length=5, validators=[MinValueValidator(0),
                                                        MaxValueValidator(1)], blank=True, null=True)
    wR2_2s = models.FloatField(max_length=5, validators=[MinValueValidator(0),
                                                         MaxValueValidator(1)], blank=True, null=True)
    density = models.FloatField(max_length=5, verbose_name='density (calc)', blank=True, null=True)
    mu = models.FloatField(max_length=5, verbose_name='absorption [mm-1]', blank=True, null=True)
    formular_weight = models.FloatField(max_length=8, verbose_name='Formular weight', blank=True, null=True)
    shape = models.CharField(max_length=20, blank=True)
    temperature = models.FloatField(max_length=5, verbose_name='Temperature [K]', blank=True, default=0, null=True)
    crystal_system = models.CharField(max_length=15, blank=True)
    space_group = models.CharField(max_length=15, blank=True)
    volume = models.FloatField(max_length=5, blank=True, null=True)
    z = models.IntegerField(blank=True, null=True)
    fnull = models.IntegerField(blank=True, null=True)
    wavelength = models.FloatField(max_length=10, blank=True, null=True)
    radiation_type = models.CharField(max_length=18, blank=True)
    theta_min = models.FloatField(max_length=10, blank=True, null=True)
    theta_max = models.FloatField(max_length=10, blank=True, null=True)
    measured_refl = models.IntegerField(blank=True, null=True)
    # _diffrn_measured_fraction_theta_max:
    completeness = models.IntegerField(blank=True, null=True)
    indep_refl = models.IntegerField(blank=True, null=True)
    refl_used = models.IntegerField(blank=True, null=True)
    r_int = models.FloatField(max_length=10, blank=True, null=True)
    parameters = models.IntegerField(blank=True, null=True)
    restraints = models.IntegerField(blank=True, null=True)
    peak = models.FloatField(max_length=10, blank=True, null=True)
    hole = models.FloatField(max_length=10, blank=True, null=True)
    goof = models.FloatField(max_length=10, blank=True, null=True)
    cell_a.short_description = 'Unit Cell Parameter a'
    cell_b.short_description = 'Unit Cell Parameter b'
    cell_c.short_description = 'Unit Cell Parameter c'
    alpha.short_description = 'Unit Cell Parameter alpha'
    beta.short_description = 'Unit Cell Parameter beta'
    gamma.short_description = 'Unit Cell Parameter gamma'
    z.empty_value_display = '?'

    class Meta:
        ordering = ['-measure_date', '-name']

    def get_model_fields(self):
        return self._meta.fields

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse('stdb:detail', kwargs={'pk': self.id})

    def was_measured_recently(self):
        now = datetime.date.today()
        return now - datetime.timedelta(days=7) <= self.measure_date <= now

    is_publishable.short_description = 'publishable?'
    is_publishable.boolean = True
    was_measured_recently.admin_order_field = 'measure_date'
    was_measured_recently.boolean = True
    was_measured_recently.short_description = 'Measured recently?'

    def publishable(self):
        if self.is_publishable:
            return True
        else:
            return False

    def format_formula(self):
        """
        Taken from: http: // www.mzan.com / article / 34067043 - django -
        not -rendering - html -
        with-tags - assigned - in -python - code.shtml  # sthash.QXxIeVLy.dpuf
        :return: formula as html string
        """
        new_string = ''
        for n, item in enumerate(self.formula):
            try:
                before = '.,-'.find(self.formula[n + 1])
            except IndexError:
                before = False
            try:
                after = '.,-'.find(self.formula[n - 1])
            except IndexError:
                after = False
            # make shure before and after the digit is no komma or dash. like in 1,2-Diol
            if item.isdigit() and not (before > 0 or after > 0):
                # we know item is a number, so no need to escape it
                new_string += '<sub>'+ item +'</sub>'
            else:
                new_string += escape(item)
                # we built new_string from safe parts, so we can mark it as
                # safe to prevent autoescaping
        return mark_safe(new_string.replace(' ', ''))

    def format_scpace_group(self):
        """
        find all 2(1), 3(1), 3(2), 4(1), 4(2), 6(1), 6(2), 6(3), 6(4), 6(5) and replace with 2<sub>1<sub> ....
        find all -number and replace with <bar>number</bar>
        make all characters italic
        :return:
        """
        pass


STATE_CHOICES = (
    (1,  'Smart APEXII Quazar'),
    (2,   'R-AXIS Spider'),
    (3, 'VENTURE'),
    (4, 'other'),
)
STATE_DICT = dict(STATE_CHOICES)


class Machines(models.Model):
    name = models.ForeignKey(Dataset, on_delete=models.CASCADE)
    machine = models.PositiveSmallIntegerField(choices=STATE_CHOICES, default=1)

    def __str__(self):
        return '{}'.format(STATE_DICT[self.machine])


def get_filename(instance, name):
    """
    returns the path to where the uploaded file should be stored
    :param instance: An instance of the model where the FileField is defined.
    :param name: Filename to be stored
    :return: full path to store into
    """
    path = os.path.join('cif_file/', os.path.join(instance.dataset.name, name))
    print('upload path:', path, '######')
    return path


class Files(models.Model):
    dataset = models.ForeignKey(Dataset, on_delete=models.CASCADE)
    cif_file = models.FileField(upload_to='cif_file/', verbose_name='CIF File', blank=True)
    res_file = models.FileField(upload_to='cif_file/', verbose_name='RES File', blank=True)
    raw_file = models.FileField(upload_to=get_filename, verbose_name='raw_file', blank=True)
    abs_file = models.FileField(upload_to=get_filename, verbose_name='abs File', blank=True)
    ls_file = models.FileField(upload_to=get_filename, verbose_name='_ls File', blank=True)
    fcf_file = models.FileField(upload_to=get_filename, verbose_name='fcf File', blank=True)
    other_file = models.FileField(upload_to=get_filename, verbose_name='other File', blank=True)
    pdf_file = models.FileField(upload_to=get_filename, verbose_name='Checkfif File', blank=True)
    report_file = models.FileField(upload_to=get_filename, verbose_name='report File', blank=True)
    hkl_file = models.FileField(upload_to=get_filename, verbose_name='hkl File', blank=True)
    p4p_file = models.FileField(upload_to=get_filename, verbose_name='p4p File', blank=True)
    comment = models.TextField(max_length=2000, blank=True)

    def __str__(self):
        return self.dataset.name

    def getsize(self, file):
        try:
            file.size
        except:
            return 'File not found!'
        if 1000 <= file.size < 1000000:
            return '{:.2f} {}'.format(file.size / 1000, 'kB')
        else:
            return '{:.2f} {}'.format(file.size / 1000000, 'MB')

    class Meta:
        pass
        #files = Files.objects.all()



class Customer(models.Model):
    dataset = models.ManyToManyField(Dataset)
    measured_for = models.CharField(max_length=120, verbose_name='Customer', blank=True)
    email = models.EmailField(blank=True)
    ak = models.CharField(max_length=120, verbose_name='Workgroup')
