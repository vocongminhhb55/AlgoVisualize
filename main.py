import turtle
import math
from queue import PriorityQueue, Queue

WIDTH = 800
PEN = turtle.Turtle()

RED = '#ff0000'
BLACK = '#000000'
GREEN = '#00ff00'
WHITE = '#ffffff'
ORANGE = '#ffa500'
GREY = '#808080'


def draw_rect(pen, color, x, y, width, height):
    pen.color(BLACK, color)
    pen.begin_fill()
    pen.pu()
    pen.goto(x, y)
    pen.pd()
    for side in range(4):
        if side % 2 == 0:
            pen.forward(width)
            pen.left(90)

        else:
            pen.forward(height)
            pen.left(90)
    pen.end_fill()


def draw_line(pen, color, x, y):
    pen.color(color)
    pen.penup()
    pen.goto(x)
    pen.pendown()
    pen.goto(y)


def find_gap(rows, cols, width):
    r_gap = width // rows
    c_gap = width // cols
    if r_gap < c_gap:
        gap = r_gap
    else:
        gap = c_gap
    return gap


def setup_window_size_and_turtle(pen, rows, cols, width):
    gap = find_gap(rows, cols, width)
    turtle.setup(cols * gap, rows * gap)
    screen = turtle.Screen()
    screen.setworldcoordinates(5, 5, cols * gap + 5, rows * gap + 5)
    turtle.title("Path Finding Algorithm Visualizer")
    pen.hideturtle()
    pen.speed(0)


def draw_grid(pen, rows, cols, width):
    gap = find_gap(rows, cols, width)
    for i in range(rows + 1):
        draw_line(pen, GREY, (0, i * gap), (cols * gap, i * gap))
    for i in range(cols + 1):
        draw_line(pen, GREY, (i * gap, 0), (i * gap, rows * gap))


class Spot:
    def __init__(self, row, col, width, total_rows, total_cols):
        self.row = row
        self.col = col
        self.x = row * width
        self.y = col * width
        self.color = WHITE
        self.neighbors = []
        self.width = width
        self.total_rows = total_rows
        self.total_cols = total_cols

    def get_coord(self):
        return self.x, self.y

    def get_pos(self):
        return self.row, self.col

    def is_barrier(self):
        return self.color == BLACK

    def is_start(self):
        return self.color == ORANGE

    def is_end(self):
        return self.color == RED

    def make_start(self):
        self.color = ORANGE

    def make_barrier(self):
        self.color = BLACK

    def make_end(self):
        self.color = RED

    def make_path(self):
        self.color = GREEN

    def draw(self, pen):
        if self.color != WHITE:
            draw_rect(pen, self.color, self.x, self.y, self.width, self.width)

    def update_neighbors(self, grid):
        self.neighbors = []

        if self.col < self.total_rows - 1 and not grid[self.row][self.col + 1].is_barrier():
            self.neighbors.append(grid[self.row][self.col + 1])

        if self.row < self.total_cols - 1 and not grid[self.row + 1][self.col].is_barrier():
            self.neighbors.append(grid[self.row + 1][self.col])

        if self.col > 0 and not grid[self.row][self.col - 1].is_barrier():
            self.neighbors.append(grid[self.row][self.col - 1])

        if self.row > 0 and not grid[self.row - 1][self.col].is_barrier():
            self.neighbors.append(grid[self.row - 1][self.col])


def make_grid(rows, cols, width):
    grid = []
    gap = find_gap(rows, cols, width)
    for i in range(cols):
        grid.append([])
        for j in range(rows):
            spot = Spot(i, j, gap, rows, cols)
            grid[i].append(spot)

    return grid


def make_grid_border(grid, rows, cols):
    for i in range(rows):
        if i == 0 or i == rows - 1:
            for j in range(cols):
                grid[j][i].make_barrier()
        else:
            grid[0][i].make_barrier()
            grid[cols - 1][i].make_barrier()

    return grid


def draw(pen, grid, rows, cols, width):
    for row in grid:
        for spot in row:
            spot.draw(pen)

    draw_grid(pen, rows, cols, width)


