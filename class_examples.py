class MyClass:
    # You can optionally declare instance variables in the class body
    attr: int
    # This is an instance variable with a default value
    charge_percent: int = 100

    # The "__init__" method doesn't return anything, so it gets return
    # type "None" just like any other method that doesn't return anything
    def __init__(self) -> None:
        ...

    # For instance methods, omit type for "self"
    def my_method(self, num: int, str1: str) -> str:
        return num * str1

# User-defined classes are valid as types in annotations
x: MyClass = MyClass()

# You can use the ClassVar annotation to declare a class variable
class Car:
    seats: ClassVar[int] = 4
    passengers: ClassVar[List[str]]

# You can also declare the type of an attribute in "__init__"
class Box:
    def __init__(self) -> None:
        self.items: List[str] = []




from dataclasses import dataclass

@dataclass
class InventoryItem:
    """Class for keeping track of an item in inventory."""
    name: str
    unit_price: float
    quantity_on_hand: int = 0

    def total_cost(self) -> float:
        return self.unit_price * self.quantity_on_hand
"""        
Will add, among other things, a __init__() that looks like:

def __init__(self, name: str, unit_price: float, quantity_on_hand: int=0):
    self.name = name
    self.unit_price = unit_price
    self.quantity_on_hand = quantity_on_hand
"""