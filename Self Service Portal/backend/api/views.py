import json
import simplejson
from oidc_auth.authentication import BearerTokenAuthentication
from .models import SfcConfig, TrafficType, VnfConfig
from .permissions import IsOwnerOrReadOnly
from .serializers import SfcSerializer, TrafficTypeSerializer, VnfSerializer
from rest_framework import viewsets, permissions


class SfcViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows an authenticated user to view and edit its own SFC configuration.
    """
    serializer_class = SfcSerializer
    permission_classes = [permissions.IsAuthenticated, IsOwnerOrReadOnly]
    authentication_classes = [BearerTokenAuthentication]

    def perform_create(self, serializer):
        owner = str(self.request.user)
        trafficType = serializer.validated_data.get('trafficType')
        vnfs = serializer.validated_data.get('vnfs')

        sfcConfig = SfcConfig.objects.create(
            owner=owner,
            trafficType=trafficType,
            vnfs=vnfs
        )
        sfc_dict = SfcSerializer(sfcConfig).data

        # TODO: Because of the intermediate string representation of fields, they are not serialized correctly into lists and objects
        # TODO: This is done manually and hacky here, but should be solved more clean.
        sfc_dict['trafficType'] = simplejson.loads(sfc_dict.get('trafficType'))
        sfc_dict['vnfs'] = simplejson.loads(sfc_dict.get('vnfs'))
        for vnf in sfc_dict['vnfs']:
            if vnf['firewallRules'] is None:
                vnf['firewallRules'] = 'None'
            else:
                vnf['firewallRules'] = simplejson.loads(vnf.get('firewallRules'))

            if vnf['bidirectional']:
                vnf['bidirectional'] = 'TRUE'
            else:
                vnf['bidirectional'] = 'FALSE'

        sfc_id = sfc_dict.pop('id', None)

        sfc_json_string = '{\"' + str(sfc_id) + '\": ' + str(sfc_dict).replace("'", '"') + '}'
        print('Add SFC to sfc.json: ' + str(sfc_json_string))
        sfc_json = json.loads(sfc_json_string)

        with open('customer_json/sfc.json', 'r') as json_file_read:
            data = json.load(json_file_read)
            data.update(sfc_json)
            json_file_read.close()
            with open('customer_json/sfc.json', 'w') as json_file_write:
                formatted_data = json.dumps(data, indent=4, sort_keys=False)
                json_file_write.write(formatted_data)
                json_file_write.close()

    def perform_destroy(self, instance):

        with open('customer_json/sfc.json', 'r') as json_file_read:
            sfcs_data = json.load(json_file_read)

            print(str(sfcs_data))
            print(instance.id)

            sfcs_data.pop(str(instance.id), None)
            sfcs_data.update(sfcs_data)
            json_file_read.close()
            with open('customer_json/sfc.json', 'w') as json_file_write:
                formatted_data = json.dumps(sfcs_data, indent=4, sort_keys=False)
                json_file_write.write(formatted_data)
                json_file_write.close()
        instance.delete()

    def get_queryset(self):
        """
        This view should return a list of all the VNFs
        for the currently authenticated user.
        As an admin, return list of all SFCs by all users
        """
        user = self.request.user
        if self.request.user.is_staff:
            return SfcConfig.objects.all()
        else:
            return SfcConfig.objects.filter(owner=user)


class TrafficTypesViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows an authenticated user to view and edit its own TrafficType configuration.
    """
    serializer_class = TrafficTypeSerializer
    permission_classes = [permissions.IsAuthenticated, IsOwnerOrReadOnly]
    authentication_classes = [BearerTokenAuthentication]

    def perform_create(self, serializer):
        owner = str(self.request.user)
        name = serializer.validated_data.get('name')
        ipAddress = serializer.validated_data.get('ipAddress')

        # In case there is a traffic type of the current user, update it,
        # otherwise, create new traffic type object.
        TrafficType.objects.create(
            owner=owner,
            name=name,
            ipAddress=ipAddress
        )

    def get_queryset(self):
        """
        This view should return a list of all the TrafficTypes
        for the currently authenticated user.
        As an admin, return list of all TrafficTypes by all users
        """
        user = self.request.user

        if self.request.user.is_staff:
            return TrafficType.objects.all()
        else:
            return TrafficType.objects.filter(owner=user)


class VNFViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows an authenticated user to view and edit its own TrafficType configuration.
    """
    serializer_class = VnfSerializer
    permission_classes = [permissions.IsAuthenticated, IsOwnerOrReadOnly]
    authentication_classes = [BearerTokenAuthentication]

    def perform_create(self, serializer):
        owner = str(self.request.user)
        applicationName = serializer.validated_data.get('applicationName')
        serviceType = serializer.validated_data.get('serviceType')
        bidirectional = serializer.validated_data.get('bidirectional')
        virtualization = serializer.validated_data.get('virtualization')
        vcpus = serializer.validated_data.get('vcpus')
        vmemory = serializer.validated_data.get('vmemory')
        firewallRules = serializer.validated_data.get('firewallRules')

        VnfConfig.objects.create(
            owner=owner,
            applicationName=applicationName,
            serviceType=serviceType,
            bidirectional=bidirectional,
            virtualization=virtualization,
            vcpus=vcpus,
            vmemory=vmemory,
            firewallRules=firewallRules
        )

    def get_queryset(self):
        """
        This view should return a list of all the TrafficTypes
        for the currently authenticated user.
        As an admin, return list of all TrafficTypes by all users
        """
        user = self.request.user

        if self.request.user.is_staff:
            return VnfConfig.objects.all()
        else:
            return VnfConfig.objects.filter(owner=user)
