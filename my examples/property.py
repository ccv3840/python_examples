from dataclasses import dataclass


class Circle:
    def __init__(self, radius):
        self._radius = radius

    @property
    def radius(self):
        """Get the radius of the circle."""
        return self._radius

    @radius.setter
    def radius(self, value):
        """Set the radius of the circle."""
        if value < 0:
            raise ValueError("Radius cannot be negative.")
        self._radius = value

    @property
    def diameter(self):
        """Get the diameter of the circle."""
        return 2 * self._radius


c1 = Circle(5)
print(c1)


class Math:
    @staticmethod
    def add(a, b):
        return a + b

    @staticmethod
    def mul(a, b):
        return a * b


print(Math())


class Person:
    species = "Homo sapiens"

    @classmethod
    def get_species(cls):
        return cls.species


print(Person.get_species())
print(Person())


@dataclass
class Product:
    name: str
    price: float
    quantity: int = 0

    def total(self):
        return self.price * self.quantity


# Goal modify the behavior of the sub class with meta class without touching the sub class itself


class Meta(type):
    def __new__(self, class_name, bases, attrs):
        print(attrs)

        a = {}

        for name, value in attrs.items():
            if name.startswith("__"):
                a[name] = value

            else:
                a[name.upper()] = value
        print(a)
        return type(class_name, bases, a)


class Dog(metaclass=Meta):
    x = 5
    y = 8

    def hello(self):
        print("Hello, my dog!")


a = Dog()

print(a.x)  # AttributeError: 'Dog' object has no attribute 'x'. Did you mean: 'X'?e
