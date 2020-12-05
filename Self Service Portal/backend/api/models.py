from django.db import models

class VnfConfig(models.Model):
    owner = models.CharField(max_length=200)
    applicationName = models.CharField(max_length=200)
    serviceType = models.CharField(max_length=200) # TODO: TrafficType relation instead of string
    bidirectional = models.BooleanField(default=False)
    virtualization = models.CharField(max_length=200)
    vcpus = models.IntegerField()
    vmemory = models.IntegerField()
    firewallRules = models.CharField(max_length=4000, blank=True, null=True, auto_created=True)

class SfcConfig(models.Model):
    owner = models.CharField(max_length=200)
    trafficType = models.CharField(max_length=200) # TODO: TrafficType relation instead of string
    vnfs = models.CharField(max_length=2000) # TODO: VnfConfig[] relation instead of string

class TrafficType(models.Model):
    owner = models.CharField(max_length=200)
    name = models.CharField(max_length=200)
    ipAddress = models.CharField(max_length=200)
