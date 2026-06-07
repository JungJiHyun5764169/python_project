import pygame
import random
import sys
import os

os.chdir(os.path.dirname(os.path.abspath(__file__)))

# 1. Pygame 초기화
pygame.init()
pygame.mixer.init()

# 2. 화면 크기 및 설정
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("행소 유물 수호전")

# 색상 정의 (RGB)
BLACK = (0, 0, 0)
BLUE = (50, 150, 255)
GOLD = (255, 215, 0)
RED = (255, 50, 50)

# 이미지 로드 및 크기 조절
background_image = pygame.image.load("startBack.png").convert()
background_image = pygame.transform.scale(background_image, (SCREEN_WIDTH, SCREEN_HEIGHT))

# 플레이 화면 배경 로드 및 비율 유지 스케일링
play_bg_image = pygame.image.load("playBack.png").convert()
play_bg_w, play_bg_h = play_bg_image.get_size()
play_scale = max(SCREEN_WIDTH / play_bg_w, SCREEN_HEIGHT / play_bg_h)
play_bg_image = pygame.transform.scale(play_bg_image, (int(play_bg_w * play_scale), int(play_bg_h * play_scale)))
play_bg_rect = play_bg_image.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2))

# 엔딩 화면 배경 로드 및 비율 유지 스케일링 (에러 방지 적용)
try:
    ending_image = pygame.image.load("ending.png").convert()
    end_bg_w, end_bg_h = ending_image.get_size()
    end_scale = max(SCREEN_WIDTH / end_bg_w, SCREEN_HEIGHT / end_bg_h)
    ending_image = pygame.transform.scale(ending_image, (int(end_bg_w * end_scale), int(end_bg_h * end_scale)))
except FileNotFoundError:
    ending_image = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
ending_rect = ending_image.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2))

# 패배 화면 배경 로드 및 비율 유지 스케일링
try:
    lose_image = pygame.image.load("lose.png").convert()
    lose_bg_w, lose_bg_h = lose_image.get_size()
    lose_scale = max(SCREEN_WIDTH / lose_bg_w, SCREEN_HEIGHT / lose_bg_h)
    lose_image = pygame.transform.scale(lose_image, (int(lose_bg_w * lose_scale), int(lose_bg_h * lose_scale)))
except FileNotFoundError:
    lose_image = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
lose_rect = lose_image.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2))

# 각 라운드 승리 조합에 따른 배경 이미지 로드
ending_bgs = {}
for bg_name in ["round1.png", "round2.png", "round3.png", "round12.png", "round13.png", "round23.png"]:
    try:
        img = pygame.image.load(bg_name).convert()
        w, h = img.get_size()
        scale = max(SCREEN_WIDTH / w, SCREEN_HEIGHT / h)
        ending_bgs[bg_name] = pygame.transform.scale(img, (int(w * scale), int(h * scale)))
    except FileNotFoundError:
        ending_bgs[bg_name] = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))

# 엔딩 유물 설명 이미지 로드 및 위치 매핑
ending_info_images = {}
ending_image_mapping = {
    0: "ending7.png", 1: "ending8.png", 2: "ending9.png", # 상단 (좌, 중, 우)
    3: "ending6.png", 4: "ending4.png", 5: "ending5.png", # 중단 (좌, 중, 우)
    6: "ending3.png", 7: "ending1.png", 8: "ending2.png"  # 하단 (좌, 중, 우)
}
for idx, filename in ending_image_mapping.items():
    try:
        info_img = pygame.image.load(filename).convert_alpha()
        info_w, info_h = info_img.get_size()
        target_w = 640  # 화면 중앙에 크게 띄우기 위해 크기 확대
        target_h = int(info_h * (target_w / info_w))
        ending_info_images[idx] = pygame.transform.scale(info_img, (target_w, target_h))
    except FileNotFoundError:
        pass

# 페이드 효과를 위한 알파값 및 위치 저장 딕셔너리
ending_alphas = {i: 0 for i in range(9)}
ending_positions = {i: (0, 0) for i in range(9)}

# 9개의 유물 전시 위치 (화면 중앙 기준 대략적인 3x3 격자 좌표 설정)
ending_hover_rects = [
    pygame.Rect(180, 140, 100, 110), pygame.Rect(350, 140, 100, 110), pygame.Rect(520, 140, 100, 110), # 상단 3개
    pygame.Rect(180, 310, 100, 110), pygame.Rect(350, 310, 100, 110), pygame.Rect(520, 310, 100, 110), # 중단 3개
    pygame.Rect(180, 460, 100, 110), pygame.Rect(350, 460, 100, 110), pygame.Rect(520, 460, 100, 110)  # 하단 3개
]
selected_artifact_idx = 6 # 엔딩씬 진입 시 좌측 하단 기본 선택

start_btn_base = pygame.image.load("startButton.png").convert_alpha()
start_btn_small = pygame.transform.scale(start_btn_base, (240, 50))
start_btn_large = pygame.transform.scale(start_btn_base, (260, 55))

