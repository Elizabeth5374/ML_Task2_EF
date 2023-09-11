# This Code is Heavily Inspired By The YouTuber: Cheesy AI
# Code Chaned, Optimized And Commented By: NeuralNine (Florian Dedov)
# This code has again been hoisted by the CGS Digital Innovation Department
# giving credit to the above authors for the benfit of our education in ML


#could change survival_threshold

import math
import random
import sys
import os

import neat
import pygame

# Constants
# WIDTH = 1600
# HEIGHT = 880

WIDTH = 1920
HEIGHT = 1080

CAR_SIZE_X = 60
CAR_SIZE_Y = 60

BORDER_COLOR = (255, 255, 255, 255)  # Color To Crash on Hit

current_generation = 0  # Generation counter
"""
The Car Class 

Throughout this section, you will need to explore each function
and provide extenive comments in the spaces denoted by the 
triple quotes(block quotes) """ """.
Your comments should describe each function and what it is doing, 
why it is necessary and where it is being used in the rest of the program.

"""


class Car:
    """1. This Function:
        This function  constructs the car and sets it up with basic features including: loading the image, 
        sets the starting position, speed and angle, caculates the center of the car and makes an array of
        the radars and draws them, it also defines some important varibles inclusing a boolean if it is still
        alive(set to true as the car starts alive), the distance it has driven (initiated at 0) and the current 
        time(initiated at 0), which are used throughout the program to evaluate the suxcess of the car. these are 
        all  important for setting up the car and this function is called for every car that is created in this class. 
    
    """

    def __init__(self):
        # Load Car Sprite and Rotate
        self.sprite = pygame.image.load("car.png").convert()  # Convert Speeds Up A Lot
        self.sprite = pygame.transform.scale(self.sprite, (CAR_SIZE_X, CAR_SIZE_Y))
        self.rotated_sprite = self.sprite

        # self.position = [690, 740] # Starting Position
        self.position = [830, 920]  # Starting Position
        self.angle = 0
        self.speed = 0

        self.speed_set = False  # Flag For Default Speed Later on

        self.center = [
            self.position[0] + CAR_SIZE_X / 2,
            self.position[1] + CAR_SIZE_Y / 2,
        ]  # Calculate Center

        self.radars = []  # List For Sensors / Radars
        self.drawing_radars = []  # Radars To Be Drawn

        self.alive = True  # Boolean To Check If Car is Crashed

        self.distance = 0  # Distance Driven
        self.time = 0  # Time Passed

    """ 2. This Function:
            This function draws the sprite(blit) and radars on the screen using all the information from the 
            init function such as it's staring position and angle and which sprite to use(in this case car.png). 
            The libary pygame is used to draw them.

            This function is nescecary for the programer to see the cars moving around the track and where 
            their radars are. without this function the programer would only know the cars scores but would not 
            be able to visulaise the function
    """

    def draw(self, screen):
        screen.blit(self.rotated_sprite, self.position)  # Draw Sprite
        self.draw_radar(screen)  # OPTIONAL FOR SENSORS

    """ 3. This Function:
        This function uses pygame to draw the radars that were previousouly defined, in the above function it is called
        using the line "self.draw_radar(screen)", there is a foor loop that draws each radar line and the circle on the end

        this function is optional but is important to visualise the radars and from that the information the program is 
        using to detrmine it's next move.
    """

    def draw_radar(self, screen):
        # Optionally Draw All Sensors / Radars
        for radar in self.radars:
            position = radar[0]
            pygame.draw.line(screen, (0, 255, 0), self.center, position, 1)
            pygame.draw.circle(screen, (0, 255, 0), position, 5)

    """ 4. This Function:
        This function checks for collisions between the car and the edge of the track, there is a for loop that 
        itirates over every point in the rectangulat box around the car, for each point it uses an if statment to 
        determine if it is touching the border of the track, in which case it changes the self.alive varible to false.

        This function is very important as it is used to determine if/when the car dies, without it the cars would never die
        and would never evolve to drive around the track.
    """

    def check_collision(self, game_map):
        self.alive = True
        for point in self.corners:
            # If Any Corner Touches Border Color -> Crash
            # Assumes Rectangle
            if game_map.get_at((int(point[0]), int(point[1]))) == BORDER_COLOR:
                self.alive = False
                break

    """ 5. This Function:
        essentaly this function detrimes how long the radar should be, the first part caculates the x and y coordonates of
        radar. self.center[0] and self.center[1] represent the center point, from there cos and sin are used to find the 
        coorodniates of the end of the radar. The second part (starting at the while loop) caculates the length of the radars,
        if the radars have not reached the edge of the track and are not longer that 300 they get longer and longer. 
        again this uses cos and sin to find the coordinates of the end of the radars. Then the length of the radars is 
        caculated and it and the coodinates are added to the radars list to be used by the algorithim to decide the next action.

        this function is important because it caculates and supplies the program with some of the most essintial data that it uses
        to detrmine which action to take. without it the program would have no idea where the edge of the track is and as such
        would not know which action to take and would crash almost immediatly.

    
    """

    def check_radar(self, degree, game_map):
        length = 0
        x = int(
            self.center[0]
            + math.cos(math.radians(360 - (self.angle + degree))) * length
        )
        y = int(
            self.center[1]
            + math.sin(math.radians(360 - (self.angle + degree))) * length
        )

        # While We Don't Hit BORDER_COLOR AND length < 300 (just a max) -> go further and further
        while not game_map.get_at((x, y)) == BORDER_COLOR and length < 300:
            length = length + 1
            x = int(
                self.center[0]
                + math.cos(math.radians(360 - (self.angle + degree))) * length
            )
            y = int(
                self.center[1]
                + math.sin(math.radians(360 - (self.angle + degree))) * length
            )

        # Calculate Distance To Border And Append To Radars List
        dist = int(
            math.sqrt(math.pow(x - self.center[0], 2) + math.pow(y - self.center[1], 2))
        )
        self.radars.append([(x, y), dist])

    """ 6. This Function:
        This function updates the car position, angle and hitbox. firstly it initilises the speed to 20, after tihis the neural network decides it's speed.
        then it updates the position and rotation of the car in the x-direction. after this it increaces the distance and time varibles for the car, which are later used to 
        caculate it's score. similar to before it updates the position and orientation of the car but in the y-position.
        with the updated position it caculates the new center which is used to cacuate and display the radars.
        after this it caculates the position of the hit box which is used to determine if the car has hit the edge of the track.
        finaly it checks the collisions of the car with the check_collision() function and checks the each of the cars radars.

        This function is important because it updates the car allowing the neural network to interact with the map in real time and 
        accuretly represent the cars position.
    """

    def update(self, game_map):
        # Set The Speed To 20 For The First Time
        # Only When Having 4 Output Nodes With Speed Up and Down
        if not self.speed_set:
            self.speed = 20
            self.speed_set = True

        # Get Rotated Sprite And Move Into The Right X-Direction
        # Don't Let The Car Go Closer Than 20px To The Edge
        self.rotated_sprite = self.rotate_center(self.sprite, self.angle)
        self.position[0] += math.cos(math.radians(360 - self.angle)) * self.speed
        self.position[0] = max(self.position[0], 20)
        self.position[0] = min(self.position[0], WIDTH - 120)

        # Increase Distance and Time
        self.distance += self.speed
        self.time += 1

        # Same For Y-Position
        self.position[1] += math.sin(math.radians(360 - self.angle)) * self.speed
        self.position[1] = max(self.position[1], 20)
        self.position[1] = min(self.position[1], WIDTH - 120)

        # Calculate New Center
        self.center = [
            int(self.position[0]) + CAR_SIZE_X / 2,
            int(self.position[1]) + CAR_SIZE_Y / 2,
        ]

        # Calculate Four Corners of the rectangle around the car
        # Length Is Half The Side
        length = 0.5 * CAR_SIZE_X
        left_top = [
            self.center[0] + math.cos(math.radians(360 - (self.angle + 30))) * length,
            self.center[1] + math.sin(math.radians(360 - (self.angle + 30))) * length,
        ]
        right_top = [
            self.center[0] + math.cos(math.radians(360 - (self.angle + 150))) * length,
            self.center[1] + math.sin(math.radians(360 - (self.angle + 150))) * length,
        ]
        left_bottom = [
            self.center[0] + math.cos(math.radians(360 - (self.angle + 210))) * length,
            self.center[1] + math.sin(math.radians(360 - (self.angle + 210))) * length,
        ]
        right_bottom = [
            self.center[0] + math.cos(math.radians(360 - (self.angle + 330))) * length,
            self.center[1] + math.sin(math.radians(360 - (self.angle + 330))) * length,
        ]
        self.corners = [left_top, right_top, left_bottom, right_bottom]

        # Check Collisions And Clear Radars
        self.check_collision(game_map)# call the check-collision function
        self.radars.clear()

        # From -90 To 120 With Step-Size 45 Check Radar
        for d in range(-90, 120, 45):
            self.check_radar(d, game_map)

    """ 7. This Function:
        This function finds the distance from the car to the border using the radars that were defined earlier.
        return_values are initiated at 0 and then a fro loop itirates through each radar assing a value to the 
        corresponding return_value list item. it then returns the return-value.
    """

    def get_data(self):
        # Get Distances To Border
        radars = self.radars
        return_values = [0, 0, 0, 0, 0]
        for i, radar in enumerate(radars):
            return_values[i] = int(radar[1] / 30)

        return return_values

    """ 8. This Function:
        this Function checks if the car is still alive. it uses the boolean self.alive to check this which 
        is modified in the function check_collision(). this is important to ensure that when a car dies it
        dose not continue to drive and ensure that its score it accurate.
    """

    def is_alive(self):
        # Basic Alive Function
        return self.alive

    """ 9. This Function:
        this function caculated the car's score using its distance and size. this is important to 
        evaluate how well the car preformed compared to other cars, and thus decide if its genetics should be passed on.
    """

    def get_reward(self):
        # Calculate Reward (Maybe Change?)
        # return self.distance / 50.0
        return self.distance / (CAR_SIZE_X / 2)

    """ 10. This Function:
        This function rotates the car using pygame. this is important as it visualy represnts the car turning and 
        shows the user the cars current action. whichout this function the car would never turn onscreen and would just
        appear to go directly ahead.
    """

    def rotate_center(self, image, angle):
        # Rotate The Rectangle
        rectangle = image.get_rect()
        rotated_image = pygame.transform.rotate(image, angle)
        rotated_rectangle = rectangle.copy()
        rotated_rectangle.center = rotated_image.get_rect().center
        rotated_image = rotated_image.subsurface(rotated_rectangle).copy()
        return rotated_image


