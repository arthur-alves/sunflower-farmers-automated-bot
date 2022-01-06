"""Logger."""
COLORS = {
    'green': "\033[1;32;49m %s",
    'red': "\033[1;31;49m %s",
    'white': "\033[1;37;49m %s",
    'yellow': "\033[1;33;49m %s",
}


def log(word, color='green'):
    print(COLORS[color] % ('%s ' % word))
