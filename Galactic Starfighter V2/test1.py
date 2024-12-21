import pygame
import random
import math

# 初始化 Pygame
pygame.init()

# 设置窗口大小
WIDTH, HEIGHT = 1000, 800
window = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("飞机射击游戏")

# 设置颜色
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)

# 加载图片
player_image = pygame.image.load("player.png")
enemy_image = pygame.image.load("enemy.png")
enemy2_image = pygame.image.load("enemy2.png")  # 新敌人图像
bullet_image = pygame.image.load("bullet.png")
enemybullet_image = pygame.image.load("enemybullet.png")  # 敌人子弹图像
background_image = pygame.image.load("background.png")
kill_image = pygame.image.load("kill.png")  # 加载击毁特效图像
addHP_image = pygame.image.load("addHP.bmp")  # 更改为 addHP.bmp 文件

# 获取原始图像尺寸
player_width, player_height = player_image.get_size()
enemy_width, enemy_height = enemy_image.get_size()
enemy2_width, enemy2_height = enemy2_image.get_size()
bullet_width, bullet_height = bullet_image.get_size()
enemybullet_width, enemybullet_height = enemybullet_image.get_size()
addHP_width, addHP_height = addHP_image.get_size()  # 获取回血道具尺寸
kill_width, kill_height = kill_image.get_size()

# 调整为原尺寸的50%（你可以根据需要调整比例）
scale_factor1 = 0.5
scale_factor2 = 0.5
scale_factor3 = 0.5
scale_factor4 = 1.5
scale_factor5 = 1

# 计算新的尺寸
new_player_size = (int(player_width * scale_factor1), int(player_height * scale_factor1))
new_enemy_size = (int(enemy_width * scale_factor2), int(enemy_height * scale_factor2))
new_enemy2_size = (int(enemy2_width * scale_factor2), int(enemy2_height * scale_factor2))
new_bullet_size = (int(bullet_width * scale_factor3), int(bullet_height * scale_factor3))
new_enemybullet_size = (int(enemybullet_width * scale_factor3), int(enemybullet_height * scale_factor3))
new_addHP_size = (int(addHP_width * scale_factor5), int(addHP_height * scale_factor5))
new_kill_size = (int(kill_width * scale_factor4), int(kill_height * scale_factor4))

# 调整图像大小
player_image = pygame.transform.scale(player_image, new_player_size)
enemy_image = pygame.transform.scale(enemy_image, new_enemy_size)
enemy2_image = pygame.transform.scale(enemy2_image, new_enemy2_size)
bullet_image = pygame.transform.scale(bullet_image, new_bullet_size)
enemybullet_image = pygame.transform.scale(enemybullet_image, new_enemybullet_size)
addHP_image = pygame.transform.scale(addHP_image, new_addHP_size)
kill_image = pygame.transform.scale(kill_image, new_kill_size)

background_image = pygame.transform.scale(background_image, (WIDTH, HEIGHT))

