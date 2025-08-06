from random import choice
from typing import NamedTuple
from ddframework.statemachine import StateMachine


class Place(NamedTuple):
    description: str
    exits: tuple[str]
    followups: tuple[str]


PLACES = {
    'center': Place(description='I am in the middle of a large room.',
                    exits=('north', 'south', 'east', 'west'),  # ty: ignore[invalid-argument-type]
                    followups=('north', 'south', 'west', 'east')),  # ty: ignore[invalid-argument-type]
    'north': Place(description='I am at the north wall of the large room.',
                   exits=('south', 'west', 'east'),  # ty: ignore[invalid-argument-type]
                   followups=('north', 'center', 'west', 'east')),  # ty: ignore[invalid-argument-type]
    'south': Place(description='I am at the south wall of the large room.',
                   exits=('north', 'west', 'east'),  # ty: ignore[invalid-argument-type]
                   followups=('center', 'south', 'west', 'east')),  # ty: ignore[invalid-argument-type]
    'west': Place(description='I am at the west wall of the large room.',
                  exits=('north', 'south', 'west', 'east'),  # ty: ignore[invalid-argument-type]
                  followups=('north', 'south', 'door', 'center')),  # ty: ignore[invalid-argument-type]
    'east': Place(description='I am at the east window of the large room.',
                  exits=('north', 'south', 'west'),  # ty: ignore[invalid-argument-type]
                  followups=('north', 'south', 'center', 'east')),  # ty: ignore[invalid-argument-type]
    'door': Place(description='I am at the west door of the large room.',
                  exits=('north', 'south', 'west', 'east'),  # ty: ignore[invalid-argument-type]
                  followups=('north', 'south', 'west', 'hallway')),  # ty: ignore[invalid-argument-type]
    'hallway': Place(description='I am in the hallway.',
                     exits=('west', 'east'),  # ty: ignore[invalid-argument-type]
                     followups=('hallway', 'hallway', None, 'west')),  # ty: ignore[invalid-argument-type]
}

MOVE_MAP = {'north': 0, 'south': 1, 'west': 2, 'east': 3}

sm = StateMachine()
for identifier, state in PLACES.items():
    sm.add(identifier, *state.followups)

walker = sm.walker()
state = next(walker)

while True:
    place = PLACES[state]
    move = choice(list(place.exits))
    print(f'{place.description}  There are exits {", ".join(place.exits)}')
    print(f"I'm walking {move}")
    try:
        state = walker.send(MOVE_MAP[move])
    except StopIteration:
        break

print('I am outside')