""" This Function:
    overall this function runs the simulation. 
    It starts by defining nets and cars and initilising the display with pygame. then it then populates the array cars
    with the initial neural networks, the initial fittness of each genome is 0. the next part prepars the informnation 
    that is displayed on the map by setting up the clock and defining the fonts. it also loads the map, whic in this case
    is map4. the lines "global current_generation" and "current_generation += 1" define a global varible that is the number
    of generations and increments it for each generation that exsists.

    The while True loop is the core of the code. it takes each car in the list cars(which is defined at the top), caculates 
    its decision using its neural network with the NEAT algorithim. It then adjucts the cars angle or speed. Then the program 
    checks if the car is still alive and gives it a reward based on that and updates the car possition on the game map.
    the code after this draws the map and all the cars with pygame and displays the info on the map: generation num and num of 
    cars still alive. the last two lines update the screen at a rate of 60 FPS.

    This function is one of the key functions and without it there would be no machene learning. 
"""


def run_simulation(genomes, config):
    # Empty Collections For Nets and Cars
    nets = []
    cars = []

    # Initialize PyGame And The Display
    pygame.init()
    screen = pygame.display.set_mode((WIDTH, HEIGHT), pygame.FULLSCREEN)

    # For All Genomes Passed Create A New Neural Network
    for i, g in genomes:
        net = neat.nn.FeedForwardNetwork.create(g, config)
        nets.append(net)
        g.fitness = 0

        cars.append(Car())

    # Clock Settings
    # Font Settings & Loading Map
    clock = pygame.time.Clock()
    generation_font = pygame.font.SysFont("Arial", 30)
    alive_font = pygame.font.SysFont("Arial", 20)
    # game_map = pygame.image.load(mapnum).convert()  # Convert Speeds Up A Lot
    game_map = pygame.image.load("map4.png").convert()  # Convert Speeds Up A Lot

    global current_generation
    current_generation += 1

    # Simple Counter To Roughly Limit Time (Not Good Practice)
    counter = 0

    while True:
        # Exit On Quit Event
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                sys.exit(0)

        # For Each Car Get The Acton It Takes
        for i, car in enumerate(cars):
            output = nets[i].activate(car.get_data())
            choice = output.index(max(output))
            if choice == 0:
                car.angle += 10  # Left
            elif choice == 1:
                car.angle -= 10  # Right
            elif choice == 2:
                if car.speed - 2 >= 12:
                    car.speed -= 2  # Slow Down
            else:
                car.speed += 2  # Speed Up

        # Check If Car Is Still Alive
        # Increase Fitness If Yes And Break Loop If Not
        still_alive = 0
        for i, car in enumerate(cars):
            if car.is_alive():
                still_alive += 1
                car.update(game_map)
                genomes[i][1].fitness += car.get_reward()

        if still_alive == 0:
            break

        counter += 1
        if counter == 30 * 40:  # Stop After About 20 Seconds
            break

        # Draw Map And All Cars That Are Alive
        screen.blit(game_map, (0, 0))
        for car in cars:
            if car.is_alive():
                car.draw(screen)

        # Display Info
        text = generation_font.render(
            "Generation: " + str(current_generation), True, (0, 0, 0)
        )
        text_rect = text.get_rect()
        text_rect.center = (900, 450)
        screen.blit(text, text_rect)

        text = alive_font.render("Still Alive: " + str(still_alive), True, (0, 0, 0))
        text_rect = text.get_rect()
        text_rect.center = (900, 490)
        screen.blit(text, text_rect)

        pygame.display.flip()
        clock.tick(60)  # 60 FPS


""" 1. This Section:
    This section loads the infomation from the config file and creats a neat configuration object with it, which 
    which determines how the program behaves, eg. population size, activation function ..., It then creats the 
    population and and finds it's stats with neat, which it prints to the terminal. It also sets a limit for 
    the maximum number of generations, which in this case is 1000.

    This section is important because it sets up the car to have all the correct configurations from the config file
    and creats the population of cars. it is also important because it prints the statistics from the program alowing the
    programer to see how well the program is going with statistics.
"""
if __name__ == "__main__":
    # Load Config
    config_path = "./config.txt"
    config = neat.config.Config(
        neat.DefaultGenome,
        neat.DefaultReproduction,
        neat.DefaultSpeciesSet,
        neat.DefaultStagnation,
        config_path,
    )

    # Create Population And Add Reporters
    population = neat.Population(config)
    population.add_reporter(neat.StdOutReporter(True))
    stats = neat.StatisticsReporter()
    population.add_reporter(stats)

    # Run Simulation For A Maximum of 1000 Generations
    population.run(run_simulation, 1000)