def bresenham_line_gen(grid, start, end):
    # roguebasin.com/index.php/Bresenham%27s_Line_Algorithm#Python
    # Setup initial conditions
    x1, y1 = start
    x2, y2 = end
    dx = x2 - x1
    dy = y2 - y1

    grid[x1][y1].make_barrier()
    grid[x2][y2].make_barrier()

    # Determine how steep the line is
    is_steep = abs(dy) > abs(dx)

    # Rotate line
    if is_steep:
        x1, y1 = y1, x1
        x2, y2 = y2, x2

    # Swap start and end points if necessary and store swap state
    swapped = False
    if x1 > x2:
        x1, x2 = x2, x1
        y1, y2 = y2, y1
        swapped = True

    # Recalculate differentials
    dx = x2 - x1
    dy = y2 - y1

    # Calculate error
    error = int(dx / 2.0)
    ystep = 1 if y1 < y2 else -1

    # Iterate over bounding box generating points between start and end
    y = y1
    points = []
    for x in range(x1, x2 + 1):
        coord = (y, x) if is_steep else (x, y)
        points.append(coord)
        error -= abs(dy)
        if error < 0:
            y += ystep
            error += dx

    # Reverse the list if the coordinates were swapped
    if swapped:
        points.reverse()
    for pixel in points:
        x, y = pixel
        grid[x][y].make_barrier()


def get_data_from_file(filename):
    with open(filename) as f:
        array = []
        for line in f:
            array.append([int(x) for x in line.split()])
        return array


def write_on_spot(pen, spot, string):
    x, y = spot.get_coord()
    pen.pu()
    pen.goto(x, y)
    pen.color(BLACK)
    pen.write(string)
    pen.pd()


def manhattan_distance(p1, p2):
    x1, y1 = p1
    x2, y2 = p2
    return abs(x1 - x2) + abs(y1 - y2)


def reconstruct_path(came_from, current):
    cost = 0
    while current in came_from:
        current = came_from[current]
        current.make_path()
        cost += 1
    return cost


def a_star_search(grid, start, end):
    count = 0
    open_set = PriorityQueue()
    open_set.put((0, count, start))
    came_from = {}
    g_score = {spot: float("inf") for row in grid for spot in row}
    g_score[start] = 0
    f_score = {spot: float("inf") for row in grid for spot in row}
    f_score[start] = manhattan_distance(start.get_pos(), end.get_pos())

    open_set_hash = {start}

    while not open_set.empty():

        current = open_set.get()[2]
        open_set_hash.remove(current)

        if current == end:
            reconstruct_path(came_from, end)
            start.make_start()
            end.make_end()
            return True, g_score[end]

        for neighbor in current.neighbors:
            temp_g_score = g_score[current] + 1

            if temp_g_score < g_score[neighbor]:
                came_from[neighbor] = current
                g_score[neighbor] = temp_g_score
                f_score[neighbor] = temp_g_score + manhattan_distance(neighbor.get_pos(), end.get_pos())
                if neighbor not in open_set_hash:
                    count += 1
                    open_set.put((f_score[neighbor], count, neighbor))
                    open_set_hash.add(neighbor)

    return False, -1


def greedy_best_first_search(grid, start, end):
    count = 0
    open_set = PriorityQueue()
    open_set.put((0, count, start))
    came_from = {}
    g_score = {spot: float("inf") for row in grid for spot in row}
    g_score[start] = 0
    f_score = {spot: float("inf") for row in grid for spot in row}
    f_score[start] = manhattan_distance(start.get_pos(), end.get_pos())

    open_set_hash = {start}

    while not open_set.empty():

        current = open_set.get()[2]
        open_set_hash.remove(current)

        if current == end:
            reconstruct_path(came_from, end)
            start.make_start()
            end.make_end()
            return True, g_score[end]

        for neighbor in current.neighbors:
            temp_g_score = g_score[current] + 1

            if temp_g_score < g_score[neighbor]:
                came_from[neighbor] = current
                g_score[neighbor] = temp_g_score
                f_score[neighbor] = manhattan_distance(neighbor.get_pos(), end.get_pos())
                if neighbor not in open_set_hash:
                    count += 1
                    open_set.put((f_score[neighbor], count, neighbor))
                    open_set_hash.add(neighbor)

    return False, -1


def uniform_cost_search(grid, start, end):
    count = 0
    open_set = PriorityQueue()
    open_set.put((0, count, start))
    came_from = {}
    g_score = {spot: float("inf") for row in grid for spot in row}
    g_score[start] = 0
    # delete f_score because in this search f(n) = g(n)

    open_set_hash = {start}

    while not open_set.empty():

        current = open_set.get()[2]
        open_set_hash.remove(current)

        if current == end:
            reconstruct_path(came_from, end)
            start.make_start()
            end.make_end()
            return True, g_score[end]

        for neighbor in current.neighbors:
            temp_g_score = g_score[current] + 1

            if temp_g_score < g_score[neighbor]:
                came_from[neighbor] = current
                g_score[neighbor] = temp_g_score
                if neighbor not in open_set_hash:
                    count += 1
                    open_set.put((g_score[neighbor], count, neighbor))
                    open_set_hash.add(neighbor)

    return False, -1