sound_btn_base = pygame.image.load("soundButton.png").convert_alpha()
sound_btn_small = pygame.transform.scale(sound_btn_base, (240, 50))
sound_btn_large = pygame.transform.scale(sound_btn_base, (260, 55))

check_btn_base = pygame.image.load("checkButton.png").convert_alpha()
check_btn_small = pygame.transform.scale(check_btn_base, (300, 60))
check_btn_large = pygame.transform.scale(check_btn_base, (320, 65))

replay_btn_base = pygame.image.load("replayButton.png").convert_alpha()
replay_btn_small = pygame.transform.scale(replay_btn_base, (300, 60))
replay_btn_large = pygame.transform.scale(replay_btn_base, (320, 65))

# 엔딩 화면용 작은 종료 버튼 추가
end_btn_base = pygame.image.load("endButton.png").convert_alpha()
end_btn_ending_small = pygame.transform.scale(end_btn_base, (180, 40))
end_btn_ending_large = pygame.transform.scale(end_btn_base, (200, 45))

# 도둑 이미지 로드 및 크기 조절
thief_image = pygame.image.load("thief.png").convert_alpha()
img_w, img_h = thief_image.get_size()
thief_target_h = 120
thief_target_w = int(img_w * (thief_target_h / img_h))  # 원본 이미지 비율 유지
thief_image = pygame.transform.scale(thief_image, (thief_target_w, thief_target_h))

# 플레이어 이미지 로드 및 크기 조절
player_image = pygame.image.load("player.png").convert_alpha()
p_img_w, p_img_h = player_image.get_size()
player_target_w = int(p_img_w * (thief_target_h / p_img_h))
player_image = pygame.transform.scale(player_image, (player_target_w, thief_target_h))

# FPS 제어를 위한 Clock 객체
clock = pygame.time.Clock()

# 3. 플레이어(큐레이터) 사각형 설정
player_width = 40  # 도둑과 동일한 콜라이더 너비로 수정
player_height = 30 # 도둑과 동일한 콜라이더 높이로 수정
player_x = (SCREEN_WIDTH - player_width) // 2
player_y = SCREEN_HEIGHT - player_height - 20
player_speed = 7
player_rect = pygame.Rect(player_x, player_y, player_width, player_height)

# AI 도둑 사각형 설정
thief_width = 40   # 자루 부분 너비 콜라이더 (기존 80에서 절반으로 축소)
thief_height = 30  # 자루 부분 높이 콜라이더 (기존 60에서 절반으로 축소)
thief_x = random.randint(0, SCREEN_WIDTH - thief_width)
thief_y = SCREEN_HEIGHT - thief_height - 20
thief_rect = pygame.Rect(thief_x, thief_y, thief_width, thief_height)

# 라운드 설정
current_round = 1
max_rounds = 3
round_duration = 20000  # 라운드 제한 시간 (20초)
ai_initial_speeds = [4, 6, 8]  # 라운드별 AI 도둑 초기 속도 (점점 빨라짐)
thief_speed = ai_initial_speeds[0]
game_state = "START_SCREEN"  # 게임 상태 관리 (START_SCREEN, PLAYING, ROUND_OVER, GAME_OVER)
selected_button_idx = 0  # 0: 시작 버튼, 1: 종료 버튼 (마우스/키보드 선택용)
round_over_time = 0
round_start_timer = 0
round_start_time = pygame.time.get_ticks()
remaining_time = 20
countdown_sec = -1
total_player_wins = 0
total_ai_wins = 0
player_won_rounds = []

# 4. 유물(Artifact) 이미지 로드 및 설정
loaded_artifacts = {1: [], 2: [], 3: []}
for rnd, img_paths in [
    (1, ["obj1.png", "obj2.png", "obj3.png"]),
    (2, ["obj4.png", "obj5.png", "obj6.png"]),
    (3, ["obj7.png", "obj8.png", "obj9.png"])
]:
    for img_path in img_paths:
        try:
            img = pygame.image.load(img_path).convert_alpha()
            img_w, img_h = img.get_size()
            target_h = 40  # 화면 비율에 맞게 유물 이미지 높이를 40으로 조절
            target_w = int(img_w * (target_h / img_h))
            img = pygame.transform.scale(img, (target_w, target_h))
            loaded_artifacts[rnd].append(img)
        except FileNotFoundError:
            # 이미지가 폴더에 없을 경우 에러 방지용 임시 이미지(금색 사각형) 생성
            temp_img = pygame.Surface((30, 40))
            temp_img.fill(GOLD)
            loaded_artifacts[rnd].append(temp_img)

artifacts = []  # 유물들을 관리할 리스트
artifact_speed = 5

# 유물 생성 타이머 설정 (1초 = 1000ms 간격)
SPAWN_ARTIFACT = pygame.USEREVENT + 1
spawn_interval = 1000
pygame.time.set_timer(SPAWN_ARTIFACT, spawn_interval)

