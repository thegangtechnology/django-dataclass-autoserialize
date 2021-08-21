from __future__ import annotations

import functools
import os
from dataclasses import dataclass
from unittest import TestCase, mock
from unittest.mock import patch

import pytest

from django_dataclass_autoserialize import AutoSerialize, swagger_post_schema, TGSerializer, swagger_get_schema


@dataclass
class Point(AutoSerialize):
    x: float
    y: float

    @classmethod
    def validate_data(cls, obj: Point):
        from rest_framework.exceptions import ValidationError
        if obj.x + obj.y > 1000:
            raise ValidationError('too far')
        return obj

    @classmethod
    def example(cls) -> Point:
        return cls(x=1.2, y=3.4)


@dataclass
class Line(AutoSerialize):
    start: Point
    end: Point

    @classmethod
    def example(cls) -> Line:
        return cls(start=Point.example(), end=Point.example())


def custom_django_config(f):
    @functools.wraps(f)
    def ret(*arg, **kwds):
        with mock.patch.dict(os.environ, {"DJANGO_SETTINGS_MODULE": "django_dataclass_autoserialize.settings_test"},
                             clear=True) as patch:
            return f(*arg, **kwds)

    return ret


class TestSimpleAutoSerialize(TestCase):

    def setUp(self):
        self.point = Point(x=1.2, y=3.4)
        self.point_data = {'x': 1.2, 'y': 3.4}

    def test_as_can_serialize(self):
        ser = Point.serializer()
        assert ser(self.point).data == self.point_data

    def test_can_do_to_data(self):
        assert self.point.to_data() == self.point_data

    def test_as_can_deserialize(self):
        ser = Point.serializer()
        obj = ser(data=self.point_data)
        assert obj.is_valid()
        assert obj.save() == self.point

    def test_can_do_from_data(self):
        p = self.point.from_data(self.point_data)
        assert p == self.point

    def test_can_convert_from_post_request(self):
        class MockedPostRequest:
            data = self.point_data

        request = MockedPostRequest()
        p = Point.from_post_request(request)
        assert p == self.point

    def test_can_convert_from_get_request(self):
        obj = self

        class QueryDict:
            def dict(self):
                return obj.point_data

        class MockedGetRequest:
            query_params = QueryDict()

        request = MockedGetRequest()
        p = Point.from_get_request(request)
        assert p == self.point

    def test_can_convert_to_response(self):
        with patch('django_dataclass_autoserialize.Response') as mock:
            res = self.point.to_response()
            mock.assert_called_once()
            mock.assert_called_with(self.point_data)
            assert res is not None

    @custom_django_config
    def test_as_does_validation(self):
        from rest_framework.exceptions import ValidationError
        with pytest.raises(ValidationError):
            Point.from_data({'x': 'hello', 'y': 3.0})

    @custom_django_config
    def test_as_can_do_custom_validation(self):
        from rest_framework.exceptions import ValidationError
        with pytest.raises(ValidationError):
            Point.from_data({'x': 1000, 'y': 1})

    def test_as_has_swagger_ref(self):
        ser = Point.serializer()
        assert ser.Meta.ref_name == 'Point'

    def test_as_has_swagger_example(self):
        ser = Point.serializer()
        example = ser.Meta.swagger_schema_fields['example']
        assert example == self.point_data

    @custom_django_config
    def test_swagger_post_schema(self):
        with patch('drf_yasg.utils.swagger_auto_schema') as mock:
            f = swagger_post_schema(body_type=Line,
                                    response_types={200: Point})
            assert callable(f)
            kwargs = mock.call_args.kwargs
            assert issubclass(kwargs['request_body'], TGSerializer)
            assert len(kwargs['responses']) == 1
            assert 200 in kwargs['responses']
            for k, v in kwargs['responses'].items():
                assert issubclass(v, TGSerializer)

    @custom_django_config
    def test_swagger_get_schema(self):
        with patch('drf_yasg.utils.swagger_auto_schema') as mock:
            f = swagger_get_schema(query_type=Line,
                                   response_types={200: Point})
            assert callable(f)
            kwargs = mock.call_args.kwargs
            assert issubclass(kwargs['query_serializer'], TGSerializer)
            assert len(kwargs['responses']) == 1
            assert 200 in kwargs['responses']
            for k, v in kwargs['responses'].items():
                assert issubclass(v, TGSerializer)

    def test_can_serialize_nested(self):
        line = Line(start=Point(1.2, 3.4), end=Point(5.6, 7.8))
        got = line.to_data()
        exp = {
            'start': {'x': 1.2, 'y': 3.4},
            'end': {'x': 5.6, 'y': 7.8}
        }
        assert got == exp

    def test_can_deserialize_nested(self):
        data = {
            'start': {'x': 1.2, 'y': 3.4},
            'end': {'x': 5.6, 'y': 7.8}
        }
        got = Line.from_data(data)
        assert got == Line(start=Point(1.2, 3.4), end=Point(5.6, 7.8))
