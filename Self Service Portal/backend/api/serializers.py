from rest_framework import serializers
from .models import SfcConfig, TrafficType, VnfConfig


class SfcSerializer(serializers.ModelSerializer):
    class Meta:
        model = SfcConfig
        owner = serializers.ReadOnlyField(source='owner.username')
        fields = ('id', 'owner', 'trafficType', 'vnfs')


class TrafficTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = TrafficType
        owner = serializers.ReadOnlyField(source='owner.username')
        fields = ('id', 'owner', 'name', 'ipAddress')

class VnfSerializer(serializers.ModelSerializer):
    class Meta:
        model = VnfConfig
        owner = serializers.CharField(max_length=200)
        applicationName = serializers.CharField(max_length=200)
        serviceType = serializers.CharField(max_length=200)
        bidirectional = serializers.BooleanField()
        virtualization = serializers.CharField(max_length=200)
        vcpus = serializers.IntegerField()
        vmemory = serializers.IntegerField()
        firewallRules = serializers.CharField(max_length=4000)
        fields = ('id', 'owner', 'applicationName', 'serviceType', 'bidirectional', 'virtualization', 'vcpus', 'vmemory', 'firewallRules')