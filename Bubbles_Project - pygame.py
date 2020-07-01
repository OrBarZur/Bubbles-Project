import random
import math
import pygame
import time
import webcolors


class Circle:
    def __init__(self, r, x, y, color, screen):
        self.r = r
        self.x = x
        self.y = y
        self.color = color
        self.screen = screen
        self.exploded = False
        self.check_floating = True
        self.to_draw = False
        self.to_explode = False
        if self.color != webcolors.name_to_rgb('white'):
            self.draw_circle(False)

    def draw_circle(self, is_white):
        if is_white:
            pygame.draw.circle(self.screen, webcolors.name_to_rgb('white'), (int(self.x), int(self.y)), self.r + 1)
        else:
            pygame.draw.circle(self.screen, self.color, (int(self.x), int(self.y)), self.r)
            pygame.draw.circle(self.screen, webcolors.name_to_rgb('black'), (int(self.x), int(self.y)), self.r, 1)
        pygame.display.flip()


class Board:
    def __init__(self, rows, cols, rows_start, r, x0, y0, interval, tries_to_down, sensitive, colors):
        self.rows = rows + 1
        self.cols = cols
        self.rows_start = rows_start
        self.r = r
        self.x0 = x0
        self.y0 = y0
        self.interval = interval
        self.sensitive = sensitive
        self.tries_to_down = tries_to_down
        self.progress = self.r / 2
        self.tries_level = tries_to_down - 1
        self.black = webcolors.name_to_rgb('black')
        self.white = webcolors.name_to_rgb('white')
        self.grey = webcolors.name_to_rgb('lightgrey')
        self.colors = [webcolors.name_to_rgb('red'), webcolors.name_to_rgb('blue'), webcolors.name_to_rgb('limegreen'),
                       webcolors.name_to_rgb('yellow'), webcolors.name_to_rgb('magenta'), webcolors.name_to_rgb('cyan'),
                       webcolors.name_to_rgb('orange'), webcolors.name_to_rgb('brown')]
        self.colors = self.colors[:colors]

        self.closest_i = None
        self.closest_j = None
        self.board = None
        self.cur_cir = None
        self.next_cir = None
        self.tries = None
        self.arrow = None
        self.exploded_3_first = False
        self.first_3_coors = []
        self.count_exploded = 0
        self.done = False

        pygame.init()
        self.screen = pygame.display.set_mode((1000, 800))
        pygame.display.set_caption("Bubbles Game")
        self.screen.fill(webcolors.name_to_rgb('white'))

    def min_x(self):
        return self.x0 - (self.interval + 1)*self.r

    def max_x(self):
        return self.x0 + (self.interval + 2)*self.r*self.cols

    def min_y(self):
        return self.y0 - (self.interval + 1)*self.r

    def max_y(self):
        return self.y0 - (self.interval + 1)*self.r + (self.interval + 2)*self.r*(self.rows - 1) + 1

    def update_arounds(self, i, j):
        return [i, i + 1, i + 1, i, i, i - 1, i - 1], [j, j + i % 2,j - 1 + i % 2, j - 1, j + 1, j + i % 2, j - 1 + i % 2]

    def borders(self):
        # draw borders of the game
        pygame.draw.line(self.screen, self.black, (int(self.min_x()), int(self.max_y())), (int(self.max_x()), int(self.max_y())))
        pygame.draw.line(self.screen, self.black, (int(self.max_x()), int(self.max_y())), (int(self.max_x()), int(self.min_y())))
        pygame.draw.line(self.screen, self.black, (int(self.max_x()), int(self.min_y())), (int(self.min_x()), int(self.min_y())))
        pygame.draw.line(self.screen, self.black, (int(self.min_x()), int(self.min_y())), (int(self.min_x()), int(self.max_y())))

    def explosion(self, i, j):
        circles_around_i, circles_around_j = self.update_arounds(i, j)

        for t in xrange(1, len(circles_around_i)):
            if 0 <= circles_around_i[t] <= self.rows - 1 and 0 <= circles_around_j[t] <= self.cols - 1:
                if (not self.board[circles_around_i[t]][circles_around_j[t]].exploded) and self.board[circles_around_i[t]][circles_around_j[t]].color == self.cur_cir.color:
                    self.count_exploded += 1
                    self.board[circles_around_i[t]][circles_around_j[t]].exploded = True
                    if len(self.first_3_coors) == 1:
                        time.sleep(0.1)
                    if not self.exploded_3_first:
                        self.first_3_coors.append([circles_around_i[t], circles_around_j[t]])

                    if not self.exploded_3_first and self.count_exploded >= 3:
                        self.exploded_3_first = True
                        for coor in self.first_3_coors:
                            self.board[coor[0]][coor[1]].color = self.white
                            self.board[coor[0]][coor[1]].draw_circle(True)
                            time.sleep(0.08)

                    if self.count_exploded > 3:
                        self.board[circles_around_i[t]][circles_around_j[t]].color = self.white
                        self.board[circles_around_i[t]][circles_around_j[t]].draw_circle(True)
                        time.sleep((self.rows*self.cols - self.count_exploded)*0.00015)

                    self.explosion(circles_around_i[t], circles_around_j[t])
                    self.board[circles_around_i[t]][circles_around_j[t]].exploded = False

        self.board[i][j].exploded = False

    def check_explosion_floating(self, i, j):
        circles_around_i, circles_around_j = self.update_arounds(i, j)

        for t in xrange(0, len(circles_around_i)):
            if 0 <= circles_around_i[t] <= self.rows - 1 and 0 <= circles_around_j[t] <= self.cols - 1:
                if self.board[circles_around_i[t]][circles_around_j[t]].check_floating and self.board[circles_around_i[t]][circles_around_j[t]].color != self.white:
                    self.board[circles_around_i[t]][circles_around_j[t]].check_floating = False
                    self.check_explosion_floating(circles_around_i[t], circles_around_j[t])

    def exploses_floating_circles(self):
        for i in xrange(0, self.rows):
            for j in xrange(0, self.cols):
                if self.board[i][j].check_floating:
                    if self.board[i][j].color != self.white:
                        self.board[i][j].color = self.white
                        self.board[i][j].draw_circle(True)
                        time.sleep(0.05)
                else:
                    self.board[i][j].check_floating = True

    def random_color(self, i):
        # random a color or put white if needed
        if i >= self.rows_start:
            return self.white
        else:
            return random.choice(self.colors)

    def release_random_color(self):
        colors_update = []
        for i in xrange(0, self.rows):
            for j in xrange(0, self.cols):
                if self.board[i][j].color != self.white and self.board[i][j].color not in colors_update:
                    colors_update.append(self.board[i][j].color)
        self.colors = colors_update

    def check_borders(self, click_x, click_y):
        if self.min_x() <= click_x <= self.max_x() and self.min_y() <= click_y <= self.max_y():
            self.turn(click_x, click_y)

    def closest_cor(self, x, y):
        dist_from_0_i = y - self.min_y()
        i_cor = dist_from_0_i / ((self.interval + 2) * self.r)
        if y <= self.min_y():
            closest_i = 0
        elif y >= self.max_y():
            closest_i = self.rows - 1
        else:
            closest_i = int(round(i_cor)) - 1
        dist_from_0_j = x - self.min_x() - (self.interval/2 + 1) * self.r * (closest_i % 2)
        j_cor = dist_from_0_j / ((self.interval + 2) * self.r)
        if x <= self.min_x():
            closest_j = 0
        elif x >= self.max_x():
            closest_j = self.cols - 1
        else:
            closest_j = int(round(j_cor)) - 1
        if self.board[closest_i][closest_j].color != self.white:
            self.board[closest_i][closest_j].draw_circle(False)
        return closest_i, closest_j

    def closest_white_circle(self, i, j):
        circles_around_i, circles_around_j = self.update_arounds(i, j)
        first_white = True
        min_dist_t = 0
        for t in xrange(1, len(circles_around_i)):
            if 0 <= circles_around_i[t] <= self.rows - 1 and 0 <= circles_around_j[t] <= self.cols - 1:
                if self.board[i][j].color != self.white:
                    self.board[i][j].draw_circle(False)
                is_white = self.board[circles_around_i[t]][circles_around_j[t]].color == self.white
                if first_white:
                    if is_white:
                        first_white = False
                        min_dist_t = t
                else:
                    if is_white and self.dist(self.board[circles_around_i[t]][circles_around_j[t]]) < self.dist(self.board[circles_around_i[min_dist_t]][circles_around_j[min_dist_t]]):
                        min_dist_t = t
        return circles_around_i[min_dist_t], circles_around_j[min_dist_t]

    def dist(self, circle):
        return math.sqrt((self.cur_cir.x - circle.x)**2 + (self.cur_cir.y - circle.y)**2)

    def change_degrees(self, degrees):
        if self.cur_cir.x <= self.min_x() + self.r*(1 - math.cos(degrees)) or self.cur_cir.x >= self.max_x() + self.r*(-1 - math.cos(degrees)):
            return math.pi - degrees
        else:
            return degrees

    def print_board(self):
        for i in xrange(0, self.rows):
            for j in xrange(0, self.cols):
                print self.board[i][j].exploded,
            print "\n"
        print self.count_exploded

    def check_keep_moving(self, closest_i, closest_j, degrees):
        circles_around_i, circles_around_j = self.update_arounds(closest_i, closest_j)
        keep_moving = True

        for t in xrange(0, len(circles_around_i)):
            if 0 <= circles_around_i[t] <= self.rows - 1 and 0 <= circles_around_j[t] <= self.cols - 1:
                i = circles_around_i[t]
                j = circles_around_j[t]
                if self.dist(self.board[i][j]) <= 2 * self.r and self.board[i][j].color != self.white:
                    self.board[i][j].to_draw = True
                if self.dist(self.board[i][j]) <= self.r*(1 + self.sensitive) and self.board[i][j].color != self.white or self.cur_cir.y <= self.min_y() + self.r + math.sin(degrees) * self.progress:
                    keep_moving = False
                    break

        return keep_moving

    def out_of_tries(self):
        for i in xrange(self.rows - 2, -1, -1):
            for j in xrange(0, self.cols):
                if self.board[i][j].color != self.white:
                    self.board[i + 1][j].color = self.board[i][j].color
                    self.board[i + 1][j].draw_circle(False)

        for j in xrange(0, self.cols):
            self.board[0][j] = Circle(self.r, self.x0 + (self.interval + 2)*j*self.r, self.y0, self.random_color(0), self.screen)

    def draw_to_draw(self):
        for i in xrange(0, self.rows):
            for j in xrange(0, self.cols):
                if self.board[i][j].color != self.white and self.board[i][j].to_draw:
                    self.board[i][j].to_draw = False
                    self.board[i][j].draw_circle(False)

    def draw_around_circles(self, i, j):
        circles_around_i, circles_around_j = self.update_arounds(i, j)
        for t in xrange(0, len(circles_around_i)):
            if 0 <= circles_around_i[t] <= self.rows - 1 and 0 <= circles_around_j[t] <= self.cols - 1:
                if self.board[circles_around_i[t]][circles_around_j[t]].color != self.white:
                    self.board[circles_around_i[t]][circles_around_j[t]].draw_circle(False)

    def one_col_down(self):
        if not self.exploded_3_first:
            if len(self.tries) > 0:
                self.tries[-1].draw_circle(True)
                self.tries.pop(-1)
            else:
                self.out_of_tries()
                if self.tries_level == 0:
                    self.tries_level = self.tries_to_down - 1
                else:
                    self.tries_level -= 1
                self.tries = [Circle(self.r, self.x0 + (2 * self.interval + 2) * (i + 1) * self.r, self.cur_cir.y, self.grey, self.screen) for i in range(self.tries_level)]

    def mov_circle(self, click_x, click_y):
        # move the current ball in the direction of the user's point and stop when it touches another ball
        degrees = math.atan2(click_y - self.cur_cir.y, click_x - self.cur_cir.x)

        closest_i, closest_j = self.closest_cor(self.cur_cir.x, self.cur_cir.y)
        while self.check_keep_moving(closest_i, closest_j, degrees):
            degrees = self.change_degrees(degrees)
            self.cur_cir.draw_circle(True)
            self.cur_cir.x += math.cos(degrees) * self.progress
            self.cur_cir.y += math.sin(degrees) * self.progress
            self.cur_cir.draw_circle(False)
            closest_i, closest_j = self.closest_cor(self.cur_cir.x, self.cur_cir.y)
            self.borders()
            time.sleep(0.003)

        self.cur_cir.draw_circle(True)
        closest_i, closest_j = self.closest_white_circle(closest_i, closest_j)
        self.draw_around_circles(closest_i, closest_j)
        self.board[closest_i][closest_j].color = self.cur_cir.color
        self.board[closest_i][closest_j].draw_circle(False)
        return closest_i, closest_j

    def check_win(self):
        win = self.colors == []
        if win:
            win_image = pygame.transform.scale(pygame.image.load('win.png'), (500, 500))
            self.screen.blit(win_image, (self.cur_cir.x - 0.5 * win_image.get_width(), 100))
            pygame.display.flip()
            self.done = True
            pygame.event.wait()

    def check_lose(self):
        lose = False
        for j in xrange(0, self.cols):
            if self.board[self.rows - 1][j].color != self.white:
                lose = True
        if lose:
            lose_image = pygame.transform.scale(pygame.image.load('lose.png'), (500, 500))
            self.screen.blit(lose_image, (self.cur_cir.x - 0.5 * lose_image.get_width(), 100))
            pygame.display.flip()
            self.done = True
            pygame.event.wait()

    def turn(self, click_x, click_y):
        cur_cir_i, cur_cir_j = self.mov_circle(click_x, click_y)
        self.draw_to_draw()
        self.borders()

        self.count_exploded = 1
        self.exploded_3_first = False
        self.board[cur_cir_i][cur_cir_j].exploded = True
        self.first_3_coors = [[cur_cir_i, cur_cir_j]]
        self.explosion(cur_cir_i, cur_cir_j)

        for j in xrange(0, self.cols):
            if self.board[0][j].color != self.white:
                self.check_explosion_floating(0, j)
        self.exploses_floating_circles()
        self.borders()

        self.cur_cir.x = (2*self.x0 + (self.interval + 2)*self.r*self.cols - (self.interval/2 + 1)*self.r)/2
        self.cur_cir.y = self.y0 + (self.interval + 2)*self.rows*self.r
        self.cur_cir.color = self.next_cir.color
        self.release_random_color()
        self.check_win()
        self.check_lose()
        if len(self.colors) == 0:
            return
        self.next_cir.color = random.choice(self.colors)
        self.cur_cir.draw_circle(False)
        self.next_cir.draw_circle(False)
        self.one_col_down()
        self.check_lose()

    def game(self):
        # last_deg = math.pi / 2
        while not self.done:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    self.done = True
                    global end
                    end = True
                    """
                elif event.type == pygame.MOUSEMOTION:
                    new_deg = math.atan2(pygame.mouse.get_pos()[1] - self.cur_cir.y, pygame.mouse.get_pos()[0] - self.cur_cir.x)
                    self.arrow = pygame.transform.rotate(self.arrow, math.degrees(new_deg - last_deg))
                    last_deg = new_deg
                    pygame.display.flip()
                    """
                elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                    self.check_borders(pygame.mouse.get_pos()[0], pygame.mouse.get_pos()[1])
        while not end:
            for event in pygame.event.get():
                if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                    return

    def start_game(self):
        r = self.r
        self.borders()
        self.board = [[Circle(r, self.x0 + (self.interval + 2)*j*r + (self.interval/2 + 1)*r*(i % 2), self.y0 + (self.interval + 2)*i*r, self.random_color(i), self.screen) for j in range(self.cols)] for i in range(self.rows)]
        self.cur_cir = Circle(r, (2*self.x0 + (self.interval + 2)*self.r*self.cols - (self.interval/2 + 1)*self.r)/2, self.y0 + (self.interval + 2)*self.rows*r, random.choice(self.colors), self.screen)
        self.next_cir = Circle(r, self.x0, self.cur_cir.y, random.choice(self.colors), self.screen)
        self.tries = [Circle(r, self.x0 + (2*self.interval + 2)*(i+1)*r, self.cur_cir.y, self.grey, self.screen) for i in range(self.tries_to_down - 1)]
        """
        self.arrow = pygame.transform.rotate(pygame.transform.scale(pygame.image.load('arrow.png'), (60, 120)), 180)
        self.screen.blit(self.arrow, (self.cur_cir.x - 0.5 * self.arrow.get_width(), self.cur_cir.y - self.arrow.get_height()))
        pygame.display.flip()
        """
        self.game()


end = False
b_rows, b_cols, b_rows_start, b_r, b_x0, b_y0, b_interval, b_tries_to_down, b_sensitive, b_colors = 17, 17, 9, 16, 250, 50, 0.2, 6, 0.6, 5
b = Board(b_rows, b_cols, b_rows_start, b_r, b_x0, b_y0, b_interval, b_tries_to_down, b_sensitive, b_colors)
while not end:
    b = Board(b_rows, b_cols, b_rows_start, b_r, b_x0, b_y0, b_interval, b_tries_to_down, b_sensitive, b_colors)
    b.start_game()
