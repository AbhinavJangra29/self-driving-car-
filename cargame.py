import pygame
import math

screen_width = 1500
screen_height = 800
check_point = ((1332,659),(1088,396),(1162,132),(950,269),(708,161),(636,400),(205,154),(200,339),(282,576))

class Car:
    def __init__(self, car_file, map_file, pos):
        self.surface = pygame.image.load(car_file)
        self.map = pygame.image.load(map_file)
        self.surface = pygame.transform.scale(self.surface, (100, 100))
        self.rotate_surface = self.surface
        self.pos = pos
        self.four_points=[0,0,0,0]
        self.angle = 0
        self.speed = 0
        self.center = [self.pos[0] + 50, self.pos[1] + 50]
        self.radars = []
        self.radars_for_draw = []
        self.is_alive = True
        self.current_check = 0
        self.prev_distance = 0
        self.cur_distance = 0
        self.goal = False
        self.check_flag = False
        self.distance = 0
        self.time_spent = 0
        #checking of radars
        for d in range(-90, 120, 45):
            self.check_radar(d)
        #draws radars
        for d in range(-90, 105, 15):
            self.check_radar_for_draw(d)

    #renders car on screen
    def draw(self, screen):
        screen.blit(self.rotate_surface, self.pos)


    #draw white points around car sprite to check collision
    def draw_collision(self, screen):
        #print("drawing collision")

        for i in range(4):
            #get all x and y cor
            x = int(self.four_points[i][0])
            y = int(self.four_points[i][1])
            #draw white circles around the car to check for collision
            pygame.draw.circle(screen, (255, 255, 255), (x, y), 5)
            #if any touches the white background turn them to black
            if self.map.get_at((int(x), int(y))) == (255, 255, 255, 255):
                pygame.draw.circle(screen, (0, 0, 0), (x, y), 5)

    #drawing the radars on screen
    def draw_radar(self, screen):
        for r in self.radars_for_draw:
            pos, dist = r
            #line of radar
            pygame.draw.line(screen, (0, 255, 0), self.center, pos, 1)
            #green dots at radar end last argument shows thickness of point or line
            pygame.draw.circle(screen, (0, 255, 0), pos, 3)

    #checks 4 points if they are off track or not
    def check_collision(self):
        self.is_alive = True
        for p in self.four_points:
            #if color at fourpoint cordinate has color of white it means we are off track
            if self.map.get_at((int(p[0]), int(p[1]))) == (255, 255, 255, 255):
                self.is_alive = False
                break

    def check_radar(self, degree):
        #currentl length of radar is 0 we draw them in the loop after checking
        len = 0
        x = int(self.center[0] + math.cos(math.radians(360 - (self.angle + degree))) * len)
        y = int(self.center[1] + math.sin(math.radians(360 - (self.angle + degree))) * len)
        #check the radar line until it touches a white pixel or reaches 200 px
        while not self.map.get_at((x, y)) == (255, 255, 255, 255) and len < 200:
            len = len + 1
            #horiz  and vertical  component tak check karo
            x = int(self.center[0] + math.cos(math.radians(360 - (self.angle + degree))) * len)
            y = int(self.center[1] + math.sin(math.radians(360 - (self.angle + degree))) * len)
        #distance calculate karo formula se from center to radar endpoint
        dist = int(math.sqrt(math.pow(x - self.center[0], 2) + math.pow(y - self.center[1], 2)))
        #save this info to help draw later
        self.radars.append([(x, y), dist])

    #detect even further and maintains another list
    def check_radar_for_draw(self, degree):
        len = 0
        x = int(self.center[0] + math.cos(math.radians(360 - (self.angle + degree))) * len)
        y = int(self.center[1] + math.sin(math.radians(360 - (self.angle + degree))) * len)

        while not self.map.get_at((x, y)) == (255, 255, 255, 255) and len < 2000:
            len = len + 1
            x = int(self.center[0] + math.cos(math.radians(360 - (self.angle + degree))) * len)
            y = int(self.center[1] + math.sin(math.radians(360 - (self.angle + degree))) * len)

        dist = int(math.sqrt(math.pow(x - self.center[0], 2) + math.pow(y - self.center[1], 2)))
        self.radars_for_draw.append([(x, y), dist])

    #yellow circle checkpoints
    def check_checkpoint(self):
        p = check_point[self.current_check]
        self.prev_distance = self.cur_distance
        dist = get_distance(p, self.center)
        if dist < 70:
            self.current_check += 1
            self.prev_distance = 9999
            self.check_flag = True
            if self.current_check >= len(check_point):
                self.current_check = 0
                self.goal = True
            else:
                self.goal = False

        self.cur_distance = dist

    def update(self):#updating state of car
        #check speed
        self.speed -= 0.5#decreasing by default
        if self.speed > 10:#between 10 and 0 speed will be
            self.speed = 10
        if self.speed < 1:
            self.speed = 1

        #check position
        #updating rotated surface of car based on the angle, try commenting it and see
        self.rotate_surface = rot_center(self.surface, self.angle)
        #check cars x and y centre cordinates are within screen
        self.pos[0] += math.cos(math.radians(360 - self.angle)) * self.speed
        if self.pos[0] < 20:
            self.pos[0] = 20
        elif self.pos[0] > screen_width - 120:
            self.pos[0] = screen_width - 120

        self.distance += self.speed#technically shouldnt be distance but its just a varibale
        self.time_spent += 1
        self.pos[1] += math.sin(math.radians(360 - self.angle)) * self.speed
        if self.pos[1] < 20:
            self.pos[1] = 20
        elif self.pos[1] > screen_height - 120:
            self.pos[1] = screen_height - 120

        # caculate 4 collision points using horoz and vertical components
        self.center = [int(self.pos[0]) + 50, int(self.pos[1]) + 50]
        len = 40
        left_top = [self.center[0] + math.cos(math.radians(360 - (self.angle + 30))) * len, self.center[1] + math.sin(math.radians(360 - (self.angle + 30))) * len]
        right_top = [self.center[0] + math.cos(math.radians(360 - (self.angle + 150))) * len, self.center[1] + math.sin(math.radians(360 - (self.angle + 150))) * len]
        left_bottom = [self.center[0] + math.cos(math.radians(360 - (self.angle + 210))) * len, self.center[1] + math.sin(math.radians(360 - (self.angle + 210))) * len]
        right_bottom = [self.center[0] + math.cos(math.radians(360 - (self.angle + 330))) * len, self.center[1] + math.sin(math.radians(360 - (self.angle + 330))) * len]
        self.four_points = [left_top, right_top, left_bottom, right_bottom]

