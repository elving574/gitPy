import pygame
import random

# Initialize pygame
pygame.init()

# Screen dimensions
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600

# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
BLUE = (0, 0, 255)
GREEN = (0, 255, 0)
RED = (255, 0, 0)

# Set up the game window
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Infinite Fun Platformer")

# Frames per second
clock = pygame.time.Clock()
FPS = 60

# Fonts for displaying score
font = pygame.font.SysFont(None, 36)

# Player class
class Player(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.image = pygame.Surface((50, 50))
        self.image.fill(BLUE)
        self.rect = self.image.get_rect()
        self.rect.center = (SCREEN_WIDTH // 2, SCREEN_HEIGHT - 100)
        self.vel_y = 0
        self.jumping = False
        self.speed = 5
        self.score = 0
        self.new_platform_landed = True  # Tracks if new platform was landed on
        self.dead = False  # To track if the player is dead

    def update(self):
        # Move left and right
        keys = pygame.key.get_pressed()
        if keys[pygame.K_LEFT]:
            self.rect.x -= self.speed
        if keys[pygame.K_RIGHT]:
            self.rect.x += self.speed

        # Border collision
        if self.rect.left < 0:
            self.rect.left = 0
        if self.rect.right > SCREEN_WIDTH:
            self.rect.right = SCREEN_WIDTH

        # Jump
        if keys[pygame.K_SPACE] and not self.jumping:
            self.jumping = True
            self.vel_y = -30  # Double the jump velocity

        # Apply gravity
        self.vel_y += 1
        self.rect.y += self.vel_y

        # Prevent falling through the bottom
        if self.rect.bottom >= SCREEN_HEIGHT:
            self.rect.bottom = SCREEN_HEIGHT
            if self.score > 0:  # If player has earned any score, they die
                self.dead = True
            else:
                self.jumping = False
                self.vel_y = 0

    def score_up(self):
        self.score += 1

# Platform class
class Platform(pygame.sprite.Sprite):
    def __init__(self, x, y, width, height):
        super().__init__()
        self.image = pygame.Surface((width, height))
        self.image.fill(GREEN)
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y

    def update(self):
        pass

# Create sprite groups
all_sprites = pygame.sprite.Group()
platforms = pygame.sprite.Group()

# Create the player
player = Player()
all_sprites.add(player)

# Create some platforms
platform_list = [
    Platform(random.randint(0, SCREEN_WIDTH - 100), random.randint(100, SCREEN_HEIGHT - 50), 150, 20)
    for _ in range(5)
]

for platform in platform_list:
    all_sprites.add(platform)
    platforms.add(platform)

# Function to check platform overlap
def platform_overlap(new_platform):
    for platform in platforms:
        if new_platform.rect.colliderect(platform.rect):
            return True
    return False

# Function to generate new platforms above the screen
def generate_new_platforms():
    while len(platforms) < 6:
        new_platform = Platform(random.randint(0, SCREEN_WIDTH - 100), random.randint(-100, 0), 150, 20)
        if not platform_overlap(new_platform):  # Ensure no overlap
            platforms.add(new_platform)
            all_sprites.add(new_platform)

# Game loop
running = True
while running:
    clock.tick(FPS)
    
    # Event handling
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    # Update all sprites
    all_sprites.update()

    # Check for collision between player and platforms
    hits = pygame.sprite.spritecollide(player, platforms, False)
    
    if hits:
        for hit in hits:
            # Side collision prevention
            if player.vel_y > 0 and player.rect.bottom <= hit.rect.centery:
                player.jumping = False
                player.vel_y = 0
                player.rect.bottom = hit.rect.top

                # Only increment score if it's a new platform
                if player.new_platform_landed:
                    player.score_up()
                    player.new_platform_landed = False
            else:
                player.new_platform_landed = True

    # Move the screen upwards when the player jumps past the middle
    if player.rect.top < SCREEN_HEIGHT // 2:
        player.rect.top = SCREEN_HEIGHT // 2
        for platform in platforms:
            platform.rect.y += abs(player.vel_y)
        generate_new_platforms()

    # Remove platforms that go off the screen
    for platform in platforms:
        if platform.rect.top > SCREEN_HEIGHT:
            platform.kill()

    # If the player is dead, stop the game
    if player.dead:
        screen.fill(RED)
        game_over_text = font.render("GAME OVER!", True, WHITE)
        screen.blit(game_over_text, (SCREEN_WIDTH // 2 - 100, SCREEN_HEIGHT // 2))
        pygame.display.flip()
        pygame.time.wait(2000)
        running = False

    # Draw everything
    else:
        screen.fill(WHITE)
        all_sprites.draw(screen)

        # Display the score
        score_text = font.render(f"Score: {player.score}", True, BLACK)
        screen.blit(score_text, (SCREEN_WIDTH - 150, 10))

    # Update the display
    pygame.display.flip()

pygame.quit()
