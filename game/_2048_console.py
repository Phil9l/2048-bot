from models import Field, Direction, Direction


f = Field()
moves = {
    'd': Direction.DOWN,
    'l': Direction.LEFT,
    'u': Direction.UP,
    'r': Direction.RIGHT,
}
while not f.is_over:
    f.print()
    t = moves[input('Your turn\n> ').strip()]
    f, x = f.get_moved(t)

    print(f.score)
    print()
f.print()


# print()
# f.move()
# f.print()
# print()
# f.move()
# f.print()
# print()
# f.move()
# f.print()