#car clss was defined above and will be used here
class PyRace2D:
    def __init__(self, is_render = True):
        pygame.init()
        self.screen = pygame.display.set_mode((screen_width, screen_height))
        self.clock = pygame.time.Clock()
        self.font = pygame.font.SysFont("Arial", 30)
        self.car = Car('car.png', 'map2.png', [624,630])
        self.game_speed = 60
        self.is_render = is_render
        self.mode = 0

    def action(self, action):
        #w
        if action == 0:
            self.car.speed += 2
            #d
        if action == 1:
            self.car.angle += 5
            #a
        elif action == 2:
            self.car.angle -= 5
        # else:
        #     self.car.speed += 0

        #check and render
        self.car.update()
        self.car.check_collision()
        self.car.check_checkpoint()

        self.car.radars.clear()
        for d in range(-90, 120, 45):
            self.car.check_radar(d)

    def evaluate(self):
        reward = 0
        """
        if self.car.check_flag:
            self.car.check_flag = False
            reward = 2000 - self.car.time_spent
            self.car.time_spent = 0
        """
        if not self.car.is_alive:
            reward = -10000 + self.car.distance
        #goal is checkpoint
        elif self.car.goal:
            reward = 10000
        return reward

    def is_done(self):
        if not self.car.is_alive or self.car.goal:
            self.car.current_check = 0
            self.car.distance = 0
            return True
        return False

    # responsible for providing the current state
    def observe(self):
        # converts radar measurements into a simplified state representation,
        radars = self.car.radars
        ret = [0, 0, 0, 0, 0]
        i = 0
        for r in radars:
            ret[i] = int(r[1] / 20)
            i += 1

        return ret

    def view(self):
        # draw game
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                done = True
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_m:
                    self.mode += 1
                    self.mode = self.mode % 3
        #draw the map onto screen
        self.screen.blit(self.car.map, (0, 0))

        #if m is pressed mode is set to 1 in that case turn the screen black
        if self.mode == 1:
            self.screen.fill((0, 0, 0))

        self.car.radars_for_draw.clear()
        for d in range(-90, 105, 15):
            self.car.check_radar_for_draw(d)
        pygame.draw.circle(self.screen, (255, 255, 0), check_point[self.car.current_check], 70, 1)
        #draw coll points and radar lines on screen
        self.car.draw_collision(self.screen)
        self.car.draw_radar(self.screen)
        self.car.draw(self.screen)


        text = self.font.render("", True, (255, 255, 0))
        text_rect = text.get_rect()
        text_rect.center = (screen_width/2, 100)
        self.screen.blit(text, text_rect)


        #update the rendering and cap fps
        pygame.display.flip()
        self.clock.tick(self.game_speed)


def get_distance(p1, p2):
	return math.sqrt(math.pow((p1[0] - p2[0]), 2) + math.pow((p1[1] - p2[1]), 2))

def rot_center(image, angle):
    orig_rect = image.get_rect()
    rot_image = pygame.transform.rotate(image, angle)
    rot_rect = orig_rect.copy()
    rot_rect.center = rot_image.get_rect().center
    rot_image = rot_image.subsurface(rot_rect).copy()
    return rot_image


pygame.init()

# Create an instance of PyRace2D
game = PyRace2D()

# Game loop
running = True
while running:
    # Handle events
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    # Get the state of all keys
    keys = pygame.key.get_pressed()

    # Accumulate actions based on keyboard inputs
    move_action = 3
    turn_action = 3

    if keys[pygame.K_w]:
        move_action = 0  # Accelerate forward
    if keys[pygame.K_a]:
        turn_action = 1  # Turn left
    if keys[pygame.K_d]:
        turn_action = 2  # Turn right

    # Perform actions
    game.action(move_action)
    game.action(turn_action)

    # Update the game state
    game.evaluate()
    # if game.is_done():
    #     # Reset the game or take appropriate actions when the game is done
    #     game = PyRace2D()

    # Observe the state
    state = game.observe()

    # Render the game
    game.view()

# Quit Pygame
pygame.quit()
