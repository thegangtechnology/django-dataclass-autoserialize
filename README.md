# django-dataclass-autoserialize

An extension of slightly modified
oxan's [django-dataclass-serialize](https://github.com/oxan/djangorestframework-dataclasses). Making it much more
enjoyable to use with [drf-yasg](https://github.com/axnsan12/drf-yasg).

# Install

pip install django-dataclass-autoserialize

# Documentation

The goal of this pacakge is to make the apiview as succint as possible. The main pain point it is trying solve is

1) Having to define the param class and serialize seperately.
2) Having it integrate with drf-yasg without having to duplicate information.

## Simple Usage

Here is an example of a typical usage. (Full project example at ...)

```python
from django_dataclass_autoserialize import AutoSerialize, swagger_post_schema, swagger_get_schema
from dataclasses import dataclass


@dataclass
class InputParam(Autoserialize):
    a: int
    b: int

    @classmethod
    def example(cls) -> 'PostParam':
        # this is actually optional but it will show up
        # in swagger doc
        return cls(a=3, b=2)


@dataclass
class ComputeResponse(AutoSerialize):
    msg: str
    result: int

    @classmethod
    def example(cls) -> 'RandomResponse':
        return cls(msg='hello world', result=5)


class AddView(APIView):

    @swagger_post_schema(
        body_type=InputParam,
        response_types={200: ComputeResponse}
    )
    def post(self, request: Request) -> Response:
        param = InputParam.from_request(request)
        return ComputeResponse(msg='add successfully',
                               result=param.a + param.b).to_response()


class SubtractView(APIView):
    @swagger_get_schema(
        query_type=InputParam,
        response_types={200: ComputeResponse}
    )
    def get(self, request: Request) -> Response:
        param = InputParam.from_request(request)
        return ComputeResponse(msg='subtract successfully',
                               result=param.a - param.b).to_response()

```

Then the swagger will shows up like the following

## Customization

Under the hood it uses [djangorestframework-dataclasses](https://github.com/oxan/djangorestframework-dataclasses). So
all the customization that can be done for dataclass is applied here as well. For example, you can
add `serializer_kwargs` like so

```python
@dataclasses.dataclass
class Person:
    email: str = dataclasses.field(metadata={'serializer_field': fields.EmailField()})
    age: int = dataclasses.field(metadata={'serializer_kwargs': {'min_value': 0}})
```

## Validation

The validation of the object can be done by overiding 
`validate_data(cls, obj)` method. For example
```python
class Numbers(AutoSerialize):
    a: int
    b: int

    @classmethod
    def validate_data(cls, obj: Numbers):
        from rest_framework.exceptions import ValidationError
        if obj.a + obj.b > 1000:
            raise ValidationError('too big')
        return obj
```

## Swagger

drg-yasg integration is done through `swagger_get_schema` and `swagger_get_schema`
decorator. See simple example for the usage. keywords other than `query_type/body_type` and `response_types`
are forwarded to drf-yasg's `swagger_auto_schema`.
