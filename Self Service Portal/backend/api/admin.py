from django.contrib import admin
from .models import SfcConfig, VnfConfig, TrafficType

# Register your models here.
admin.site.register(SfcConfig)
admin.site.register(TrafficType)
admin.site.register(VnfConfig)