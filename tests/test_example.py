from django-dataclass-autoserialize.example import add_number


def test_example():
  assert add_number(2, 3) == 5
