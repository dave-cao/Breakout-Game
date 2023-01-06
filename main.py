import random

import pygame


def main():
    # initialize game
    pygame.init()

    WIDTH, HEIGHT = 800, 600
    pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("Breakout")
    w_surface = pygame.display.get_surface()

    game = Game(w_surface)

    game.play()

    pygame.quit()


class Game:
    def __init__(self, surface):
        self.surface = surface
        self.bg_color = pygame.Color("black")

        self.FPS = 60
        self.game_Clock = pygame.time.Clock()
        self.close_clicked = False
        self.continue_game = False

        # Deal with PADDLE CLASS
        self.paddle_height = 10
        self.paddle_width = 70

        self.paddle_y = self.surface.get_height() - 50

        # middle of screen width x
        self.paddle_x = self.surface.get_width() // 2 - self.paddle_width // 2
        self.paddle = Paddle(
            self.paddle_x,
            self.paddle_y,
            self.paddle_width,
            self.paddle_height,
            "white",
            self.surface,
        )

        # Create a ball
        self.middle_screen_x = self.surface.get_width() // 2
        self.middle_screen_y = self.surface.get_height() // 2
        self.ball = Ball(
            "red", 5, [self.middle_screen_x, self.middle_screen_y], [0, 4], self.surface
        )
        self.ball.randomize_x_velocity()

        # create bricks
        self.bricks = []
        self.create_bricks()
        self.brick_length = len(self.bricks)
        self.bricks_to_break_speedup = self.brick_length // 5

    def create_bricks(self):
        # create the bricks
        x = 0
        y = 200
        brick_colors = ["blue", "green", "yellow", "orange", "red"]

        for color in brick_colors:
            while x <= self.surface.get_width():
                self.bricks.append(
                    Brick(x, y, random.randint(40, 60), 30, color, self.surface)
                )
                x += 53

            x = 0
            y -= 35

    def play(self):
        while not self.close_clicked:
            self.handle_events()
            self.draw()
            if self.continue_game:
                self.update()

            self.game_Clock.tick(self.FPS)  # run at most with FPS

    def handle_events(self):
        # Handles every event of the game
        events = pygame.event.get()
        for event in events:
            if event.type == pygame.QUIT:
                self.close_clicked = True

            if not self.continue_game:
                if event.type == pygame.MOUSEBUTTONUP:
                    self.continue_game = True
                    self.restart_game()

    def restart_game(self):
        # restart bricks
        self.bricks = []
        self.create_bricks()
        self.brick_length = len(self.bricks)
        self.bricks_to_break_speedup = self.brick_length // 5

        # restart ball
        self.ball.set_pos(self.middle_screen_x, self.middle_screen_y)
        self.ball.set_velocity(0, 4)
        self.ball.randomize_x_velocity()

    def update(self):
        # update the game state

        # Move the paddle with player mouse
        mouse_pos_x = pygame.mouse.get_pos()[0]
        middle_of_mouse_x = mouse_pos_x - self.paddle.get_width() // 2
        if middle_of_mouse_x > self.paddle.get_pos()[0]:
            self.paddle.set_horizontal_velocity(10)
            self.paddle.move()
        if middle_of_mouse_x < self.paddle.get_pos()[0]:
            self.paddle.set_horizontal_velocity(-10)
            self.paddle.move()

        # Move the ball
        self.ball.move()

        # check collision between ball and paddle
        self.check_collide()

        # check if the ball hits the bottom
        self.check_end_condition()

    def check_end_condition(self):
        ball_y = self.ball.get_center()[1]
        if ball_y + self.ball.get_radius() > self.surface.get_height():
            self.continue_game = False

    def check_increase_ball_speed(self):
        # increases ball speed after certain amount of bricks are broken
        if not len(self.bricks) % self.bricks_to_break_speedup:
            self.ball.speed_up()

    def check_collide(self):

        # check is ball collids with apddle and reverses direction

        ball_radius = self.ball.get_radius()
        ball_x, ball_y = self.ball.get_center()

        ball_bottom_edge = ball_y + ball_radius
        ball_top_edge = ball_y - ball_radius
        ball_left_edge = ball_x - ball_radius
        ball_right_edge = ball_x + ball_radius

        ball_velocity_x, ball_velocity_y = self.ball.get_velocity()

        # if bottom of ball collides with paddle
        if (
            self.paddle.collide_point((ball_x, ball_bottom_edge))
            and ball_velocity_y > 0
        ):
            self.ball.reverse_y_velocity()
            self.ball.randomize_x_velocity()

        # if top of ball collides with brick
        for brick in self.bricks:
            # if collides with bottom of brick
            if brick.collide_point((ball_x, ball_top_edge)) and ball_velocity_y < 0:
                self.ball.reverse_y_velocity()
                self.bricks.remove(brick)
                self.check_increase_ball_speed()

            # if collids with top of brick
            if brick.collide_point((ball_x, ball_bottom_edge)) and ball_velocity_y > 0:
                self.ball.reverse_y_velocity()
                self.bricks.remove(brick)
                self.check_increase_ball_speed()

            # if colide with left side of brick
            if brick.collide_point((ball_left_edge, ball_y)) and ball_velocity_x < 0:
                self.ball.reverse_x_velocity()
                self.bricks.remove(brick)
                self.check_increase_ball_speed()

            # if collide with right side of brick
            if brick.collide_point((ball_right_edge, ball_y)) and ball_velocity_x > 0:
                self.ball.reverse_x_velocity()
                self.bricks.remove(brick)
                self.check_increase_ball_speed()

    def draw(self):
        self.surface.fill(self.bg_color)

        self.ball.draw()
        self.paddle.draw()

        # draw the bricks
        for brick in self.bricks:
            brick.draw()

        if not self.continue_game:
            self.draw_restart()

        pygame.display.update()  # make the updated surface appear on the display

    def draw_restart(self):
        string = "Click anywhere to start/restart"
        fg_color = pygame.Color("red")
        font = pygame.font.SysFont("", 30)
        text_box = font.render(string, True, fg_color, self.bg_color)

        # want to draw to middle of screen
        x = self.surface.get_width() // 2 - text_box.get_width() // 2
        y = self.surface.get_height() // 2 - text_box.get_height() // 2
        location = x, y

        self.surface.blit(text_box, location)


