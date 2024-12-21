import pygame
import random
import math

# 初始化 Pygame
pygame.init()

# 设置窗口大小
WIDTH, HEIGHT = 1000, 800
window = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("飞机射击游戏")
player_position = [WIDTH / 2, HEIGHT / 2]

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
scale_factor5 = 0.5

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
        self.alive = True  # 玩家是否存活
        global player_position
        player_position = self.rect.center

    def update(self):
        if not self.alive:  # 如果玩家已死亡，停止移动
            return
        pygame.key.stop_text_input()  # 重点在这
        keys = pygame.key.get_pressed()

        # 使用 WASD 键进行移动
        if keys[pygame.K_a] or keys[pygame.K_LEFT]:  # 向左移动
            if self.rect.left > 0:
                self.rect.x -= self.speed
        if keys[pygame.K_d] or keys[pygame.K_RIGHT]:  # 向右移动
            if self.rect.right < WIDTH:
                self.rect.x += self.speed
        if keys[pygame.K_w] or keys[pygame.K_UP]:  # 向上移动
            if self.rect.top > 0:
                self.rect.y -= self.speed
        if keys[pygame.K_s] or keys[pygame.K_DOWN]:  # 向下移动
            if self.rect.bottom < HEIGHT:
                self.rect.y += self.speed
        global player_position
        player_position = self.rect.center
        # print(player_position)

    def take_damage(self):
        self.health -= 1
        if self.health <= 0:
            self.health = 0
            self.alive = False  # 玩家死亡

    def heal(self):
        if self.health < 10:
            self.health += 1  # 玩家恢复一点血量，最大血量限制为10

    def get_position(self):
        """
        返回玩家飞机的当前位置，通常是rect的中心位置。
        :return: (x, y) 玩家当前位置
        """
        return self.rect.center  # 你也可以使用self.rect.topleft返回左上角坐标


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
        self.shoot_delay = 50  # 每隔60帧发射一次子弹
        self.shoot_timer = self.shoot_delay

    def update(self):
        super().update()
        self.shoot_timer -= 1
        if self.shoot_timer <= 0:
            self.shoot()
            self.shoot_timer = self.shoot_delay

    def shoot(self):
        # 计算玩家与敌人的方向
        global player_position
        # print("player:", player_position)
        player_center = pygame.math.Vector2(player_position)  # 玩家位置
        enemy_center = pygame.math.Vector2(self.rect.centerx, self.rect.centery)
        # print("enemy:", enemy_center)
        direction = player_center - enemy_center  # 从敌人到玩家的方向向量
        # print("direction:", direction)
        angle = - direction.angle_to(pygame.math.Vector2(1, 0))  # 获取玩家方向

        # 随机偏移角度 [-30, 30] 度
        offset = random.uniform(-10, 10)
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
        self.speed = 8
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
    def __init__(self, x, y, lifespan=5000):

        super().__init__()
        self.image = addHP_image
        self.rect = self.image.get_rect()
        self.rect.center = (x, y)
        self.speed_x = random.uniform(-1, 1)  # 道具在水平方向上小幅度随机移动
        self.speed_y = random.uniform(-1, 1)  # 道具在竖直方向上小幅度随机移动
        self.lifespan = lifespan  # 道具的生存时间(毫秒)
        self.spawn_time = pygame.time.get_ticks()  # 记录道具的生成时间

    def update(self):
        # 使道具在周围小幅度随机移动
        self.rect.x += self.speed_x
        self.rect.y += self.speed_y

        # 确保道具不会离开屏幕
        if self.rect.top < 0 or self.rect.bottom > HEIGHT or self.rect.left < 0 or self.rect.right > WIDTH:
            self.kill()  # 如果道具超出屏幕，删除
            # 检查道具是否已经过期（超过最大生存时间）
            current_time = pygame.time.get_ticks()
            if current_time - self.spawn_time > self.lifespan:
                self.kill()  # 删除道具


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
        self.animation_frames = 25  # 设置动画帧数
        self.current_frame = 0  # 当前帧数
        self.animation_speed = 5  # 控制爆炸动画播放速度

    def update(self):
        self.current_frame += 1
        if self.current_frame >= self.animation_frames:
            self.kill()  # 动画结束后移除爆炸特效


# 游戏初始化
player = Player()
enemies = pygame.sprite.Group()
enemies2 = pygame.sprite.Group()
bullets = pygame.sprite.Group()
enemy_bullets = pygame.sprite.Group()
explosions = pygame.sprite.Group()
hp_items = pygame.sprite.Group()

# 设置时钟
clock = pygame.time.Clock()

