from django.apps import apps
from django.utils.decorators import method_decorator
from django.views.decorators.cache import never_cache
from rest_framework import viewsets

from .pagination import AdminAPIPagination
from .permissions import IsAPIUser
from .serializers import AdminAPISerializer


@method_decorator(never_cache, name="list")
@method_decorator(never_cache, name="retrieve")
class AdminAPIViewSet(viewsets.ModelViewSet):
    model_app_label = "api"
    model_name = None
    serializer_base = AdminAPISerializer
    serializer_class = None
    route_ns = "admin_rest"

    permission_classes = [IsAPIUser]

    # Pagination
    pagination_class = AdminAPIPagination

    # TODO: Filter, idk figure something out,
    #   don't reinvent odata $filter and build an injection attack.
    # TODO: Natural Keys, router support needed.

    # Caching
    # AdminAPI does not support a caching scheme, so we apply a Cache-Control=Never
    # for HTTP GETs (list/retrieve).

    # Response Shape
    # AdminAPI is inspired by, but noncompliant with JSON:API at this time.
    # The paginator provides the top level list response shape.

    @property
    def model(self):
        return apps.get_model(
            app_label=str(self.model_app_label), model_name=str(self.model_name)
        )

    def get_queryset(self):
        model = self.model
        return model.objects.all()

    def get_serializer_class(self):
        if self.serializer_class is None:

            class AdminSerializer(self.serializer_base):
                class Meta(self.serializer_base.Meta):
                    model = self.model

            self.serializer_class = AdminSerializer
        return self.serializer_class

    def get_serializer_context(self,):
        ctx = super().get_serializer_context()
        # add the route namespace to the serializer context
        ctx["route_ns"] = self.route_ns
        return ctx
