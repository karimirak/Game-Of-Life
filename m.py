from random import random

from kivy import Config
from kivy.app import App
from kivy.graphics import Color, Rectangle
from kivy.properties import NumericProperty
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.widget import Widget

cells_alive = set()


class Main(BoxLayout):
    pass


class Cell(Widget):
    # alive = NumericProperty(0)

    def __init__(self, x, y, alive= 0,  **kwargs):
        super().__init__(**kwargs)
        self.x_grid = x
        self.y_grid = y
        self.alive = 0
        # with self.canvas.before:
        #     self.rect_colour = Color(1, 1, 1, 1)

    def on_touch_down(self, touch):
        # collide_point : Check if a point (x, y) is inside the widget’s axis aligned bounding box.
        if self.collide_point(*touch.pos):
            if self.alive == 0:
                self.live()
            else:
                self.die()

            print(cells_alive)
            print(self.x_grid, self.y_grid, " : ", self.neighbors_state())
        # return True
        # else:
        #     return super(Cell, self).on_touch_down(touch)

    # cliquer et selectionner plusieurs cellules pour les rendre vivantes
    def on_touch_move(self, touch):
        if self.collide_point(*touch.pos):
            if self.alive == 0:
                self.live()

    def update_cell_color(self):
        self.canvas.clear()
        with self.canvas:
            if self.alive == 1:
                Color(1, 0, 0)
                Rectangle(size=self.size, pos=self.pos)
            elif self.alive == 0:
                Color(1, 1, 1)
                Rectangle(size=self.size, pos=self.pos)

        # self.canvas.clear()
        # if self.alive == 1:
        #     self.rect_colour.rgb = (1, 0, 0)
        #
        # elif self.alive == 0:
        #     self.rect_colour.rgb = (1, 1, 1)

    # callback event on the age property: the cell is cleared and redesigned as a rectangle canvas,
    # updating the color according to its age
    # def on_alive(self, instance, value):
    #     self.canvas.clear()
    #     if value == 1:  # if alive = 1 : Vit
    #         with self.canvas:
    #             Color(1, 0, 0)
    #             Rectangle(size=self.size, pos=self.pos)
    #     else:
    #         with self.canvas:
    #             Color(1, 1, 1)
    #             Rectangle(size=self.size, pos=self.pos)

    def neighbors(self):
        x = self.x_grid
        y = self.y_grid
        neighbors = (
            (x - 1, y - 1), (x, y - 1), (x + 1, y - 1),
            (x - 1, y), (x + 1, y),
            (x - 1, y + 1), (x, y + 1), (x + 1, y + 1)
        )
        return neighbors

    def neighbors_state(self):
        # coordonnées des voisins de la cellule et etat alive/dead
        # retourner ( x, y, etat_cellule) : True : vivante, False : morte

        x = self.x_grid
        y = self.y_grid
        neighbors_state = []

        for elem in self.neighbors():
            neighbor_cell = Cell(elem[0], elem[1])
            is_alive = neighbor_cell.is_alive()
            neighbors_state.append((*elem, is_alive))

        return neighbors_state

    def count_alive_neighbors(self):
        cnt = 0
        neighbors = self.neighbors_state()
        for neighbor in neighbors:
            if neighbor[2] == True:
                cnt += 1
        return cnt

        # OU utiliser completion de liste
        # return sum([1 if neighbor[2] == True else 0 for neighbor in neighbors])

    def is_alive(self):
        if (self.x_grid, self.y_grid) in cells_alive:
        # if self.alive == 1:
            return True
        else:
            return False

    def die(self):
        self.alive = 0
        if ((self.x_grid, self.y_grid)) in cells_alive:
            cells_alive.remove((self.x_grid, self.y_grid))

        # print((self.x_grid, self.y_grid), ' meurt')
        self.update_cell_color()

    def live(self):
        self.alive = 1
        if (self.x_grid, self.y_grid) not in cells_alive:
            cells_alive.add((self.x_grid, self.y_grid))

        # print((self.x_grid, self.y_grid), ' live')
        self.update_cell_color()


class Grid(GridLayout):
    # number of iterations
    iterations = NumericProperty(12)

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.rows = 50
        self.cols = 40
        self.add_cells()

    def add_cells(self):
        for i in range(self.rows):
            for j in range(self.cols):
                cell = Cell(j + 1, i + 1)
                self.add_widget(cell)

    def on_text_cols_validate(self, widget):
        self.clear_widgets()
        self.cols = int(widget.text)
        self.add_cells()

    def on_text_rows_validate(self, widget):
        self.clear_widgets()
        self.rows = int(widget.text)
        self.add_cells()

    def cells_candidats(self):
        cells_candidats = {}
        for elem in cells_alive:
            cell = Cell(elem[0], elem[1])
            neighbors = cell.neighbors_state()
            for c in neighbors:
                n = Cell(c[0], c[1])
                cells_candidats[(c[0], c[1])] = n.count_alive_neighbors()
        return cells_candidats

    def next_gen(self):
        dead_cells = set()
        # print("Cellules_Actives ==> nb :", len(cells_alive), " __ Coordonnées : ", cells_alive)
        # print("list_candidates :", len(self.cells_candidats()),  self.cells_candidats())
        candidates = self.cells_candidats()
        for key in candidates:
            if key in cells_alive:
                if candidates[key] != 2 and candidates[key] != 3:
                    dead_cells.add(key)
                    # cell = Cell(key[0], key[1])
                    # cell.die()
            elif candidates[key] == 3:
                # cell = Cell(key[0], key[1])
                # cell.live()
                if key not in cells_alive:
                    cells_alive.add(key)

        self.iterations += 1
        # print('cells_active :' , cells_alive)
        # self.evolve(dead_cells)

        # print(dead_cells)
        for cell in self.children:
            # print((cell.x_grid, cell.y_grid))
            if (cell.x_grid, cell.y_grid) in cells_alive:
                cell.live()
            elif (cell.x_grid, cell.y_grid) in dead_cells:
                cell.die()

    # clear the grid
    def clear(self):
        for cell in self.children:
            cell.die()
        cells_alive.clear()
        self.iterations = 0

    # update the age of the cells according to the new generation in the world, and kill the dead cells
    def evolve(self, dead_cells):
        # print(dead_cells)
        for cell in self.children:
            # print((cell.x_grid, cell.y_grid))
            if (cell.x_grid, cell.y_grid) in cells_alive:
                cell.live()
            elif (cell.x_grid, cell.y_grid) in dead_cells:
                cell.die()
        # n = self.rows * self.cols
        # for cell in cells_alive:
        #     if (cell >= (1, 1) and cell < (self.rows - 1, self.cols -1)):
        #         # reflexing indices because kivy saves widget in the GridLayout from bottom right to top left
        #         self.children[n - 1 - (cell[0] * self.cols + cell[1])].live()
        #
        # for cell in dead_cells:
        #     if (cell >= (1, 1) and cell < (self.rows-1, self.cols-1)):
        #         self.children[n - 1 - (cell[0] * self.cols + cell[1])].die()


class GameOfLifeApp(App):
    # dimension windows fixe
    Config.set('graphics', 'width', 1000)
    Config.set('graphics', 'height', 700)
    Config.set('graphics', 'resizable', 0)


GameOfLifeApp().run()