import json
import random

from kivy import Config
from kivy.app import App
from kivy.graphics import Color, Rectangle
from kivy.properties import NumericProperty, Clock, StringProperty
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.popup import Popup
from kivy.uix.widget import Widget

cells_alive = set()

class Main(BoxLayout):
    pass

class Cell(Widget):
    alive = NumericProperty(0)

    def __init__(self, x, y, **kwargs):
        super().__init__(**kwargs)
        self.x_grid = x
        self.y_grid = y

        # with self.canvas.before:
        #     self.rect_colour = Color(1, 1, 1, 1)

    def on_touch_down(self, touch):
        # collide_point : Check if a point (x, y) is inside the widget’s axis aligned bounding box.
        if self.collide_point(*touch.pos):
            if self.alive == 0:
                self.live()
            else:
                self.die()
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
    iterations = NumericProperty(0)
    fps = 1
    is_running = True

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.rows = 30
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

    def neighbors(self, elem):
        x = elem[0]
        y = elem[1]
        neighbors = (
            (x - 1, y - 1), (x, y - 1), (x + 1, y - 1),
            (x - 1, y), (x + 1, y),
            (x - 1, y + 1), (x, y + 1), (x + 1, y + 1)
        )
        return neighbors

    def neighbors_state(self, elem):
        # coordonnées des voisins de la cellule et etat alive/dead
        # retourner ( x, y, etat_cellule) : True : vivante, False : morte

        neighbors_state = []
        for cell in self.neighbors(elem):
            is_alive = cell in cells_alive
            neighbors_state.append((*elem, is_alive))
        return neighbors_state

    def get_cnt_alive_neighbors(self, elem):
        cnt = 0
        neighbors = self.neighbors_state(elem)
        for neighbor in neighbors:
            if neighbor[2] == True:
                cnt += 1
        return cnt

        # OU utiliser completion de liste
        # return sum([1 if neighbor[2] == True else 0 for neighbor in neighbors])

    def cells_candidats(self):
        # liste des candidats pour la nouvelle génération, y compris les cellules vivantes
        list_candidats = set()
        for elem in cells_alive:
            list_candidats.add(elem)
            neighbors = self.neighbors(elem)
            for cell in neighbors:
                list_candidats.add(cell)

        # enlever les cells en dehors de la grille
        for cell in list_candidats.copy():  # on boucle sur une copie sinon err : RuntimeError:Set changed size during iteration
            if not ((1 <= cell[0] <= self.cols) and (1 <= cell[1] <= self.rows)):
                list_candidats.remove(cell)

        # get cnt_alive_neighbors :
        cells_candidats_nb = {}
        for cell in list_candidats:
            cells_candidats_nb[cell] = self.get_cnt_alive_neighbors(cell)

        return cells_candidats_nb

    def next_gen(self, dt):
        cells_dead = set()
        cells_born = set()
        # print("Cellules_Actives ==> nb :", len(cells_alive), " __ Coordonnées : ", cells_alive)
        # print("list_candidates :", len(self.cells_candidats()), self.cells_candidats())

        candidates = self.cells_candidats()

        for cell in candidates:
            if cell not in cells_alive and candidates[cell] == 3:
                cells_born.add(cell)
            elif cell in cells_alive:
                if candidates[cell] != 2 and candidates[cell] != 3:
                    cells_dead.add(cell)

        self.iterations += 1
        self.evolve(cells_born, cells_dead)

    def evolve(self, cells_born, cells_dead):
        # todo : coordonnée to self.children pour eviter de boucler dur tous les self.children
        n = self.rows * self.cols
        # print(self.children[n - self.cols * self.rows])
        # for cell in cells_born:
        # for cell in cells_dead:

        for cell in self.children:
            if (cell.x_grid, cell.y_grid) in cells_born:
                cell.live()
            elif (cell.x_grid, cell.y_grid) in cells_dead:
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

    # clear the grid
    def clear(self):
        for cell in self.children:
            cell.die()
        cells_alive.clear()

        self.iterations = 0
        self.parent.ids.Toggle_Play_Pause.state = "normal"

    def on_toggle_state(self, play_pause_btn):
        if play_pause_btn.state == 'normal':
            play_pause_btn.text = "Play"
            # self.parent.ids.cols.disabled = False
            # self.parent.ids.rows.disabled = False
            self.control_pause()
        else:
            play_pause_btn.text = "Pause"
            # self.parent.ids.cols.disabled = True
            # self.parent.ids.rows.disabled = True
            self.control_play()

    def control_play(self):
        self.is_running = True
        Clock.schedule_interval(self.next_gen, 1/self.fps)
        if len(cells_alive) == 0:
            Clock.unschedule(self.next_gen)
            self.iterations = 0

    def control_pause(self):
        self.is_running = False
        Clock.unschedule(self.next_gen)

    def change_fps(self, fps_slider):
        self.fps = fps_slider.value
        if self.is_running:
            self.control_pause()
            self.control_play()

    def random_cells(self):
        self.clear()
        nb_cells = random.randint(1, self.cols*self.rows)
        for i in range(nb_cells):
            cells_alive.add((random.randint(1,self.cols),random.randint(1,self.rows)))
        for cell in self.children:
            if (cell.x_grid, cell.y_grid) in cells_alive:
                cell.live()

    def import_cells(self, cells):
        self.clear()
        for cell in self.children:
            if [cell.x_grid, cell.y_grid] in cells:
                cell.live()


class OpenDialog(Popup):
       filename = StringProperty()

       def __init__(self, type, grid):
        super(OpenDialog, self).__init__()
        self.type = type
        self.grid = grid

       def _enter(self):
           if self.filename:
            if self.type == 'save':
                self.export_file()
            elif self.type == 'load':
                self.import_file()
            self.dismiss()

       def export_file(self):

           # self.title = 'Export de la configuration en fichier en Json'
           cells_alive_json = json.dumps(list(cells_alive))
           f = open(self.filename + ".json", "w")
           f.write(cells_alive_json)
           f.close()

       def import_file(self):
        print("title :" , self.title)
        # self.title = "Import d'une configuration en fichier Json"
        try:
            with open(self.filename + ".json", "r") as file:
                cells_json = file.read()
                cells = json.loads(cells_json)
                Grid.import_cells(self.grid, cells)
        except:
            Grid.clear(self.grid)

class GameOfLifeApp(App):
    # dimension windows fixe
    Config.set('graphics', 'width', 1000)
    Config.set('graphics', 'height', 700)
    Config.set('graphics', 'resizable', 0)



GameOfLifeApp().run()
