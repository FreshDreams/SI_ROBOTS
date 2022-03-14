import sys
import pygame
import random
from pygame import mixer


pygame.init()

pygame.display.set_mode((750,750))
menubck = pygame.image.load("menubck.png").convert()
backgr = pygame.image.load("bck.png").convert()
pygame.display.set_caption("CyJam TEST")
icon = pygame.image.load("robot.png").convert_alpha()
pygame.display.set_icon(icon)
sheet = pygame.image.load("sprite_sheet_robot_green.png").convert_alpha()
sheet = pygame.transform.scale(sheet, (384, 128))
rocket = pygame.image.load("rocket.png").convert_alpha()
ufo = pygame.image.load("ghost.png").convert_alpha()
ufor = pygame.image.load("ufor.png").convert_alpha()
ufoy = pygame.image.load("ufoy.png").convert_alpha()
laser = pygame.image.load("laser.png").convert_alpha()
lasery = pygame.image.load("lasery.png").convert_alpha()
laserg = pygame.image.load("laserg.png").convert_alpha()
#menuimg = pygame.image.load("menubck.png").convert()

def getimg(x, y, width, height):
    image = pygame.Surface((width, height))
    image.blit(sheet, (0, 0), (x, y, width, height))
    image.set_colorkey((0, 0, 0))
    return image

frame1 = getimg(0, 0, 128, 128)
frame2 = getimg(64, 0, 64, 64)
frame3 = getimg(128, 0, 64, 64)


class Button():
    def __init__(self, image, pos, text_input, font, base_color, hovering_color):
        self.image = image
        self.x_pos = pos[0]
        self.y_pos = pos[1]
        self.font = font
        self.base_color, self.hovering_color = base_color, hovering_color
        self.text_input = text_input
        self.text = self.font.render(self.text_input, True, self.base_color)

        self.rect = self.image.get_rect(center=(self.x_pos, self.y_pos))
        self.text_rect = self.text.get_rect(center=(self.x_pos, self.y_pos))
        if self.image is None:
            self.image = self.text
    def update(self, screen):
        if self.image is not None:
            screen.blit(self.image, self.rect)
        screen.blit(self.text, self.text_rect)

    def checkForInput(self, position):
        if position[0] in range(self.rect.left, self.rect.right) and position[1] in range(self.rect.top, self.rect.bottom):
            return True
        return False

    def changeColor(self, position):
        if position[0] in range(self.rect.left, self.rect.right) and position[1] in range(self.rect.top, self.rect.bottom):
            self.text = self.font.render(self.text_input, True, self.hovering_color)
        else:
            self.text = self.font.render(self.text_input, True, self.base_color)

class Laser:
    def __init__(self, x, y, img):
        self.x = x
        self.y = y
        self.img = img
        self.mask = pygame.mask.from_surface(self.img)

    def draw(self, window):
        window.blit(self.img, (self.x, self.y))

    def move(self, spd):
        self.y += spd

    def ofscr(self, hgt):
        return not(self.y <= hgt and self.y >= 0)

    def coll(self, obj):
        return collide(obj, self)

def collide(obj1, obj2):
    offsetx = obj2.x - obj1.x
    offsety = obj2.y - obj1.y
    return obj1.mask.overlap(obj2.mask, (offsetx, offsety)) != None


class Robot:
    COOLDOWN = 30

    def __init__(self, x, y, health = 100):
        self.x = x
        self.y = y
        self.health = health
        self.spr = None
        self.laserspr = None
        self.lasers = []
        self.cldwncnt = 0

    def shoot(self):
        if self.cldwncnt == 0:
            laser = Laser(self.x, self.y, self.laserspr)
            self.lasers.append(laser)
            self.cldwncnt = 1
            if self.y >= 500:
                laser2 = Laser(self.x + 80, self.y, self.laserspr)
                self.lasers.append(laser2)

                bsound = mixer.Sound("bullet.wav")
                bsound.play()


    def cooldown(self):
        if self.cldwncnt >= self.COOLDOWN:
            self.cldwncnt = 0
        elif self.cldwncnt > 0:
            self.cldwncnt += 1
    def get_width(self):
        return self.spr.get_width()

    def get_height(self):
        return self.spr.get_height()

    def draw(self, window):
        window.blit(self.spr, (self.x, self.y))
        for laser in self.lasers:
            laser.draw(window)

    def movel(self, spd, obj):
        self.cooldown()
        for laser in self.lasers:
            laser.move(spd)
            if laser.ofscr(750):
                self.lasers.remove(laser)
            elif laser.coll(obj):
                obj.health -= 20
                hurt = mixer.Sound("hurt.wav")
                hurt.play()
                self.lasers.remove(laser)

class Player(Robot):
    def __init__(self, x, y, health = 100):
        super().__init__(x, y, health)
        self.spr = frame1
        self.laserspr = rocket
        self.mask = pygame.mask.from_surface(self.spr)
        self.maxhealth = health

    def movel(self, spd, objs):
        self.cooldown()
        bsound = mixer.Sound("bullet.wav")
        for laser in self.lasers:
            laser.move(spd)
            if laser.ofscr(750):
                self.lasers.remove(laser)
            else:
                for obj in objs:
                    if laser.coll(obj):
                        esound = mixer.Sound("expl.wav")
                        esound.play()
                        objs.remove(obj)
                        self.lasers.remove(laser)

    def healthbar(self, window):
        pygame.draw.rect(window, (255, 0, 0), (self.x, self.y + self.spr.get_height() + 10, self.spr.get_width(), 10))
        pygame.draw.rect(window, (0, 255, 0), (self.x, self.y + self.spr.get_height() + 10, (self.spr.get_width() * ((self.health / self.maxhealth))), 10))

    def draw(self, window):
        super().draw(window)
        self.healthbar(window)

