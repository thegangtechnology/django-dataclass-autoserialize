# django-dataclass-autoserialize

An extension of slightly modified oxan's [django-dataclass-serialize](https://github.com/oxan/djangorestframework-dataclasses). 
Making it much more enjoyable to use with [drf-yasg](https://github.com/axnsan12/drf-yasg).

```python
@dataclass
class PostParam(Autoserialize):
    a: int
    b: int
    @classmethod
    def example(cls) -> 'PostParam':
        # this is actually optional but it will show up
        # in swagger doc
        return cls(a=3, b=2)

@dataclass
class RandomReponse(AutoSerialize):
    msg: str
    result: int
    @classmethod
    def example(cls) -> 'RandomResponse':
        return cls(msg='hello world', result=5)

class RandomView(APIView):
    @autoserialize_swagger(
        body=PostParam,
        response=RandomResponse
    )
    def post(self, request: Request) -> Response:
        param = PostParam.from_request(request)
        ...
        return RandomReponse(msg='hello', 
                             result=param.a + param.b).to_response()
```
