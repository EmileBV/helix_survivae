from random import random, randint


class Enemy:

    def __init__(self, enemy_type: int):
        self.enemy_type = enemy_type
        self.x_amount = round(random() * 5)
        self.y_amount = round(random() * 5)
        self.x_counter = 0
        self.y_counter = 0
        self.x_dir = [-1, 1][randint(0, 1)]
        self.y_dir = [-1, 1][randint(0, 1)]

    def __int__(self):
        return self.enemy_type

    def moving_x(self):
        if self.x_counter > self.x_amount:
            self.x_counter = 0
            return True
        else:
            self.x_counter += 1
            return False

    def moving_y(self):
        if self.y_counter > self.y_amount:
            self.y_counter = 0
            return True
        else:
            self.y_counter += 1
            return False

    def get_x_dir(self):
        return self.x_dir

    def get_y_dir(self):
        return self.y_dir

    def flip_x(self):
        self.x_dir = - self.x_dir

    def flip_y(self):
        self.y_dir = - self.y_dir
