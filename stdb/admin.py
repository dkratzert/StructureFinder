from django.contrib import admin

# Register your models here.
from stdb.models import Dataset, RefineResult

admin.site.register(Dataset)
admin.site.register(RefineResult)