from django.contrib import admin

# Register your models here.
from .models import Dataset, Machines, Files

#from .models import Document

"""
class DocumentInline(admin.TabularInline):
    model = Document
    extra = 1
    verbose_name = 'File'
    verbose_name_plural = 'Files'
    fieldsets = [
        ('Data files', {'fields': ['cif_file']
                        }
         )
    ]
"""

class MachinesAdmin(admin.ModelAdmin):
    pass

class MachinesInline(admin.StackedInline):
    model = Machines
    extra = 0

class FilesAdmin(admin.ModelAdmin):
    pass

class FilesInline(admin.StackedInline):
    model = Files
    extra = 0
    #fieldsets = [
    #    ('Data files', {'fields': ['cif_file', 'res_file']
    #                    }
    #     )
    #]

class DatasetAdmin(admin.ModelAdmin):
    inlines = [MachinesInline, FilesInline]
    #ordering = ['-measure_date']
    fieldsets = [
        ('Measurement', {'fields': [('name', 'is_publishable'), 'measure_date', 'operator', 'flask_name', 'machine',
                                    ('received', 'output')]}),
        #('Files', {'fields': [ 'cif_file', 'res_file' ]}),
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
    list_display = ('name', 'measure_date', 'was_measured_recently', 'is_publishable', 'machine', 'operator')
    list_filter = ['measure_date']
    search_fields = ['name', 'operator', 'flask_name']


admin.site.register(Dataset, DatasetAdmin)
#admin.site.register(Files, FilesAdmin)

"""
Add possibility to add machines like Choices in https://docs.djangoproject.com/en/1.9/intro/tutorial07/
"""
