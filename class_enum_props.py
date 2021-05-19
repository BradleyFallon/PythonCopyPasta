# see https://www.youtube.com/watch?v=gPPDXgCMZ0k


from enum import Enum, auto

class Value(Enum):
    ONE = auto()
    TWO = auto()
    THREE = auto()
    FOUR = auto()
    FIVE = auto()
    SIX = auto()
    SEVEN = auto()
    EIGHT= auto()
    NINE = auto()
    TEN = auto()
    JACK = auto()
    QUEEN = auto()
    KING = auto()
    ACE = auto()

class Suit(Enum):
    HEART = auto()
    SPADE = auto()
    DIAMOND = auto()
    CLUB = auto()

class Card:
    def __init__(self, suit: Suit, value: Value):
        self._suit = None
        self._value = None
        self.suit = suit
        self.value = value

    @property
    def suit(self) -> Suit:
        return self._suit

    @suit.setter
    def suit(self, suit: Suit):
        if suit not in Suit:
            raise ValueError
        self._suit = suit

    @property
    def value(self) -> Value:
        return self._value

    @value.setter
    def value(self, value: Value):
        if value not in Value:
            raise ValueError
        self._value = value

    def __repr__(self):
        return f"<Card {self.value} of {self.suit}>"
        
class Deck:
    def __init__(self):
        self.cards: list = [Card(s, v) for s in Suit for v in Value]

    def __repr__(self):
        return '\n'.join([str(c) for c in self.cards])
    

def main():
    deck = Deck()
    print(deck)

if __name__ == '__main__':
    main()
