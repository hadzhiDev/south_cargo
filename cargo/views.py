from rest_framework.viewsets import ModelViewSet

from cargo.models import Client
from cargo.serializers import ClientSerializer


class ClientModelViewSet(ModelViewSet):
    serializer_class = ClientSerializer
    queryset = Client.objects.all()

