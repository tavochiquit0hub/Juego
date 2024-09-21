import tkinter as tk
import random
import math

class AsteroidDodgeGame:
    def __init__(self, root):
        self.root = root
        self.canvas = tk.Canvas(root, width=600, height=400, bg="black")
        self.canvas.pack()

        self.start_screen()

    def start_screen(self):
        self.canvas.delete("all")
        self.canvas.create_text(300, 100, text="Asteroid Dodge Game", fill="white", font=("Arial", 24))

        play_button = tk.Button(self.root, text="Jugar", command=self.start_game, bg="black", fg="white", width=20, height=2, borderwidth=2, relief="solid", highlightbackground="black")
        play_button_window = self.canvas.create_window(300, 200, window=play_button)

        instructions_button = tk.Button(self.root, text="Instrucciones", command=self.show_instructions, bg="black", fg="white", width=20, height=2, borderwidth=2, relief="solid", highlightbackground="black")
        instructions_button_window = self.canvas.create_window(300, 250, window=instructions_button)

        exit_button = tk.Button(self.root, text="Salir", command=self.root.quit, bg="black", fg="white", width=20, height=2, borderwidth=2, relief="solid", highlightbackground="black")
        exit_button_window = self.canvas.create_window(300, 300, window=exit_button)

    def show_instructions(self):
        self.canvas.delete("all")
        self.canvas.create_text(300, 50, text="Instrucciones:", fill="white", font=("Arial", 24))
        self.canvas.create_text(300, 100, text="Evita los asteroides usando las flechas.", fill="white", font=("Arial", 16))
        self.canvas.create_text(300, 150, text="Pierdes una vida si chocas con un asteroide.", fill="white", font=("Arial", 16))
        back_button = tk.Button(self.root, text="Volver", command=self.start_screen, bg="black", fg="white", width=20, height=2, borderwidth=2, relief="solid", highlightbackground="black")
        back_button_window = self.canvas.create_window(300, 250, window=back_button)

    def start_game(self):
        self.canvas.delete("all")
        self.ship = self.create_galaga_ship(300, 200)
        self.asteroids = []
        self.score = 0
        self.level = 1
        self.progress = 0
        self.lives = 1  # Comenzamos con 1 vida
        self.lives_indicators = []
        self.progress_bar = self.canvas.create_rectangle(50, 350, 50, 360, fill="green")
        self.game_over = False

        self.canvas.bind_all("<KeyPress-Left>", self.move_left)
        self.canvas.bind_all("<KeyPress-Right>", self.move_right)
        self.canvas.bind_all("<KeyPress-Up>", self.move_up)
        self.canvas.bind_all("<KeyPress-Down>", self.move_down)

        self.spawn_asteroid()
        self.update_game()
        self.start_progress_timer()

    def create_galaga_ship(self, x, y):
        ship_shape = [
            x, y - 10,
            x - 8, y,
            x - 12, y + 5,
            x - 8, y + 10,
            x + 8, y + 10,
            x + 12, y + 5,
            x + 8, y
        ]
        return self.canvas.create_polygon(ship_shape, fill="blue", outline="white")

    def move_left(self, event):
        if not self.game_over:
            self.canvas.move(self.ship, -15, 0)

    def move_right(self, event):
        if not self.game_over:
            self.canvas.move(self.ship, 15, 0)

    def move_up(self, event):
        if not self.game_over:
            self.canvas.move(self.ship, 0, -15)

    def move_down(self, event):
        if not self.game_over:
            self.canvas.move(self.ship, 0, 15)

    def spawn_asteroid(self):
        if not self.game_over:
            edge = random.choice(["top", "bottom", "left", "right"])
            x, y = 0, 0

            if edge == "top":
                x = random.randint(0, 570)
                y = 0
            elif edge == "bottom":
                x = random.randint(0, 570)
                y = 400
            elif edge == "left":
                x = 0
                y = random.randint(0, 370)
            else:
                x = 600
                y = random.randint(0, 370)

            asteroid = self.canvas.create_oval(x, y, x + 30, y + 30, fill="gray")
            direction = self.calculate_direction(x, y)
            self.asteroids.append((asteroid, direction))
            self.root.after(1000, self.spawn_asteroid)

    def calculate_direction(self, x, y):
        ship_coords = self.canvas.coords(self.ship)
        if ship_coords and len(ship_coords) >= 6:
            ship_x = (ship_coords[0] + ship_coords[4]) / 2
            ship_y = (ship_coords[1] + ship_coords[5]) / 2

            dx = ship_x - x
            dy = ship_y - y
            distance = math.sqrt(dx ** 2 + dy ** 2)

            if distance != 0:
                return (dx / distance, dy / distance)
        return (0, 0)

    def update_game(self):
        if not self.game_over:
            self.move_asteroids()
            self.check_collisions()
            self.canvas.delete("score")
            self.canvas.create_text(500, 30, text=f"Puntaje: {self.score}", fill="white", font=("Arial", 16), tag="score")
            self.update_lives_display()
            self.root.after(50, self.update_game)

    def move_asteroids(self):
        to_remove = []
        for asteroid, direction in self.asteroids:
            self.canvas.move(asteroid, direction[0] * 5, direction[1] * 5)
            coords = self.canvas.coords(asteroid)
            if coords and (coords[1] > 400 or coords[3] < 0 or coords[0] > 600 or coords[2] < 0):
                to_remove.append(asteroid)
                self.score += 1

        for asteroid in to_remove:
            for ast, dir in self.asteroids:
                if ast == asteroid:
                    self.asteroids.remove((ast, dir))
                    self.canvas.delete(ast)

    def check_collisions(self):
        ship_coords = self.canvas.coords(self.ship)
        if ship_coords:
            for asteroid, _ in self.asteroids:
                coords = self.canvas.coords(asteroid)
                if coords and self.overlap(ship_coords, coords):
                    if self.lives > 1:
                        self.lives -= 1
                        if self.lives_indicators:
                            last_indicator = self.lives_indicators.pop()
                            self.canvas.delete(last_indicator)
                    else:
                        self.end_game()
                    self.revive()
                    return

    def revive(self):
        self.canvas.delete(self.ship)
        self.ship = self.create_galaga_ship(300, 200)

        for asteroid, _ in self.asteroids:
            self.canvas.delete(asteroid)
        self.asteroids.clear()

    def overlap(self, coords1, coords2):
        return (coords1[2] > coords2[0] and coords1[0] < coords2[2] and
                coords1[3] > coords2[1] and coords1[1] < coords2[3])

    def start_progress_timer(self):
        self.progress = 0
        self.update_progress()

    def update_progress(self):
        if not self.game_over:
            self.progress += 1
            if self.progress >= 15:
                self.level_up()
            else:
                self.canvas.coords(self.progress_bar, 50, 350, 50 + (self.progress / 15 * 500), 360)
                self.root.after(1000, self.update_progress)

    def level_up(self):
        self.progress = 0
        self.level += 1
        self.lives += 1
        self.canvas.coords(self.progress_bar, 50, 350, 50, 360)
        self.start_progress_timer()

    def update_lives_display(self):
        self.canvas.delete("lives_indicator")
        self.lives_indicators.clear()

        for i in range(self.lives):
            x_pos = 50 + i * 30
            indicator = self.create_galaga_ship(x_pos, 370)
            self.lives_indicators.append(indicator)

    def end_game(self):
        self.game_over = True
        self.canvas.create_text(300, 200, text="Game Over", fill="red", font=("Arial", 30))
        self.canvas.create_text(300, 250, text=f"Puntaje final: {self.score}", fill="white", font=("Arial", 16))

root = tk.Tk()
game = AsteroidDodgeGame(root)
root.mainloop()