def breadth_first_search(start, end):
    # delete count variable because now this use normal queue
    open_set = Queue()
    open_set.put(start)
    came_from = {}

    open_set_hash = {start}
    visited = {start}

    while not open_set.empty():

        current = open_set.get()
        open_set_hash.remove(current)

        if current == end:
            cost = reconstruct_path(came_from, end)
            start.make_start()
            end.make_end()
            return True, cost

        for neighbor in current.neighbors:
            if neighbor not in open_set_hash and neighbor not in visited:
                came_from[neighbor] = current
                open_set.put(neighbor)
                open_set_hash.add(neighbor)
                visited.add(neighbor)

    return False, -1


def depth_limited_search(start, end, max_depth, path, visited):
    if start == end:
        return True, path

    if max_depth <= 0:
        return False, -1

    for neighbor in start.neighbors:
        if neighbor not in path and neighbor not in visited:
            path[neighbor] = start
            result = depth_limited_search(neighbor, end, max_depth - 1, path, visited)
            if result[0]:
                return True, path

    path.pop(start, None)
    visited.append(start)
    return False, -1


def iterative_deepening_search(start, end, max_depth):
    for limit in range(max_depth):
        path = {}
        visited = []
        result = depth_limited_search(start, end, limit, path, visited)
        if result[0]:
            cost = reconstruct_path(path, end)
            start.make_start()
            end.make_end()
            return result[0], cost

    return False, -1


def menu():
    menu_options = {
        1: 'Breadth-first search',
        2: 'Uniform-cost search',
        3: 'Iterative deepening search',
        4: 'Greedy-best first search',
        5: 'Graph-search A* ',
    }

    def print_menu():
        for key in menu_options.keys():
            print(key, '--', menu_options[key])

    while True:
        print_menu()
        option = ''
        try:
            option = int(input('Enter your choice: '))
        except:
            print('Wrong input. Please enter a number ...')
        # Check what choice was entered and act accordingly
        if option in range(1, 6):
            return option
        else:
            print('Invalid option. Please enter a number between 1 and 5.')


if __name__ == "__main__":
    data = get_data_from_file('input.txt')
    cols, rows = data[0]
    x_start, y_start, x_goal, y_goal = data[1]
    cols += 1
    rows += 1

    setup_window_size_and_turtle(PEN, rows, cols, WIDTH)
    grid = make_grid(rows, cols, WIDTH)
    make_grid_border(grid, rows, cols)
    grid[x_start][y_start].make_start()
    grid[x_goal][y_goal].make_end()
    for i in range(3, data[2][0] + 3):
        for j in range(int(len(data[i]) / 2)):
            point1 = data[i][j * 2], data[i][j * 2 + 1]
            if j != int(len(data[i]) / 2) - 1:
                point2 = data[i][j * 2 + 2], data[i][j * 2 + 3]
            else:
                point2 = data[i][0], data[i][1]
            bresenham_line_gen(grid, point1, point2)

    for row in grid:
        for spot in row:
            spot.update_neighbors(grid)

    user_choice = menu()
    if user_choice == 1:
        result = breadth_first_search(grid[x_start][y_start], grid[x_goal][y_goal])
    elif user_choice == 2:
        result = uniform_cost_search(grid, grid[x_start][y_start], grid[x_goal][y_goal])
    elif user_choice == 3:
        result = iterative_deepening_search(grid[x_start][y_start], grid[x_goal][y_goal], 50)
    elif user_choice == 4:
        result = greedy_best_first_search(grid, grid[x_start][y_start], grid[x_goal][y_goal])
    elif user_choice == 5:
        result = a_star_search(grid, grid[x_start][y_start], grid[x_goal][y_goal])

    draw(PEN, grid, rows, cols, WIDTH)

    write_on_spot(PEN, grid[x_start][y_start], 'Start')
    if result[0]:
        string_to_write = 'G, cost =' + str(result[1])
        write_on_spot(PEN, grid[x_goal][y_goal], string_to_write)
    else:
        write_on_spot(PEN, grid[x_goal][y_goal], 'G')

    turtle.done()
