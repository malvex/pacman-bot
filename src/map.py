screen_size = (20, 40)


def draw_map(game_state):
    map = {}

    # draw empty map first
    for x in range(screen_size[0]):
        map[x] = {}
        for y in range(screen_size[1]):
            map[x][y] = "."

    # draw entities
    entities = [] \
        + [game_state.pacman] \
        + (list(game_state.ghosts.values())) \
        + (game_state.berries or []) \
        + (game_state.buffs or [])

    for entity in entities:
        if not entity:
            continue

        x = int(entity["x"] / 50)
        y = int(entity["y"] / 50)

        entity_symbol = {
            "pacman": "P",
            "ghost-red": "R",
            "ghost-green": "G",
            "ghost-orange": "O",
            "ghost-yelow": "Y",
            "ghost-vulnerable": "X",
            "berry": "b",
            "buff": "B",
        }.get(entity["class"], "?")

        try:
            map[y][x] = entity_symbol
        except:
            pass

    # print it
    s = ""
    for x in map:
        for y in map[x]:
            s += map[x][y]
        s += "\n"

    print(s)