class Enemy(Robot):
    COLOR_MAP = {
        "red": (ufor, laser),
        "green": (ufo, laserg),
        "yellow": (ufoy, lasery)
    }

    def __init__(self, x, y, color,  health=100):
        super().__init__(x, y , health)
        self.spr, self.laserspr = self.COLOR_MAP[color]
        self.mask = pygame.mask.from_surface(self.spr)

    def move(self, spd):
        self.y += spd

def game():
    over = False
    overcnt = 0
    width = 750
    height = 750
    FPS = 60
    clock = pygame.time.Clock()
    screen = pygame.display.set_mode((width, height))
    mixer.music.load("background.wav")
    mixer.music.play(-1)
    level = 0
    lives = 3
    font1 = pygame.font.Font('04B_30__.ttf', 32)
    font2 = pygame.font.Font('04B_30__.ttf', 64)
    font3 = pygame.font.Font('04B_30__.ttf', 18)
    pspd = 5
    player = Player(300, 500)

    lspd = 7

    enemies = []
    wlenght = 0
    espd = 1

    def redrawin():
        screen.blit(backgr, (0, 0))

        liveslabel = font1.render(f"Lives: {lives}", True, (255, 255, 255))
        levellabel = font1.render(f"Level: {level}", True, (255, 255, 255))

        screen.blit(liveslabel, (10, 10))
        screen.blit(levellabel, (width - levellabel.get_width() - 10, 10))

        for enemy in enemies:
            enemy.draw(screen)

        player.draw(screen)

        if over:
            lostlabel = font2.render("Game Over", True, (255, 255, 255))
            screen.blit(lostlabel, (width / 2 - lostlabel.get_width() / 2, 350))

        pygame.display.update()

    run = True
    while run:
        clock.tick(FPS)
        redrawin()

        if lives <= 0:
            over = True
            overcnt += 1
            
        if player.health <= 0 and lives > 0:
            lives -= 1
            player.health = 100

        if over:
            if overcnt > FPS * 3:
                run = False
                pygame.mixer.music.stop()
            else:
                continue

        if len(enemies) == 0:
            level += 1
            wlenght += 5
            if player.health + 30 > player.maxhealth:
                player.health = player.maxhealth
            else:
                player.health += 30
            for i in range(wlenght):
                enemy = Enemy(random.randrange(50, width - 100), random.randrange(-1500, -100), random.choice(["red", "yellow", "green"]))
                enemies.append(enemy)

        for enemy in enemies[:]:
            enemy.movel(lspd, player)
            enemy.move(espd)

            if random.randrange(0, 2*60) == 1:
                enemy.shoot()
                if enemy.y > 0:
                    lsound = mixer.Sound("laser.wav")
                    lsound.play()


            if collide(enemy, player):
                player.health -= 10
                hurt = mixer.Sound("hurt.wav")
                hurt.play()
                enemies.remove(enemy)
            elif enemy.y + enemy.get_height() > height:
                lives -= 1
                enemies.remove(enemy)
                hurt = mixer.Sound("hurt.wav")
                hurt.play()

        player.movel(-lspd, enemies)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
        keys = pygame.key.get_pressed()
        if keys[pygame.K_RIGHT] and player.x + player.get_width() < width:
            player.x += pspd
        if keys[pygame.K_LEFT] and player.x > 0:
            player.x -= pspd
        if keys[pygame.K_SPACE]:
            player.shoot()
        if keys[pygame.K_ESCAPE]:
            run = False
            pygame.mixer.music.stop()

def get_font(size): # Returns Press-Start-2P in the desired size
    return pygame.font.Font("04B_30__.ttf", size)

def main_menu():
    screen = pygame.display.set_mode((750, 750))
    while True:
        screen.blit(menubck, (0, 0))

        MENU_MOUSE_POS = pygame.mouse.get_pos()

        MENU_TEXT = get_font(64).render("MAIN MENU", True, "#b68f40")
        MENU_RECT = MENU_TEXT.get_rect(center=(375, 200))

        PLAY_BUTTON = Button(image=pygame.image.load("Play Rect.png"), pos=(375, 350),
                             text_input="PLAY", font=get_font(32), base_color="#d7fcd4", hovering_color="White")
        QUIT_BUTTON = Button(image=pygame.image.load("Play Rect.png"), pos=(375, 500),
                             text_input="QUIT", font=get_font(32), base_color="#d7fcd4", hovering_color="White")

        screen.blit(MENU_TEXT, MENU_RECT)

        for button in [PLAY_BUTTON, QUIT_BUTTON]:
            button.changeColor(MENU_MOUSE_POS)
            button.update(screen)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.MOUSEBUTTONDOWN:
                if PLAY_BUTTON.checkForInput(MENU_MOUSE_POS):
                    game()
                if QUIT_BUTTON.checkForInput(MENU_MOUSE_POS):
                    pygame.quit()
                    sys.exit()

        pygame.display.update()


main_menu()