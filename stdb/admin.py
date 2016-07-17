from django.contrib import admin

# Register your models here.
from .models import Dataset, Machine



class MachinesAdmin(admin.ModelAdmin):
    model = Machine
    extra = 0

class MachinesInline(admin.StackedInline):
    model = Machine
    extra = 0


class DatasetAdmin(admin.ModelAdmin):
    #inlines = [MachinesInline]
    #ordering = ['-measure_date']
    fieldsets = [
        ('Measurement', {'fields': [('name', 'is_publishable'), 'measure_date', 'operator', 'flask_name',
                                    #'machine',
                                    ('received', 'output')]}),
        ('Files', {'fields': [ 'cif_file', 'res_file' ]}),
        ('Misc', {'fields': ['formula', 'z', 'comment']}),
        ('Results', {'fields': [ ('cell_a', 'cell_b', 'cell_c'),
                                 ('alpha', 'beta', 'gamma'), 'R1_all', 'wR2_all', 'R1_2s', 'wR2_2s',
                                'density', 'mu', 'formular_weight', 'colour', 'shape', 'temperature', 'crystal_system',
                                'space_group', 'volume', 'wavelength', 'radiation_type', 'theta_min', 'theta_max',
                                'measured_refl', 'indep_refl', 'refl_used', 'r_int', 'parameters', 'restraints',
                                'peak', 'hole', 'goof'
                                ]
                     }
         )
    ]
    list_display = ('name', 'measure_date', 'was_measured_recently', 'is_publishable',
                    #'machine',
                    'operator')
    list_filter = ['measure_date']
    search_fields = ['name', 'operator', 'flask_name']


admin.site.register(Dataset, DatasetAdmin)
admin.site.register(Machine, MachinesAdmin)


