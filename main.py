import math
import random

import pygame


def main():

    # initialize game
    pygame.init()

    # Create the screen
    WIDTH, HEIGHT = 800, 600
    pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("Breakout")
    w_surface = pygame.display.get_surface()

    # Run the game
    game = Game(w_surface)
    game.play()

    # the screen when game is finished
    pygame.quit()


class Game:
    def __init__(self, surface):
        """The object that runs the game"""

        # Static variables
        self.surface = surface
        self.bg_color = pygame.Color("black")
        self.middle_screen_x = self.surface.get_width() // 2
        self.middle_screen_y = self.surface.get_height() // 2

        # Dynamic variables
        self.FPS = 60
        self.game_Clock = pygame.time.Clock()
        self.close_clicked = False
        self.continue_game = False

        # create the paddle and ball
        self.paddle = self.create_paddle()
        self.ball = self.create_ball()

        # create bricks
        self.bricks = []
        self.create_bricks()
        self.brick_length = len(self.bricks)
        self.bricks_to_break_speedup = self.brick_length // 5

    def create_ball(self):
        """Creates the ball
        Return:
            ball(Ball): The abll to create
        """
        ball_velocity = [0, 4]
        radius = 5
        ball = Ball(
            "red",
            radius,
            [self.middle_screen_x, self.middle_screen_y],
            ball_velocity,
            self.surface,
        )
        ball.randomize_x_velocity()
        return ball

    def create_paddle(self):
        """Create the paddle
        Returns:
            paddle(Paddle): the paddle to create
        """
        paddle_height = 10
        paddle_width = 70
        paddle_y = self.surface.get_height() - 50
        paddle_x = self.surface.get_width() // 2 - paddle_width // 2

        paddle = Paddle(
            paddle_x,
            paddle_y,
            paddle_width,
            paddle_height,
            "white",
            self.surface,
        )

        return paddle

    def create_bricks(self):
        """Create the breaks for the game"""
        x = 0
        y = 200
        brick_colors = ["blue", "green", "yellow", "orange", "red"]

        # Make bricks for each colour spanning the whole width of the screen
        # with random sizes
        for color in brick_colors:
            while x <= self.surface.get_width():
                self.bricks.append(
                    Brick(x, y, random.randint(40, 60), 30, color, self.surface)
                )
                x += 53

            x = 0
            y -= 35

    def play(self):
        """Plays the breakout game"""
        while not self.close_clicked:
            self.handle_events()
            self.draw()
            if self.continue_game:
                self.update()

            self.game_Clock.tick(self.FPS)  # run at most with FPS

    def handle_events(self):
        """Handles every event of the game"""
        events = pygame.event.get()
        for event in events:
            if event.type == pygame.QUIT:
                self.close_clicked = True

            if not self.continue_game:
                if event.type == pygame.MOUSEBUTTONUP:
                    self.continue_game = True
                    self.restart_game()

    def restart_game(self):
        """Restarts the game"""

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
        """Updates the game objects"""

        # Move the paddle with player mouse
        mouse_pos_x = pygame.mouse.get_pos()[0]
        middle_of_mouse_x = mouse_pos_x - self.paddle.get_width() // 2

        # Make sure that the middle of the paddle follows the mouse not the edge
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
        """Checks to see if the ball hits the bottom of the screen, if so, end the game"""
        ball_y = self.ball.get_center()[1]
        if ball_y + self.ball.get_radius() > self.surface.get_height():
            self.continue_game = False

    def check_increase_ball_speed(self):
        """Based on the number of bricks created, increase the ball speed by 5 levels"""
        if not len(self.bricks) % self.bricks_to_break_speedup:
            self.ball.speed_up()

    def check_collide(self):
        """Checks the collision of the ball with the other objects of the game"""

        # ball variables
        ball_radius = self.ball.get_radius()
        ball_x, ball_y = self.ball.get_center()

        ball_bottom_edge = ball_y + ball_radius
        ball_top_edge = ball_y - ball_radius
        ball_left_edge = ball_x - ball_radius
        ball_right_edge = ball_x + ball_radius

        ball_velocity_x, ball_velocity_y = self.ball.get_velocity()
        ball_velocity = math.sqrt(ball_velocity_x**2 + ball_velocity_y**2)

        # paddle variables
        middle_of_paddle_x = self.paddle.get_pos()[0] + self.paddle.get_width() / 2

        # ball position from iddle
        # positive is right side
        # negative is left side
        ball_pos_from_middle_of_paddle = ball_x - middle_of_paddle_x
        percentage_from_middle = ball_pos_from_middle_of_paddle / (
            self.paddle.get_width() / 2
        )
        angle_percentage = percentage_from_middle * 90

        # calculate the x and y from velocity and angle
        new_x_vel = math.sin(math.radians(angle_percentage)) * ball_velocity
        new_y_vel = math.cos(math.radians(angle_percentage)) * ball_velocity

        # if bottom of ball collides with paddle
        if (
            self.paddle.collide_point((ball_x, ball_bottom_edge))
            and ball_velocity_y > 0
        ):
            self.ball.set_velocity(new_x_vel, new_y_vel)
            self.ball.reverse_y_velocity()

        # check if ball collides with brick
        try:
            for brick in self.bricks:
                # if collides with bottom of brick
                if brick.collide_point((ball_x, ball_top_edge)) and ball_velocity_y < 0:
                    self.ball.reverse_y_velocity()
                    self.bricks.remove(brick)
                    self.check_increase_ball_speed()

                # if collids with top of brick
                if (
                    brick.collide_point((ball_x, ball_bottom_edge))
                    and ball_velocity_y > 0
                ):
                    self.ball.reverse_y_velocity()
                    self.bricks.remove(brick)
                    self.check_increase_ball_speed()

                # if colide with left side of brick
                if (
                    brick.collide_point((ball_left_edge, ball_y))
                    and ball_velocity_x < 0
                ):
                    self.ball.reverse_x_velocity()
                    self.bricks.remove(brick)
                    self.check_increase_ball_speed()

                # if collide with right side of brick
                if (
                    brick.collide_point((ball_right_edge, ball_y))
                    and ball_velocity_x > 0
                ):
                    self.ball.reverse_x_velocity()
                    self.bricks.remove(brick)
                    self.check_increase_ball_speed()

        except ValueError:
            print("That brick doesn't exist!")

    def draw(self):
        """Draws the game objects to the screen"""
        self.surface.fill(self.bg_color)

        # draw ball and paddle
        self.ball.draw()
        self.paddle.draw()

        # draw the bricks
        for brick in self.bricks:
            brick.draw()

        # draw the restart prompt if game is over
        if not self.continue_game:
            self.draw_restart()

        pygame.display.update()  # make the updated surface appear on the display

    def draw_restart(self):
        """Draw the restart prompt when the game is over"""
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
        """The Paddle class is the object that the player uses to hit the ball.

        Args:
            x(int): the x pos of the top left of the paddle
            y(int): the y pos of the top left of the paddle
            width(int): the width of the paddle
            height(int): the height of the paddle
            surface(pygame.surface): the screen display

        """

        self.rect = pygame.Rect(x, y, width, height)
        self.color = pygame.Color(color)
        self.surface = surface
        self.horizontal_velocity = 0

    def draw(self):
        """Draws the paddle to the surface"""
        pygame.draw.rect(self.surface, self.color, self.rect)

    def move(self):
        """Moves the paddle IN PLACE. Restricts paddle movement to edges of screen"""
        self.rect.move_ip(self.horizontal_velocity, 0)
        if self.rect.left <= 0:
            # if the paddle is all the way to the left
            self.rect.left = 0
        if self.rect.right >= self.surface.get_width():
            # if the paddle is all the way to the right
            self.rect.right = self.surface.get_width()

    def collide_point(self, dot_pos):
        """Checks if paddle collides with ball"""
        return self.rect.collidepoint(dot_pos)

    def get_horizontal_velocity(self):
        """Gets the horizontal velocity of the paddle"""
        return self.horizontal_velocity

    def set_horizontal_velocity(self, horizontal_velocity):
        """Sets the horizontal velocity of the paddle"""
        self.horizontal_velocity = horizontal_velocity

    def get_pos(self):
        """Gets the position of the paddle (top left)
        Returns:
            self.rect.x, self.rect.y(tuple): a tuple of the x, y position of the paddle
        """
        return self.rect.x, self.rect.y

    def get_width(self):
        """Gets the width of the paddle
        Returns:
            self.rect.width(int): the width of the paddle
        """
        return self.rect.width


