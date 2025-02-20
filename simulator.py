width, height = 11, 11
objects = {
    0: "\U00002b1b", # "⠀⠀",
    1: "<a:player:891186455592992768>",
    2: "\U00002b1c",
    3: "\U0001f7e9",
}

blocks = [2]

class Map:
    def __init__(self):
        self.x = None
        self.y = None
        self.width = width
        self.height = height
        self.grid = []
        self.content = None

    async def setup(self):
        for x in range(self.width):
            self.grid.append([2 for x in range(self.height)])

        self.x = 1 # width // 2
        self.y = 1 # height // 2
        # self.grid[-self.y-1][self.x] = self.name
        return self

    def update(self):
        while self.x <= -1:
            self.x += self.width
        while self.x >= self.width:
            self.x -= self.width
        while self.y >= self.height:
            self.y -= self.height
        while self.y <= -1:
            self.y += self.height
        self.grid[-self.y-1][self.x] = self.name

    def display(self):
        print("\n".join([" ".join([str(_) for _ in self.grid[int(_)]]) for _ in [_ for _ in range(len(self.grid))]]))

        print(" ".join(["-" for _ in range(len(self.grid))]))

    def convert(self):
        self.content = "\n".join(["".join([objects[int(_)] for _ in self.grid[int(_)]]) for _ in [_ for _ in range(len(self.grid))]])
        self.coordinates = self.x, self.y
        return self

    def set(self, x, y, name):
        self.grid[-y-1][x] = name
        return self

    def fill(self, x1, y1, x2, y2, name):
        x, y = x1, y1
        for j in range(y2-y1+1):
            for i in range(x2-x1+1):
                self.set(x, y, name)
                x += 1
            y += 1
            x = x1
        return self

    def get(self, x, y):
        return self.grid[-y-1][x]

class User(Map):
    def __init__(self, name):
        super().__init__()
        self.name = str(name)
        self.content = None
        self.coordinates = None
        self.lastobject = 0

    def teleport(self, x, y):
        self.grid[-self.y-1][self.x] = 0
        self.x = x
        self.y = y
        self.update()

    def coordinates(self):
        return (self.x, self.y)

    def left(self):
        try:
            if not self.x == 0:
                if self.grid[-self.y-1][self.x-1] in blocks:
                    return
                self.grid[-self.y-1][self.x] = self.lastobject
                # self.lastobject = self.grid[-self.y-1][self.x-1]
                self.x -= 1
        except:
            pass
        self.update()
    
    def right(self):
        try:
            if not self.x == self.width-1:
                if self.grid[-self.y-1][self.x+1] in blocks:
                    return
                self.grid[-self.y-1][self.x] = self.lastobject
                # self.lastobject = self.grid[-self.y-1][self.x+1]
                self.x += 1
        except:
            pass
        self.update()

    def down(self):
        try:
            if not self.y == 0:
                if self.grid[-self.y][self.x] in blocks:
                    return
                self.grid[-self.y-1][self.x] = self.lastobject
                # self.lastobject = self.grid[-self.y][self.x]
                self.y -= 1
        except:
            pass
        self.update()

    def up(self):
        try:
            if not self.y == self.height-1:
                if self.grid[-self.y-2][self.x] in blocks:
                    return
                self.grid[-self.y-1][self.x] = self.lastobject
                # self.lastobject = self.grid[-self.y-2][self.x]
                self.y += 1
        except:
            pass
        self.update()