# 飞机类
class Player(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.image = player_image
        self.rect = self.image.get_rect()
        self.rect.center = (WIDTH // 2, HEIGHT - 50)
        self.speed = 5
        self.health = 5
        self.score = 0

    def update(self):
        keys = pygame.key.get_pressed()
        if keys[pygame.K_LEFT] and self.rect.left > 0:
            self.rect.x -= self.speed
        if keys[pygame.K_RIGHT] and self.rect.right < WIDTH:
            self.rect.x += self.speed
        if keys[pygame.K_UP] and self.rect.top > 0:
            self.rect.y -= self.speed
        if keys[pygame.K_DOWN] and self.rect.bottom < HEIGHT:
            self.rect.y += self.speed

    def take_damage(self):
        self.health -= 1
        if self.health < 0:
            self.health = 0

    def heal(self):
        if self.health < 5:
            self.health += 1  # 玩家恢复一点血量，最大血量限制为5

# 敌人类
class Enemy(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.image = enemy_image
        self.rect = self.image.get_rect()
        self.rect.x = random.randint(0, WIDTH - self.rect.width)
        self.rect.y = random.randint(-100, -40)
        self.speed = random.randint(2, 6)

    def update(self):
        self.rect.y += self.speed
        if self.rect.top > HEIGHT:
            self.rect.x = random.randint(0, WIDTH - self.rect.width)
            self.rect.y = random.randint(-100, -40)
            self.speed = random.randint(2, 6)

# 新增敌人类型：能够发射子弹
class Enemy2(Enemy):
    def __init__(self):
        super().__init__()
        self.image = enemy2_image
        self.rect = self.image.get_rect()
        self.rect.x = random.randint(0, WIDTH - self.rect.width)
        self.rect.y = random.randint(-100, -40)
        self.speed = random.randint(2, 6)
        self.shoot_delay = 60  # 每隔60帧发射一次子弹
        self.shoot_timer = self.shoot_delay

    def update(self):
        super().update()
        self.shoot_timer -= 1
        if self.shoot_timer <= 0:
            self.shoot()
            self.shoot_timer = self.shoot_delay

    def shoot(self):
        # 计算玩家与敌人的方向
        player_center = pygame.math.Vector2(WIDTH // 2, HEIGHT - 50)  # 玩家位置
        enemy_center = pygame.math.Vector2(self.rect.centerx, self.rect.centery)
        direction = player_center - enemy_center  # 从敌人到玩家的方向向量
        angle = direction.angle_to(pygame.math.Vector2(1, 0))  # 获取玩家方向

        # 随机偏移角度 [-30, 30] 度
        offset = random.uniform(-30, 30)
        angle += offset  # 将偏移角度应用到原始角度

        # 创建敌人子弹
        bullet = EnemyBullet(self.rect.centerx, self.rect.centery, angle)
        enemy_bullets.add(bullet)  # 将敌人子弹加入敌人子弹组

# 敌人子弹类
class EnemyBullet(pygame.sprite.Sprite):
    def __init__(self, x, y, angle):
        super().__init__()
        self.image = enemybullet_image
        self.rect = self.image.get_rect()
        self.rect.center = (x, y)
        self.speed = 7
        self.angle = math.radians(angle)  # 转换为弧度
        self.dx = self.speed * math.cos(self.angle)
        self.dy = self.speed * math.sin(self.angle)

    def update(self):
        self.rect.x += self.dx
        self.rect.y += self.dy
        if self.rect.top > HEIGHT or self.rect.bottom < 0 or self.rect.left < 0 or self.rect.right > WIDTH:
            self.kill()  # 如果子弹超出屏幕，删除

# 血量道具类
class HPItem(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        self.image = addHP_image
        self.rect = self.image.get_rect()
        self.rect.center = (x, y)
        self.speed_x = random.uniform(-2, 2)  # 道具在水平方向上小幅度随机移动
        self.speed_y = random.uniform(-2, 2)  # 道具在竖直方向上小幅度随机移动

    def update(self):
        # 使道具在周围小幅度随机移动
        self.rect.x += self.speed_x
        self.rect.y += self.speed_y

        # 确保道具不会离开屏幕
        if self.rect.top < 0 or self.rect.bottom > HEIGHT or self.rect.left < 0 or self.rect.right > WIDTH:
            self.kill()  # 如果道具超出屏幕，删除

# 子弹类
class Bullet(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        self.image = bullet_image
        self.rect = self.image.get_rect()
        self.rect.center = (x, y)
        self.speed = -10

    def update(self):
        self.rect.y += self.speed
        if self.rect.bottom < 0:
            self.kill()

# 特效类（敌人被击毁时的爆炸效果）
class Explosion(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        self.image = kill_image
        self.rect = self.image.get_rect()
        self.rect.center = (x, y)
        self.lifetime = 20  # 特效持续的帧数

    def update(self):
        self.lifetime -= 1
        if self.lifetime <= 0:
            self.kill()  # 特效消失

# 创建精灵组
player = Player()
enemies = pygame.sprite.Group()
enemies2 = pygame.sprite.Group()  # 新增敌人类型
bullets = pygame.sprite.Group()
enemy_bullets = pygame.sprite.Group()  # 敌人子弹组
explosions = pygame.sprite.Group()  # 用来存放爆炸特效
hp_items = pygame.sprite.Group()  # 血量道具组

for _ in range(5):
    enemy = Enemy()
    enemies.add(enemy)

for _ in range(2):
    enemy2 = Enemy2()
    enemies2.add(enemy2)

# 设置时钟
clock = pygame.time.Clock()

# 创建字体对象，用于绘制血量和得分文本
font = pygame.font.SysFont("Arial", 30)

# 主循环
running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_SPACE:
                bullet = Bullet(player.rect.centerx, player.rect.top)
                bullets.add(bullet)

    # 更新精灵
    player.update()
    enemies.update()
    enemies2.update()  # 更新敌人2
    bullets.update()
    enemy_bullets.update()  # 更新敌人子弹
    explosions.update()  # 更新特效
    hp_items.update()  # 更新血量道具

    # 碰撞检测：子弹与敌人碰撞
    if pygame.sprite.groupcollide(bullets, enemies, True, True):
        enemy = Enemy()  # 生成新的敌人
        enemies.add(enemy)
        player.score += 1  # 每击毁一个敌人得1分
        explosion = Explosion(enemy.rect.centerx, enemy.rect.centery)  # 创建爆炸特效
        explosions.add(explosion)

        # 50%的概率生成回血道具
        if random.random() < 0.5:
            hp_item = HPItem(enemy.rect.centerx, enemy.rect.centery)
            hp_items.add(hp_item)

    # 碰撞检测：子弹与敌人2碰撞
    if pygame.sprite.groupcollide(bullets, enemies2, True, True):
        enemy2 = Enemy2()  # 生成新的敌人2
        enemies2.add(enemy2)
        player.score += 2  # 每击毁一个敌人2得2分
        explosion = Explosion(enemy2.rect.centerx, enemy2.rect.centery)  # 创建爆炸特效
        explosions.add(explosion)

        # 50%的概率生成回血道具
        if random.random() < 0.5:
            hp_item = HPItem(enemy2.rect.centerx, enemy2.rect.centery)
            hp_items.add(hp_item)

    # 检测玩家与敌人的碰撞
    if pygame.sprite.spritecollide(player, enemies, True):
        player.take_damage()
        if player.health == 0:
            print("游戏结束！")
            running = False  # 游戏结束

    # 检测玩家与敌人2的子弹碰撞
    if pygame.sprite.spritecollide(player, enemy_bullets, True):
        player.take_damage()
        if player.health == 0:
            print("游戏结束！")
            running = False  # 游戏结束

    # 检测玩家与回血道具碰撞
    if pygame.sprite.spritecollide(player, hp_items, True):
        player.heal()  # 恢复玩家血量

    # 绘制背景、玩家、敌人、子弹
    window.blit(background_image, (0, 0))
    window.blit(player.image, player.rect)
    for enemy in enemies:
        window.blit(enemy.image, enemy.rect)
    for enemy2 in enemies2:
        window.blit(enemy2.image, enemy2.rect)
    for bullet in bullets:
        window.blit(bullet.image, bullet.rect)
    for enemy_bullet in enemy_bullets:
        window.blit(enemy_bullet.image, enemy_bullet.rect)
    for hp_item in hp_items:
        window.blit(hp_item.image, hp_item.rect)

    # 绘制玩家血量
    health_text = font.render(f"HP: {player.health}", True, RED)
    window.blit(health_text, (10, 10))  # 将血量文本绘制在左上角

    # 绘制玩家得分
    score_text = font.render(f"SCORE: {player.score}", True, RED)
    window.blit(score_text, (WIDTH - 150, 10))  # 将得分文本绘制在右上角

    # 绘制特效（爆炸）
    for explosion in explosions:
        window.blit(explosion.image, explosion.rect)

    pygame.display.flip()
    clock.tick(60)

pygame.quit()