# 점수 및 폰트 설정
score = 0
ai_score = 0
font = pygame.font.Font("국립박물관문화재단클래식M.ttf", 36)
ui_font = pygame.font.Font("국립박물관문화재단클래식M.ttf", 26)
round_font = pygame.font.Font("국립박물관문화재단클래식M.ttf", 18)
settings_font = pygame.font.Font("국립박물관문화재단클래식M.ttf", 20)
settings_title_font = pygame.font.Font("국립박물관문화재단클래식M.ttf", 28)

# 설정 및 일시정지 관련 변수
show_settings = False
pause_start_time = 0
volumes = {"master": 1.0, "bgm": 1.0, "sfx": 1.0}
dragging_slider = None
slider_rects = {
    "master": pygame.Rect(340, 240, 150, 20),
    "bgm": pygame.Rect(340, 300, 150, 20),
    "sfx": pygame.Rect(340, 360, 150, 20)
}

# 사운드 효과 및 배경음악 로드
try:
    get_sfx = pygame.mixer.Sound("get.mp3")
except:
    get_sfx = None
try:
    clear_sfx = pygame.mixer.Sound("clear.mp3")
except:
    clear_sfx = None
try:
    choice_sfx = pygame.mixer.Sound("choice.mp3")
except:
    choice_sfx = None
try:
    number_sfx = pygame.mixer.Sound("number.mp3")
except:
    number_sfx = None

def play_sfx(sfx):
    if sfx:
        sfx.set_volume(volumes["master"] * volumes["sfx"])
        sfx.play()

current_bgm = None
def update_bgm(state):
    global current_bgm
    target_bgm = None
    if state == "START_SCREEN":
        target_bgm = "title.wav"
    elif state in ["ROUND_START", "PLAYING", "ROUND_OVER"]:
        target_bgm = "play.mp3"
    elif state in ["GAME_OVER", "ENDING_SCREEN"]:
        if len(set(player_won_rounds)) == 3:
            target_bgm = "ending.mp3"
        else:
            target_bgm = "lose.mp3"
        
    if target_bgm and current_bgm != target_bgm:
        try:
            pygame.mixer.music.load(target_bgm)
            pygame.mixer.music.play(-1)
            current_bgm = target_bgm
        except:
            current_bgm = target_bgm
            
    pygame.mixer.music.set_volume(volumes["master"] * volumes["bgm"])

# 난이도 증가 타이머 설정 (10초 = 10000ms 간격)
INCREASE_DIFFICULTY = pygame.USEREVENT + 2
pygame.time.set_timer(INCREASE_DIFFICULTY, 10000)

def is_artifact_available(idx):
    if idx in [6, 7, 8] and 1 in player_won_rounds: return True
    if idx in [3, 4, 5] and 2 in player_won_rounds: return True
    if idx in [0, 1, 2] and 3 in player_won_rounds: return True
    return False

