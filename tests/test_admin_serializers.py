from unittest.mock import MagicMock, patch, sentinel

from sfdo_template_helpers.admin.serializers import AdminAPISerializer


class TestAdminAPISerializer:
    def test_build_url_field(self):
        class SubclassedAdminAPISerializer(AdminAPISerializer):
            class Meta:
                class model:
                    class _meta:
                        object_name = "Foo"

        serializer = SubclassedAdminAPISerializer(context={"route_ns": "route_ns"})
        serializer.serializer_url_field = sentinel.serializer_url_field
        expected = (sentinel.serializer_url_field, {"view_name": "route_ns:foo-detail"})

        assert serializer.build_url_field(None, None) == expected

    def test_build_relational_field(self):
        relation_info = MagicMock()
        relation_info.related_model = sentinel.related_model
        relation_info.related_model._meta = MagicMock()
        relation_info.related_model._meta.object_name = "Foo"
        method_name = "rest_framework.serializers.HyperlinkedModelSerializer.build_relational_field"
        with patch(method_name) as build_relational_field:
            build_relational_field.return_value = (
                sentinel.field_class,
                {"view_name": "foo-detail"},
            )

            serializer = AdminAPISerializer(context={"route_ns": "route_ns"})
            expected = (sentinel.field_class, {"view_name": "route_ns:foo-detail"})
            assert serializer.build_relational_field(None, relation_info) == expected

    def test_build_relational_field_not_hyperlinked(self):
        relation_info = MagicMock()
        relation_info.related_model = sentinel.related_model
        relation_info.related_model._meta = MagicMock()
        relation_info.related_model._meta.object_name = "Foo"
        method_name = "rest_framework.serializers.HyperlinkedModelSerializer.build_relational_field"
        with patch(method_name) as build_relational_field:
            build_relational_field.return_value = (sentinel.field_class, {})

            serializer = AdminAPISerializer(context={"route_ns": "route_ns"})
            expected = (sentinel.field_class, {})
            assert serializer.build_relational_field(None, relation_info) == expected
