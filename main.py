import threading
import time

import pygame as pg
import numpy as np

pg.init()
pg.font.init()


COLOURS = {
    "ALIVE": (255, 255, 255),
    "DEAD": (10, 10, 10),
    "GRID": (40, 40, 40),
}

WIN_SIZE = (900, 675)
CELL_SIZE = 15
CELL_SIZE_DRAW = CELL_SIZE - 1
NUM_CELLS = (WIN_SIZE[1] // CELL_SIZE, WIN_SIZE[0] // CELL_SIZE)

FONT = pg.font.SysFont("poppins", 14)

class Simulation:
    def __init__(self):
        self.win = pg.display.set_mode(WIN_SIZE)
        pg.display.set_caption("Conway's Game of Life")
        self.main_clock = pg.time.Clock()
        self.simulation_clock = pg.time.Clock()

        self.FRAMERATE = 120
        self.tickrate = 10    

        self.grid = True


    def _reset_simluation(self):
        self.simulation_running = False
        
        time.sleep(0.1)
        self.cells = np.zeros(NUM_CELLS)
        
        # Create Starter Glider
        row, col = NUM_CELLS[0] // 2, NUM_CELLS[1] // 2 - 1
        self.cells[row, col] = 1
        self.cells[row, col+1] = 1
        self.cells[row, col+2] = 1
        self.cells[row-1, col+2] = 1
        self.cells[row-2, col+1] = 1

        self.generation = 0


    def _draw_win(self):
        # Draw grid
        if self.grid:
            self.win.fill(COLOURS["GRID"])
        else:
            self.win.fill(COLOURS["DEAD"])

        # Draw dead cells
        dead_cells = np.argwhere(self.cells == 0)
        for row, col in dead_cells:
            pg.draw.rect(self.win, COLOURS["DEAD"], (col * CELL_SIZE, row * CELL_SIZE, CELL_SIZE_DRAW, CELL_SIZE_DRAW))

        # Draw alive cells
        alive_cells = np.argwhere(self.cells == 1)
        for row, col in alive_cells:
            pg.draw.rect(self.win, COLOURS["ALIVE"], (col * CELL_SIZE, row * CELL_SIZE, CELL_SIZE_DRAW, CELL_SIZE_DRAW))

        # Draw debug text
        debug_texts = (
            f"Framerate: {self._get_framerate()}",
            f"Tickrate: {self.tickrate}",
            f"Population: {self._get_population()}",
            f"Generation: {self.generation}"
        )

        for i, text in enumerate(debug_texts):
            draw_text = FONT.render(text, 1, COLOURS["ALIVE"])
            self.win.blit(draw_text, (20, i*20+20))

        pg.display.flip()


    def _update_cells(self):
        updated_cells = np.zeros((self.cells.shape[0], self.cells.shape[1]))

        for row, col in np.ndindex(self.cells.shape):
            alive = np.sum(self.cells[row-1:row+2, col-1:col+2]) - self.cells[row, col]

            if self.cells[row, col] == 1:
                if alive < 2 or alive > 3:
                    updated_cells[row, col] = 0
                else:
                    updated_cells[row, col] = 1
            else:
                if alive == 3:
                    updated_cells[row, col] = 1

        self.cells = updated_cells


    def _handle_input(self):
        for e in pg.event.get():
            if e.type == pg.QUIT:
                quit()
            
            if e.type == pg.KEYDOWN:
                if e.key == pg.K_SPACE:
                    self.simulation_running = not self.simulation_running
        
                elif e.key == pg.K_r:
                    self._reset_simluation()

                elif e.key == pg.K_g:
                    self.grid = not self.grid

                elif e.key == pg.K_UP and self.tickrate < 20:
                    self.tickrate += 1
                elif e.key == pg.K_DOWN and self.tickrate > 1:
                    self.tickrate -= 1
    
            mouse_presses = pg.mouse.get_pressed()
            if mouse_presses:
                x, y = pg.mouse.get_pos()
                row, col = y // CELL_SIZE, x // CELL_SIZE

                try:
                    if mouse_presses[0]:          
                        self.cells[row, col] = 1
                    if mouse_presses[2]:
                        self.cells[row, col] = 0
                except IndexError:
                    pass

    def _get_framerate(self):
        return int(self.main_clock.get_fps())

    def _get_population(self):
        return np.count_nonzero(self.cells == 1)

    def main(self):
        self._reset_simluation()
        self.win.fill(COLOURS["GRID"])

        threading.Thread(target=self._simulation_thread, daemon=True).start()

        while True:
            self.main_clock.tick(self.FRAMERATE)    
            self._handle_input()
            self._draw_win()


    def _simulation_thread(self):
        while True:
            self.simulation_clock.tick(self.tickrate)

            if self.simulation_running:
                self._update_cells()
                self.generation += 1
                

if __name__ == "__main__":
    game = Simulation()
    game.main()