import pygame
import random
import math

# 게임 초기화
pygame.init()

# 화면 크기 설정
WIDTH, HEIGHT = 480, 640
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("1945 Game")

# 색상
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)

# 플레이어 전투기 클래스
class Player(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.image = pygame.image.load('player.png').convert_alpha()  # 플레이어 이미지 로드
        self.rect = self.image.get_rect()
        self.rect.centerx = WIDTH // 2
        self.rect.bottom = HEIGHT - 10
        self.speedx = 0
        self.health = 5  # 플레이어의 생명 수정
        self.last_shot = pygame.time.get_ticks()  # 마지막으로 총알을 발사한 시간
        self.shoot_delay = 180  # 연사 딜레이 (밀리초)
        self.invincible = False  # 무적 상태
        self.invincible_time = 2000  # 무적 시간 (2초)
        self.last_hit = 0  # 마지막으로 맞은 시간

    def update(self):
        self.speedx = 0
        keys = pygame.key.get_pressed()
        if keys[pygame.K_LEFT]:
            self.speedx = -5
        if keys[pygame.K_RIGHT]:
            self.speedx = 5
        self.rect.x += self.speedx
        if self.rect.right > WIDTH:
            self.rect.right = WIDTH
        if self.rect.left < 0:
            self.rect.left = 0

        # 무적 상태 해제
        if self.invincible and pygame.time.get_ticks() - self.last_hit > self.invincible_time:
            self.invincible = False

    def shoot(self):
        now = pygame.time.get_ticks()
        if now - self.last_shot > self.shoot_delay:
            self.last_shot = now
            bullet = Bullet(self.rect.centerx, self.rect.top)
            all_sprites.add(bullet)
            bullets.add(bullet)

    def get_hit(self):
        if not self.invincible:
            self.health -= 1
            self.invincible = True
            self.last_hit = pygame.time.get_ticks()

# 적 클래스
class Enemy(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.image = pygame.image.load('enemy.png').convert_alpha()  # 적 이미지 로드
        self.rect = self.image.get_rect()
        self.rect.x = random.randint(0, WIDTH - self.rect.width)
        self.rect.y = random.randint(-100, -40)
        self.speedy = random.randint(1, 8)

    def update(self):
        self.rect.y += self.speedy
        if self.rect.top > HEIGHT + 10:
            self.rect.x = random.randint(0, WIDTH - self.rect.width)
            self.rect.y = random.randint(-100, -40)
            self.speedy = random.randint(1, 8)

# 총알 클래스
class Bullet(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        self.image = pygame.image.load('bullet.png').convert_alpha()  # 총알 이미지 로드
        self.rect = self.image.get_rect()
        self.rect.centerx = x
        self.rect.bottom = y
        self.speedy = -16  # 총알 속도를 약간 빠르게 수정

    def update(self):
        self.rect.y += self.speedy
        if self.rect.bottom < 0:
            self.kill()

# 보스 클래스
class Boss(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.image = pygame.image.load('boss.png').convert_alpha()  # 보스 이미지 로드
        self.rect = self.image.get_rect()
        self.rect.centerx = WIDTH // 2
        self.rect.top = 50
        self.health = 80  # 보스 체력
        self.last_shot = pygame.time.get_ticks()
        self.shoot_delay = 1000  # 1초마다 공격 
        self.move_direction = random.choice([-1, 1])  # 초기 이동 방향 랜덤

    def update(self):
        # 보스는 랜덤하게 좌우로 이동
        self.rect.x += self.move_direction * 2  # 이동 속도

        # 화면 밖으로 나가지 않도록 조정
        if self.rect.left < 0 or self.rect.right > WIDTH:
            self.move_direction *= -1  # 방향 반전

        # 보스는 주기적으로 총알 발사
        now = pygame.time.get_ticks()
        if now - self.last_shot > self.shoot_delay:
            self.last_shot = now
            self.shoot_bullet()

    def shoot_bullet(self):
        # 각도를 15도씩 틀어서 3발 발사
        angles = [75, 90, 105]  # 발사할 각도
        for angle in angles:
            bullet = BossBullet(self.rect.centerx, self.rect.bottom, angle)
            all_sprites.add(bullet)
            boss_bullets.add(bullet)

# 보스의 총알 클래스
class BossBullet(pygame.sprite.Sprite):
    def __init__(self, x, y, angle):
        super().__init__()
        self.image = pygame.image.load('boss_bullet.png').convert_alpha()  # 보스 총알 이미지 로드
        self.rect = self.image.get_rect()
        self.rect.centerx = x
        self.rect.top = y
        self.speed = 7  # 총알 속도
        self.angle = math.radians(angle)  # 각도를 라디안으로 변환
        self.speedx = self.speed * math.cos(self.angle)  # x 방향 속도
        self.speedy = self.speed * math.sin(self.angle)  # y 방향 속도

    def update(self):
        self.rect.x += self.speedx
        self.rect.y += self.speedy
        if self.rect.top > HEIGHT or self.rect.left < 0 or self.rect.right > WIDTH:
            self.kill()

# 스프라이트 그룹 설정
all_sprites = pygame.sprite.Group()
enemies = pygame.sprite.Group()
bullets = pygame.sprite.Group()
boss_bullets = pygame.sprite.Group()

player = Player()
all_sprites.add(player)

for i in range(8):
    enemy = Enemy()
    all_sprites.add(enemy)
    enemies.add(enemy)

# 보스 변수
boss = None
boss_spawned = False

# 점수 시스템
score = 0

# 게임 상태
game_over = False
game_clear = False

# 게임 루프
running = True
clock = pygame.time.Clock()

while running:
    # 게임 속도 조절 (FPS)
    clock.tick(60)

    # 이벤트 처리
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    # 스페이스바 꾹 누르면 연사
    keys = pygame.key.get_pressed()
    if keys[pygame.K_SPACE]:
        player.shoot()

    # 게임 업데이트
    all_sprites.update()

    # 보스가 없고, 점수가 500점 이상이면 보스 생성
    if score >= 500 and not boss_spawned:
        boss = Boss()
        all_sprites.add(boss)
        boss_spawned = True
        # 기존 적들을 제거
        for enemy in enemies:
            enemy.kill()

    # 총알과 적 충돌 처리
    if not boss_spawned:
        hits = pygame.sprite.groupcollide(enemies, bullets, True, True)
        for hit in hits:
            score += 10  # 적 처치 시 10점 추가
            enemy = Enemy()
            all_sprites.add(enemy)
            enemies.add(enemy)

    # 총알과 보스 충돌 처리
    if boss_spawned:
        hits = pygame.sprite.spritecollide(boss, bullets, True)
        for hit in hits:
            boss.health -= 1  # 보스 체력 감소
            if boss.health <= 0:
                boss.kill()  # 보스를 처치하면 게임 종료
                game_clear = True  # 게임 클리어 상태 변경

    # 적과 플레이어 충돌 처리
    hits = pygame.sprite.spritecollide(player, enemies, False)
    if hits and not player.invincible:
        player.get_hit()  # 플레이어가 맞으면 무적 시간 발동
        if player.health <= 0:
            game_over = True  # 게임 오버 상태 변경

    # 보스 총알과 플레이어 충돌 처리
    if boss_spawned:
        hits = pygame.sprite.spritecollide(player, boss_bullets, True)
        if hits and not player.invincible:
            player.get_hit()  # 보스의 총알에 맞았을 때
            if player.health <= 0:
                game_over = True  # 게임 오버 상태 변경

    # 화면 업데이트
    screen.fill(BLACK)
    all_sprites.draw(screen)

    # 점수 및 생명 표시
    font = pygame.font.SysFont(None, 36)
    score_text = font.render(f"Score: {score}", True, WHITE)
    health_text = font.render(f"Health: {player.health}", True, WHITE)
    screen.blit(score_text, (10, 10))
    screen.blit(health_text, (10, 40))

    if boss_spawned:
        boss_health_text = font.render(f"Boss Health: {boss.health}", True, WHITE)
        screen.blit(boss_health_text, (WIDTH // 2 - 50, 50))  # 보스 체력을 플레이어 체력 아래로 이동

    # 게임 종료 메시지
    if game_over:
        game_over_text = font.render("GAME OVER!", True, WHITE)
        screen.blit(game_over_text, (WIDTH // 2 - 70, HEIGHT // 2))
        pygame.display.flip()
        pygame.time.delay(2000)  # 2초 대기
        running = False  # 게임 종료

    if game_clear:
        clear_text = font.render("GAME CLEAR!", True, WHITE)
        screen.blit(clear_text, (WIDTH // 2 - 70, HEIGHT // 2))
        pygame.display.flip()
        pygame.time.delay(2000)  # 2초 대기
        running = False  # 게임 종료

    pygame.display.flip()

pygame.quit()