class Ball:
    def __init__(self, color, radius, center, velocity, surface):
        """The ball is the object that hits the bricks and gets hit by the paddle
        Args:
            color(str): the color fo the ball
            radius(int): determines how big the ball is
            center(list): the center position of the ball
            velocity(list): the x,y velocity of the ball
            surface(pygame.surface): the surface of the screen
        """

        self.color = pygame.Color(color)
        self.radius = radius
        self.center = center
        self.velocity = velocity
        self.surface = surface

    def draw(self):
        """Draws the ball to the screen"""
        pygame.draw.circle(self.surface, self.color, self.center, self.radius)

    def move(self):
        """Moves the ball on the screen. Restricts the ball within the screen."""
        size = self.surface.get_size()
        for i in range(2):
            self.center[i] = self.center[i] + self.velocity[i]

            if self.center[i] < self.radius:  # left or the top edge
                self.velocity[i] = -self.velocity[i]
            if self.center[i] + self.radius > size[i]:  # right or bottom edge
                self.velocity[i] = -self.velocity[i]

    def get_center(self):
        """Gets the center position of the ball
        Returns:
            self.center(list): a list x, y of the ball pos
        """
        return self.center

    def get_velocity(self):
        """Gets the velocity of the ball
        Returns:
            self.velocity[list]: the x, y velocity of the ball
        """
        return self.velocity

    def reverse_y_velocity(self):
        """Reverses the y velocity of the ball"""
        self.velocity[1] = -self.velocity[1]

    def reverse_x_velocity(self):
        """Reverses the x velocity of the ball"""
        self.velocity[0] = -self.velocity[0]

    def get_radius(self):
        """Gets the radius of the ball
        Returns:
            self.radius(int): the radius of the ball
        """
        return self.radius

    def randomize_x_velocity(self):
        """Gives a random chance of left or right for the ball to go"""
        velocity_choice = [-0.5, 0.5]
        self.velocity[0] = random.choice(velocity_choice)

    def speed_up(self):
        """Speeds up the ball vertical velocity by increment of 1"""
        if self.velocity[1] > 0:
            self.velocity[1] += 1
        else:
            self.velocity[1] -= 1

    def set_pos(self, x, y):
        """Sets the position of the ball (useful for restarting game)"""
        self.center = [x, y]

    def set_velocity(self, x, y):
        """Sets the velocity of the ball."""
        self.velocity = [x, y]


class Brick:
    def __init__(self, x, y, width, height, color, surface):
        """The Brick class is the object we want to break with the ball
        Args:
            x(int): the x pos of the brick
            y(int): the y pos of the brick
            width(int): the width of the brick
            height(int): the height of the brick
            color(str): the color of the brick
            surface(pygame.display.surface): the screen of the game
        """

        self.rect = pygame.Rect(x, y, width, height)
        self.color = pygame.Color(color)
        self.surface = surface

    def collide_point(self, dot_pos):
        """Checks if the brick has collided with a certain pos
        Args:
            dot_pos(tuple): an x, y tuple position
        Returns:
            self.rect.collidepoint(dot_pos)(bool): returns true if a collision has been made
        """
        return self.rect.collidepoint(dot_pos)

    def draw(self):
        """Draws the bricks to the screen"""
        pygame.draw.rect(self.surface, self.color, self.rect)


if __name__ == "__main__":
    main()