# 5. 게임 메인 루프
running = True
while running:
    update_bgm(game_state)
    
    prev_btn_idx = selected_button_idx
    prev_art_idx = selected_artifact_idx

    # 이벤트 처리
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
            
        # ESC 키 처리: 설정창 토글 및 게임 일시정지
        elif event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
            if show_settings:
                show_settings = False
                dragging_slider = None
                # 정지되었던 시간만큼 타이머 보정
                paused_duration = pygame.time.get_ticks() - pause_start_time
                round_start_time += paused_duration
                round_over_time += paused_duration
                round_start_timer += paused_duration
                # 타이머 재개
                if game_state in ["PLAYING", "ROUND_START"]:
                    pygame.time.set_timer(SPAWN_ARTIFACT, spawn_interval)
                    pygame.time.set_timer(INCREASE_DIFFICULTY, 10000)
            else:
                show_settings = True
                pause_start_time = pygame.time.get_ticks()
                # 유물 생성 및 난이도 증가 타이머 정지
                pygame.time.set_timer(SPAWN_ARTIFACT, 0)
                pygame.time.set_timer(INCREASE_DIFFICULTY, 0)
            continue

        # 설정창이 열려있을 때의 마우스 이벤트 처리
        if show_settings:
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                settings_rect = pygame.Rect(SCREEN_WIDTH//2 - 200, SCREEN_HEIGHT//2 - 150, 400, 300)
                # 설정창 바깥 영역을 클릭했을 경우 설정창 닫기 (ESC와 동일한 로직)
                if not settings_rect.collidepoint(event.pos):
                    show_settings = False
                    dragging_slider = None
                    paused_duration = pygame.time.get_ticks() - pause_start_time
                    round_start_time += paused_duration
                    round_over_time += paused_duration
                    round_start_timer += paused_duration
                    if game_state in ["PLAYING", "ROUND_START"]:
                        pygame.time.set_timer(SPAWN_ARTIFACT, spawn_interval)
                        pygame.time.set_timer(INCREASE_DIFFICULTY, 10000)
                else:
                    for key, rect in slider_rects.items():
                        hitbox = pygame.Rect(rect.x - 10, rect.y - 15, rect.width + 20, rect.height + 30)
                        if hitbox.collidepoint(event.pos):
                            dragging_slider = key
                            rel_x = max(0, min(event.pos[0] - rect.x, rect.width))
                            volumes[key] = rel_x / rect.width
            elif event.type == pygame.MOUSEBUTTONUP and event.button == 1:
                dragging_slider = None
            elif event.type == pygame.MOUSEMOTION:
                if dragging_slider:
                    rect = slider_rects[dragging_slider]
                    rel_x = max(0, min(event.pos[0] - rect.x, rect.width))
                    volumes[dragging_slider] = rel_x / rect.width
            continue  # 설정창 켜진 상태에서는 하단 게임 이벤트 무시

        elif event.type == SPAWN_ARTIFACT and game_state == "PLAYING":
            # 라운드에 맞는 유물 이미지 중 무작위 선택하여 생성
            chosen_img = random.choice(loaded_artifacts[current_round])
            img_w, img_h = chosen_img.get_size()
            artifact_x = random.randint(0, SCREEN_WIDTH - img_w)
            new_artifact_rect = pygame.Rect(artifact_x, -img_h, img_w, img_h)
            artifacts.append({"rect": new_artifact_rect, "image": chosen_img})
        elif event.type == INCREASE_DIFFICULTY and game_state == "PLAYING":
            # 난이도 상승: 생성 빈도 단축, 유물 속도 증가, 도둑 속도 증가
            if spawn_interval > 200:
                spawn_interval -= 100
                pygame.time.set_timer(SPAWN_ARTIFACT, spawn_interval)
            artifact_speed += 1
            thief_speed += 1
        elif event.type == pygame.KEYDOWN:
            if game_state == "START_SCREEN":
                if event.key == pygame.K_UP:
                    selected_button_idx = max(0, selected_button_idx - 1)
                elif event.key == pygame.K_DOWN:
                    selected_button_idx = min(1, selected_button_idx + 1)
                elif event.key == pygame.K_RETURN or event.key == pygame.K_KP_ENTER:
                    play_sfx(choice_sfx)
                    if selected_button_idx == 0:
                        game_state = "ROUND_START"
                        round_start_timer = pygame.time.get_ticks()
                        countdown_sec = -1
                        total_player_wins = 0
                        total_ai_wins = 0
                        player_won_rounds.clear()
                    elif selected_button_idx == 1:
                        show_settings = True
                        pause_start_time = pygame.time.get_ticks()
            elif game_state == "GAME_OVER":
                if event.key == pygame.K_UP:
                    selected_button_idx = max(0, selected_button_idx - 1)
                elif event.key == pygame.K_DOWN:
                    selected_button_idx = min(1, selected_button_idx + 1)
                elif event.key == pygame.K_RETURN or event.key == pygame.K_KP_ENTER:
                    play_sfx(choice_sfx)
                    if selected_button_idx == 0:
                        game_state = "ENDING_SCREEN"
                        avail = [i for i in [6,7,8, 3,4,5, 0,1,2] if is_artifact_available(i)]
                        selected_artifact_idx = avail[0] if avail else -1
                        prev_art_idx = selected_artifact_idx
                        selected_button_idx = -1
                    elif selected_button_idx == 1:
                        game_state = "START_SCREEN"
                        current_round = 1
                        score = 0
                        ai_score = 0
                        artifacts.clear()
                        selected_button_idx = 0
                        prev_btn_idx = 0
                        total_player_wins = 0
                        total_ai_wins = 0
                        player_won_rounds.clear()
            elif game_state == "ENDING_SCREEN":
                if len(set(player_won_rounds)) > 0:
                    if event.key == pygame.K_UP:
                        for step in [3, 6]:
                            if selected_artifact_idx - step >= 0 and is_artifact_available(selected_artifact_idx - step):
                                selected_artifact_idx -= step
                                break
                    elif event.key == pygame.K_DOWN:
                        for step in [3, 6]:
                            if selected_artifact_idx + step <= 8 and is_artifact_available(selected_artifact_idx + step):
                                selected_artifact_idx += step
                                break
                    elif event.key == pygame.K_LEFT:
                        row_start = (selected_artifact_idx // 3) * 3
                        if selected_artifact_idx - 1 >= row_start and is_artifact_available(selected_artifact_idx - 1):
                            selected_artifact_idx -= 1
                    elif event.key == pygame.K_RIGHT:
                        row_end = (selected_artifact_idx // 3) * 3 + 2
                        if selected_artifact_idx + 1 <= row_end and is_artifact_available(selected_artifact_idx + 1):
                            selected_artifact_idx += 1
        elif event.type == pygame.MOUSEMOTION:
            if game_state == "START_SCREEN":
                rect_start = start_btn_large.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT - 150))
                rect_sound = sound_btn_large.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT - 80))
                if rect_start.collidepoint(event.pos):
                    selected_button_idx = 0
                elif rect_sound.collidepoint(event.pos):
                    selected_button_idx = 1
            elif game_state == "GAME_OVER":
                rect_check = check_btn_large.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 - 40))
                rect_replay = replay_btn_large.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 40))
                if rect_check.collidepoint(event.pos):
                    selected_button_idx = 0
                elif rect_replay.collidepoint(event.pos):
                    selected_button_idx = 1
            elif game_state == "ENDING_SCREEN":
                end_btn_rect = end_btn_ending_small.get_rect(bottomright=(SCREEN_WIDTH - 20, SCREEN_HEIGHT - 20))
                if end_btn_rect.collidepoint(event.pos):
                    selected_button_idx = 1
                    selected_artifact_idx = -1
                else:
                    if selected_button_idx == 1:
                        selected_button_idx = -1
                    if len(set(player_won_rounds)) > 0:
                        hovered_any = False
                        for i, rect in enumerate(ending_hover_rects):
                            if rect.collidepoint(event.pos) and is_artifact_available(i):
                                selected_artifact_idx = i
                                hovered_any = True
                                break
                        if not hovered_any:
                            selected_artifact_idx = -1
        elif event.type == pygame.MOUSEBUTTONDOWN:
            if game_state == "START_SCREEN":
                rect_start = start_btn_large.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT - 150))
                rect_sound = sound_btn_large.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT - 80))
                if rect_start.collidepoint(event.pos):
                    play_sfx(choice_sfx)
                    game_state = "ROUND_START"
                    round_start_timer = pygame.time.get_ticks()
                    countdown_sec = -1
                    total_player_wins = 0
                    total_ai_wins = 0
                    player_won_rounds.clear()
                elif rect_sound.collidepoint(event.pos):
                    play_sfx(choice_sfx)
                    show_settings = True
                    pause_start_time = pygame.time.get_ticks()
            elif game_state == "GAME_OVER":
                rect_check = check_btn_large.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 - 40))
                rect_replay = replay_btn_large.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 40))
                if rect_check.collidepoint(event.pos):
                    play_sfx(choice_sfx)
                    game_state = "ENDING_SCREEN"
                    avail = [i for i in [6,7,8, 3,4,5, 0,1,2] if is_artifact_available(i)]
                    selected_artifact_idx = avail[0] if avail else -1
                    prev_art_idx = selected_artifact_idx
                    selected_button_idx = -1
                elif rect_replay.collidepoint(event.pos):
                    play_sfx(choice_sfx)
                    game_state = "START_SCREEN"
                    current_round = 1
                    score = 0
                    ai_score = 0
                    artifacts.clear()
                    selected_button_idx = 0
                    prev_btn_idx = 0
                    total_player_wins = 0
                    total_ai_wins = 0
                    player_won_rounds.clear()
            elif game_state == "ENDING_SCREEN":
                end_btn_img = end_btn_ending_large if selected_button_idx == 1 else end_btn_ending_small
                end_btn_rect = end_btn_img.get_rect(bottomright=(SCREEN_WIDTH - 20, SCREEN_HEIGHT - 20))
                if end_btn_rect.collidepoint(event.pos):
                    play_sfx(choice_sfx)
                    running = False
                else:
                    play_sfx(choice_sfx)
                    game_state = "START_SCREEN"
                    current_round = 1
                    score = 0
                    ai_score = 0
                    artifacts.clear()
                    selected_button_idx = 0
                    prev_btn_idx = 0
                    total_player_wins = 0
                    total_ai_wins = 0
                    player_won_rounds.clear()

        if not show_settings:
            if prev_btn_idx != selected_button_idx and selected_button_idx != -1:
                play_sfx(choice_sfx)
            # 마우스가 유물 밖으로 나가서 설명창이 닫힐 때는 사운드 재생 방지
            elif prev_art_idx != selected_artifact_idx and selected_artifact_idx != -1:
                play_sfx(choice_sfx)

    if game_state == "START_SCREEN":
        screen.blit(background_image, (0, 0))
        
        # 선택 상태에 따라 버튼 크기 다르게 출력
        start_img = start_btn_large if selected_button_idx == 0 else start_btn_small
        sound_img = sound_btn_large if selected_button_idx == 1 else sound_btn_small
        
        screen.blit(start_img, start_img.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT - 150)))
        screen.blit(sound_img, sound_img.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT - 80)))
    elif show_settings:
        pass  # 설정창이 켜져 있으면 하위 게임 로직(이동, 타이머 등) 업데이트 중지
    elif game_state == "PLAYING":
        # 키보드 입력 처리 (플레이어 이동)
        keys = pygame.key.get_pressed()
        if keys[pygame.K_LEFT]:
            player_rect.x -= player_speed
        if keys[pygame.K_RIGHT]:
            player_rect.x += player_speed

        # 화면 경계 제한 (플레이어가 화면 밖으로 나가지 못하게 함)
        if player_rect.left < 0:
            player_rect.left = 0
        if player_rect.right > SCREEN_WIDTH:
            player_rect.right = SCREEN_WIDTH

        # AI 도둑 이동 로직 (가장 가까운 유물 추적)
        if artifacts:
            # 직선거리가 가장 짧은 유물 타겟팅 (피타고라스 정리 활용)
            target = min(artifacts, key=lambda a: (thief_rect.centerx - a["rect"].centerx)**2 + (thief_rect.centery - a["rect"].centery)**2)
            if abs(thief_rect.centerx - target["rect"].centerx) <= thief_speed:
                pass  # 거리가 속도보다 작거나 같으면 진동(Jittering) 방지를 위해 이동하지 않음
            elif thief_rect.centerx < target["rect"].centerx:
                thief_rect.x += thief_speed
            elif thief_rect.centerx > target["rect"].centerx:
                thief_rect.x -= thief_speed
                
        # AI 도둑 화면 경계 제한
        if thief_rect.left < 0:
            thief_rect.left = 0
        if thief_rect.right > SCREEN_WIDTH:
            thief_rect.right = SCREEN_WIDTH

        # 유물 낙하 로직 및 화면 밖 처리
        for artifact in artifacts[:]:
            artifact["rect"].y += artifact_speed
            if artifact["rect"].top > SCREEN_HEIGHT:
                artifacts.remove(artifact)

        # 충돌 처리 로직 (플레이어 및 AI 도둑 vs 유물)
        for artifact in artifacts[:]:
            if player_rect.colliderect(artifact["rect"]):
                artifacts.remove(artifact)  # 충돌한 유물 제거
                score += 1                  # 점수 1 증가
                play_sfx(get_sfx)
            elif thief_rect.colliderect(artifact["rect"]):
                artifacts.remove(artifact)  # 충돌한 유물 제거
                ai_score += 1               # 도둑 점수 1 증가
                
        # 라운드 종료 및 게임 종료 조건 체크
        elapsed_round_time = pygame.time.get_ticks() - round_start_time
        remaining_time = max(0, (round_duration - elapsed_round_time) // 1000)

        if elapsed_round_time >= round_duration:
            game_state = "ROUND_OVER"
            round_over_time = pygame.time.get_ticks()
            if score > ai_score:
                total_player_wins += 1
                player_won_rounds.append(current_round)
                play_sfx(clear_sfx)
            elif score < ai_score:
                total_ai_wins += 1
                
    elif game_state == "ROUND_OVER":
        elapsed = pygame.time.get_ticks() - round_over_time
        if current_round >= max_rounds and elapsed >= 3500:
            game_state = "GAME_OVER"
            selected_button_idx = 0  # 게임 오버 시 결과 확인 버튼 기본 선택
        elif elapsed >= 3500:
            # 결과 표시 후 다음 라운드 준비 및 카운트다운 시작
            current_round += 1
            score = 0
            ai_score = 0
            artifacts.clear()
            thief_speed = ai_initial_speeds[current_round - 1]
            artifact_speed = 5
            spawn_interval = 1000
            player_rect.x = (SCREEN_WIDTH - player_width) // 2
            thief_rect.x = random.randint(0, SCREEN_WIDTH - thief_width)
            game_state = "ROUND_START"
            round_start_timer = pygame.time.get_ticks()
            countdown_sec = -1

    elif game_state == "ROUND_START":
        elapsed = pygame.time.get_ticks() - round_start_timer
        current_sec = elapsed // 1000
        if current_sec < 3 and current_sec != countdown_sec:
            play_sfx(number_sfx)
            countdown_sec = current_sec
            
        if elapsed >= 5000:
            pygame.time.set_timer(SPAWN_ARTIFACT, spawn_interval)
            pygame.time.set_timer(INCREASE_DIFFICULTY, 10000)  # 라운드 시작 시 난이도 상승 타이머 초기화
            game_state = "PLAYING"
            round_start_time = pygame.time.get_ticks()

    # 게임 플레이, 라운드 종료, 게임 오버 상태일 때의 화면 그리기
    if game_state in ["PLAYING", "ROUND_OVER", "ROUND_START", "GAME_OVER"]:
        screen.fill(BLACK)
        screen.blit(play_bg_image, play_bg_rect)         # 플레이 화면 배경 이미지 출력

        # AI 도둑 이미지 그리기 (콜라이더인 자루를 기준으로 이미지의 위치를 맞춰서 출력)
        thief_draw_x = thief_rect.centerx - (thief_image.get_width() // 2)
        thief_draw_y = thief_rect.bottom - thief_image.get_height()
        screen.blit(thief_image, (thief_draw_x, thief_draw_y))
        
        # 플레이어 이미지 그리기 (콜라이더 기준으로 이미지 위치 맞춤)
        player_draw_x = player_rect.centerx - (player_image.get_width() // 2)
        player_draw_y = player_rect.bottom - player_image.get_height()
        screen.blit(player_image, (player_draw_x, player_draw_y))
        
        for artifact in artifacts:
            screen.blit(artifact["image"], (artifact["rect"].x, artifact["rect"].y))     # 유물 이미지 출력

        # 점수 표시 (좌측 상단: 플레이어, 우측 상단: AI 도둑)
        score_shadow = ui_font.render(f"내 점수: {score}", True, BLACK)
        score_text = ui_font.render(f"내 점수: {score}", True, (255, 255, 255))
        ai_score_shadow = ui_font.render(f"도둑: {ai_score}", True, BLACK)
        ai_score_text = ui_font.render(f"도둑: {ai_score}", True, RED)
        round_shadow = round_font.render(f"{current_round}/{max_rounds}", True, BLACK)
        round_text = round_font.render(f"{current_round}/{max_rounds}", True, GOLD)
        
        screen.blit(score_shadow, (12, 12))
        screen.blit(score_text, (10, 10))
        screen.blit(round_shadow, (SCREEN_WIDTH//2 - round_text.get_width()//2 + 2, 12))
        screen.blit(round_text, (SCREEN_WIDTH//2 - round_text.get_width()//2, 10))
        screen.blit(ai_score_shadow, (SCREEN_WIDTH - ai_score_text.get_width() - 8, 12))
        screen.blit(ai_score_text, (SCREEN_WIDTH - ai_score_text.get_width() - 10, 10))
        
        time_shadow = ui_font.render(f"남은 시간: {remaining_time}", True, BLACK)
        time_text = ui_font.render(f"남은 시간: {remaining_time}", True, (255, 255, 255))
        screen.blit(time_shadow, (SCREEN_WIDTH//2 - time_text.get_width()//2 + 2, 42))
        screen.blit(time_text, (SCREEN_WIDTH//2 - time_text.get_width()//2, 40))

        # 상태별 중앙 메시지 출력
        if game_state == "ROUND_OVER":
            elapsed = pygame.time.get_ticks() - round_over_time
            if elapsed < 1500:
                msg_text = "시간 종료!"
            else:
                if score > ai_score:
                    msg_text = "도둑으로부터 유물을 지켜냈습니다!"
                elif score < ai_score:
                    msg_text = "저런, 도둑이 유물을 훔쳐갔습니다!"
                else:
                    msg_text = "무승부입니다!"
            msg_shadow = font.render(msg_text, True, BLACK)
            msg = font.render(msg_text, True, (255, 255, 255))
            screen.blit(msg_shadow, (SCREEN_WIDTH//2 - msg.get_width()//2 + 2, SCREEN_HEIGHT//2 + 2))
            screen.blit(msg, (SCREEN_WIDTH//2 - msg.get_width()//2, SCREEN_HEIGHT//2))
        elif game_state == "ROUND_START":
            elapsed = pygame.time.get_ticks() - round_start_timer
            if elapsed < 1000:
                msg_text = "3"
            elif elapsed < 2000:
                msg_text = "2"
            elif elapsed < 3000:
                msg_text = "1"
            else:
                if current_round == 1:
                    msg_text = "<삼국/가야 시대>"
                elif current_round == 2:
                    msg_text = "<고려 시대>"
                else:
                    msg_text = "<조선 시대>"
            msg_shadow = font.render(msg_text, True, BLACK)
            msg = font.render(msg_text, True, (255, 255, 255))
            screen.blit(msg_shadow, (SCREEN_WIDTH//2 - msg.get_width()//2 + 2, SCREEN_HEIGHT//2 + 2))
            screen.blit(msg, (SCREEN_WIDTH//2 - msg.get_width()//2, SCREEN_HEIGHT//2))
        elif game_state == "GAME_OVER":
            check_img = check_btn_large if selected_button_idx == 0 else check_btn_small
            replay_img = replay_btn_large if selected_button_idx == 1 else replay_btn_small
            
            screen.blit(check_img, check_img.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 - 40)))
            screen.blit(replay_img, replay_img.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 40)))

    elif game_state == "ENDING_SCREEN":
        screen.fill(BLACK)
        unique_wins = sorted(list(set(player_won_rounds)))
        if len(unique_wins) == 0:
            screen.blit(lose_image, lose_rect)
        elif len(unique_wins) == 3:
            screen.blit(ending_image, ending_rect)
        else:
            bg_name = "round" + "".join(map(str, unique_wins)) + ".png"
            bg_img = ending_bgs.get(bg_name, lose_image)
            bg_rect = bg_img.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2))
            screen.blit(bg_img, bg_rect)
            
        if len(unique_wins) > 0:
            # 알파값 및 위치 업데이트
            for i in range(9):
                if i == selected_artifact_idx and is_artifact_available(i):
                    ending_alphas[i] = min(255, ending_alphas[i] + 15)
                    if i in ending_info_images:
                        desc_w, desc_h = ending_info_images[i].get_size()
                    else:
                        desc_w, desc_h = 240, 120

                    desc_x = (SCREEN_WIDTH - desc_w) // 2
                    desc_y = (SCREEN_HEIGHT - desc_h) // 2
                    
                    ending_positions[i] = (desc_x, desc_y)
                else:
                    ending_alphas[i] = max(0, ending_alphas[i] - 15)

            # 이미지가 표시될 조건 처리
            for i in range(9):
                if ending_alphas[i] > 0:
                    desc_x, desc_y = ending_positions[i]
                    
                    if i in ending_info_images:
                        info_img = ending_info_images[i].copy()
                        alpha_surface = pygame.Surface(info_img.get_size(), pygame.SRCALPHA)
                        alpha_surface.fill((255, 255, 255, ending_alphas[i]))
                        info_img.blit(alpha_surface, (0, 0), special_flags=pygame.BLEND_RGBA_MULT)
                        screen.blit(info_img, (desc_x, desc_y))
                    else:
                        # 이미지가 폴더에 없을 경우 기존 임시 설명창(네모 박스) 출력
                        desc_w, desc_h = 240, 120
                        desc_rect = pygame.Rect(0, 0, desc_w, desc_h)
                        desc_surface = pygame.Surface((desc_w, desc_h), pygame.SRCALPHA)
                        desc_surface.fill((20, 20, 20, int(220 * (ending_alphas[i] / 255))))
                        pygame.draw.rect(desc_surface, (*GOLD, ending_alphas[i]), desc_rect, 2)
                        screen.blit(desc_surface, (desc_x, desc_y))
                        
                        title_text = ui_font.render(f"유물 {i + 1}", True, GOLD)
                        title_text.set_alpha(ending_alphas[i])
                        info_text = round_font.render("(설명 이미지 로드 실패)", True, (200, 200, 200))
                        info_text.set_alpha(ending_alphas[i])
                        screen.blit(title_text, (desc_x + 10, desc_y + 10))
                        screen.blit(info_text, (desc_x + 10, desc_y + 50))

        return_msg = ui_font.render("아무 곳이나 클릭하여 처음으로 돌아가기", True, (255, 255, 255))
        return_shadow = ui_font.render("아무 곳이나 클릭하여 처음으로 돌아가기", True, BLACK)
        screen.blit(return_shadow, (SCREEN_WIDTH//2 - return_msg.get_width()//2 + 2, 20 + 2))
        screen.blit(return_msg, (SCREEN_WIDTH//2 - return_msg.get_width()//2, 20))

        # 종료 버튼 우측 하단에 그리기
        end_btn_img = end_btn_ending_large if selected_button_idx == 1 else end_btn_ending_small
        end_btn_rect = end_btn_img.get_rect(bottomright=(SCREEN_WIDTH - 20, SCREEN_HEIGHT - 20))
        screen.blit(end_btn_img, end_btn_rect)

    # === 설정창 그리기 (가장 위에 렌더링) ===
    if show_settings:
        # 반투명 어두운 배경 오버레이
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 180))
        screen.blit(overlay, (0, 0))

        # 설정창 박스
        settings_rect = pygame.Rect(SCREEN_WIDTH//2 - 200, SCREEN_HEIGHT//2 - 150, 400, 300)
        pygame.draw.rect(screen, (40, 40, 40), settings_rect, border_radius=15)
        pygame.draw.rect(screen, GOLD, settings_rect, 3, border_radius=15)

        # 설정창 타이틀 및 구분선
        title_text = settings_title_font.render("설 정", True, (255, 255, 255))
        screen.blit(title_text, (SCREEN_WIDTH//2 - title_text.get_width()//2, settings_rect.y + 20))
        pygame.draw.line(screen, (100, 100, 100), (settings_rect.x + 30, settings_rect.y + 65), (settings_rect.x + 370, settings_rect.y + 65), 2)

        # 슬라이더 UI 렌더링
        labels = {"master": "전체 음량", "bgm": "배경음악", "sfx": "효과음"}
        for key, rect in slider_rects.items():
            cy = rect.y + rect.height // 2
            label_text = settings_font.render(labels[key], True, (200, 200, 200))
            screen.blit(label_text, (rect.x - 120, cy - label_text.get_height() // 2))

            # 슬라이더 바탕 선
            pygame.draw.line(screen, (100, 100, 100), (rect.x, cy), (rect.x + rect.width, cy), 4)
            
            # 채워진 볼륨 선 및 핸들
            filled_width = int(rect.width * volumes[key])
            if filled_width > 0:
                pygame.draw.line(screen, GOLD, (rect.x, cy), (rect.x + filled_width, cy), 4)
            pygame.draw.circle(screen, (255, 255, 255), (rect.x + filled_width, cy), 8)
            
            # % 텍스트
            pct_text = settings_font.render(f"{int(volumes[key]*100)}%", True, (255, 255, 255))
            screen.blit(pct_text, (rect.x + rect.width + 15, cy - pct_text.get_height() // 2))
            
        esc_hint = settings_font.render("ESC 키 또는 배경을 클릭하여 돌아가기", True, (150, 150, 150))
        screen.blit(esc_hint, (SCREEN_WIDTH//2 - esc_hint.get_width()//2, settings_rect.bottom - 40))

    pygame.display.flip()
    clock.tick(60) # 초당 60프레임 고정

pygame.quit()
sys.exit()