class Paddle:
    def __init__(self, x, y, width, height, color, surface):

        self.rect = pygame.Rect(x, y, width, height)
        self.color = pygame.Color(color)
        self.surface = surface
        self.horizontal_velocity = 0

    def draw(self):
        # draws the paddle to the surface
        pygame.draw.rect(self.surface, self.color, self.rect)

    def move(self):
        self.rect.move_ip(self.horizontal_velocity, 0)

        if self.rect.left <= 0:
            # if the paddle is all the way to the left
            self.rect.left = 0
        if self.rect.right >= self.surface.get_width():
            # if the paddle is all the way to the right
            self.rect.right = self.surface.get_width()

    def collide_point(self, dot_pos):
        # checks if paddle collides with ball
        return self.rect.collidepoint(dot_pos)

    def get_horizontal_velocity(self):
        return self.horizontal_velocity

    def set_horizontal_velocity(self, horizontal_velocity):
        self.horizontal_velocity = horizontal_velocity

    def get_pos(self):
        return self.rect.x, self.rect.y

    def get_width(self):
        return self.rect.width


class Ball:
    def __init__(self, color, radius, center, velocity, surface):
        # the ball is the ball hitting the blocks

        self.color = pygame.Color(color)
        self.radius = radius
        self.center = center
        self.velocity = velocity
        self.surface = surface

    def draw(self):
        pygame.draw.circle(self.surface, self.color, self.center, self.radius)

    def move(self):
        size = self.surface.get_size()
        for i in range(2):
            self.center[i] = self.center[i] + self.velocity[i]

            if self.center[i] < self.radius:  # left or the top edge
                self.velocity[i] = -self.velocity[i]
            if self.center[i] + self.radius > size[i]:  # right or bottom edge
                self.velocity[i] = -self.velocity[i]

    def get_center(self):
        return self.center

    def get_velocity(self):
        return self.velocity

    def set_velocity(self, velocity):
        self.velocity = velocity

    def reverse_y_velocity(self):
        self.velocity[1] = -self.velocity[1]

    def reverse_x_velocity(self):
        self.velocity[0] = -self.velocity[0]

    def get_radius(self):
        return self.radius

    def randomize_x_velocity(self):
        # randomize x velocity in beginning
        velocity_choice = [-0.5, 0.5]
        self.velocity[0] = random.choice(velocity_choice)

    def speed_up(self):
        if self.velocity[1] > 0:
            self.velocity[1] += 1
        else:
            self.velocity[1] -= 1

    def set_pos(self, x, y):
        self.center = [x, y]

    def set_velocity(self, x, y):
        self.velocity = [x, y]


class Brick:
    def __init__(self, x, y, width, height, color, surface):

        self.rect = pygame.Rect(x, y, width, height)
        self.color = pygame.Color(color)
        self.surface = surface

    def collide_point(self, dot_pos):
        return self.rect.collidepoint(dot_pos)

    def draw(self):
        pygame.draw.rect(self.surface, self.color, self.rect)


if __name__ == "__main__":
    main()