# 创建字体对象，用于绘制血量和得分文本
font = pygame.font.SysFont("Arial", 30)

# 游戏状态
game_started = False  # 记录游戏是否开始
game_over = False  # 记录游戏是否结束

# 主循环
while True:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            exit()

        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_RETURN:
                if not game_started:
                    game_started = True  # 游戏开始
                elif game_over:
                    # 游戏结束后重新开始
                    game_over = False
                    player = Player()
                    enemies.empty()
                    enemies2.empty()
                    bullets.empty()
                    enemy_bullets.empty()
                    explosions.empty()
                    hp_items.empty()

            if event.key == pygame.K_SPACE and game_started and not game_over:
                bullet = Bullet(player.rect.centerx, player.rect.top)
                bullets.add(bullet)

    # 如果游戏已经开始且没有结束，生成敌人
    if game_started and not game_over:
        if len(enemies) < 4:
            enemy = Enemy()
            enemies.add(enemy)
        if len(enemies2) < 2:
            enemy2 = Enemy2()
            enemies2.add(enemy2)

    # 更新精灵
    player.update()
    enemies.update()
    enemies2.update()  # 更新敌人2
    bullets.update()
    enemy_bullets.update()  # 更新敌人子弹
    explosions.update()  # 更新特效
    hp_items.update()  # 更新血量道具

    # 碰撞检测：子弹与敌人实例碰撞
    for bullet in bullets.sprites():
        for enemy in enemies:
            if pygame.sprite.collide_rect(enemy, bullet):  # 检查每个敌人与子弹的碰撞

                bullet.kill()  # 摧毁子弹
                player.score += 1  # 每击毁一个敌人得1分
                explosion = Explosion(enemy.rect.centerx, enemy.rect.centery)  # 创建爆炸特效
                explosions.add(explosion)

                # 30%的概率生成回血道具
                if random.random() < 0.3:
                    hp_item = HPItem(enemy.rect.centerx, enemy.rect.centery)
                    hp_items.add(hp_item)
                enemy.kill()  # 摧毁敌人
                # 生成新的敌人
                new_enemy = Enemy()  # 生成新的敌人实例
                enemies.add(new_enemy)

    for bullet in bullets.sprites():
        # 碰撞检测：子弹与敌人2实例碰撞
        for enemy2 in enemies2:
            if pygame.sprite.collide_rect(enemy2, bullet):  # 检查每个敌人2与子弹的碰撞

                bullet.kill()  # 摧毁子弹
                player.score += 2  # 每击毁一个敌人2得2分
                explosion = Explosion(enemy2.rect.centerx, enemy2.rect.centery)  # 创建爆炸特效
                explosions.add(explosion)

                # 50%的概率生成回血道具
                if random.random() < 0.5:
                    hp_item = HPItem(enemy2.rect.centerx, enemy2.rect.centery)
                    hp_items.add(hp_item)
                enemy2.kill()  # 摧毁敌人2
                # 生成新的敌人2
                new_enemy2 = Enemy2()  # 生成新的敌人2实例
                enemies2.add(new_enemy2)

    # 检测玩家与敌人的碰撞
    if pygame.sprite.spritecollide(player, enemies, True):
        player.take_damage()
        if player.health == 0:
            game_over = True  # 游戏结束

    # 检测玩家与敌人2的碰撞
    if pygame.sprite.spritecollide(player, enemies2, True):
        player.take_damage()
        if player.health == 0:
            game_over = True  # 游戏结束

    # 检测玩家与敌人子弹的碰撞
    if pygame.sprite.spritecollide(player, enemy_bullets, True):
        player.take_damage()
        if player.health == 0:
            game_over = True  # 游戏结束

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

    # 设置字体，第二个参数是字体大小
    font = pygame.font.Font(None, 45)  # 使用默认字体，大小为45

    # 绘制玩家血量
    health_text = font.render(f"HP: {player.health}", True, WHITE)
    window.blit(health_text, (10, 10))  # 将血量文本绘制在左上角

    # 绘制玩家得分
    score_text = font.render(f"SCORE: {player.score}", True, WHITE)
    window.blit(score_text, (WIDTH - 200, 10))  # 将得分文本绘制在右上角

    # 绘制特效（爆炸）
    for explosion in explosions:
        window.blit(explosion.image, explosion.rect)

    # 如果游戏结束，显示得分
    if game_over:
        game_over_text = font.render(f"Game Over! Score: {player.score}", True, RED)
        window.blit(game_over_text, (WIDTH // 2 - game_over_text.get_width() // 2, HEIGHT // 2))

    pygame.display.flip()
    clock.tick(60)

pygame.quit()
