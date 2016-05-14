from django.contrib import admin

# Register your models here.
from .models import Dataset, RefineResult

class RefineResultInline(admin.StackedInline):
    model = RefineResult
    extra = 0
    verbose_name = 'Refine Result'
    verbose_name_plural = 'Refine Results'
    #fields = [
    #     'is_publishable'
    #]
    #inlines = [UnitCell]
    #fieldsets = [
     #   ('Unit Cell', {'fields': ['cell']}),
    #]

class DatasetAdmin(admin.ModelAdmin):
    fieldsets = [
        ('Measurement', {'fields': ['name', 'measure_date', 'operator', 'flask_name', 'machine']}),
    ]
    inlines = [RefineResultInline]
    list_display = ('name', 'measure_date', 'was_measured_recently', 'publishable', 'machine')
    list_filter = ['measure_date']
    search_fields = ['name', 'operator', 'flask_name']

admin.site.register(Dataset, DatasetAdmin)
admin.site.register(RefineResult)

"""
Add possibility to add machines like Choices in https://docs.djangoproject.com/en/1.9/intro/tutorial07/
"""