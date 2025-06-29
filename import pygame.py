import pygame
import random
import math

# Initialize Pygame
pygame.init()

# Screen setup
WIDTH, HEIGHT = 800, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Animated Heart - From Shreyash")

# Colors
BLACK = (0, 0, 0)
RED = (255, 0, 0)
PINK = (255, 105, 180)
WHITE = (255, 255, 255)

# Clock
clock = pygame.time.Clock()

# Load font
pygame.font.init()
font = pygame.font.SysFont("Arial", 36, bold=True)

# Heart point generator
def generate_heart_points(x, y, size):
    points = []
    for t in range(0, 360, 1):
        t_rad = math.radians(t)
        x_heart = size * 16 * math.sin(t_rad) ** 3
        y_heart = -size * (13 * math.cos(t_rad) - 5 * math.cos(2 * t_rad)
                           - 2 * math.cos(3 * t_rad) - math.cos(4 * t_rad))
        points.append((x + x_heart, y + y_heart))
    return points

def draw_heart(surface, x, y, size, color, border=False):
    points = generate_heart_points(x, y, size)
    pygame.draw.polygon(surface, color, points)
    if border:
        pygame.draw.polygon(surface, PINK, points, width=2)

# Small glowing heart
class SmallHeart:
    def __init__(self):
        self.reset()

    def reset(self):
        # Avoid placing small hearts too close to the main heart
        center_zone = pygame.Rect(WIDTH//2 - 180, HEIGHT//2 - 180, 360, 360)  # Larger exclusion zone
        attempts = 0
        while True:
            self.x = random.randint(0, WIDTH)
            self.y = HEIGHT + random.randint(0, 100)
            if not center_zone.collidepoint(self.x, self.y) or attempts > 20:
                break
            attempts += 1

        self.size = random.uniform(0.3, 0.5)
        self.speed = random.uniform(0.3, 0.7)  # Slower floating
        self.blink_timer = random.randint(20, 50)  # Slower blink
        self.visible = random.choice([True, False])

    def update(self):
        self.y -= self.speed
        self.blink_timer -= 1
        if self.blink_timer <= 0:
            self.visible = not self.visible
            self.blink_timer = random.randint(20, 50)
        if self.y < -50:
            self.reset()

    def draw(self, surface):
        if self.visible:
            # Glow
            glow_radius = int(self.size * 30)
            glow_surface = pygame.Surface((glow_radius * 2, glow_radius * 2), pygame.SRCALPHA)
            pygame.draw.circle(glow_surface, (255, 0, 0, 60), (glow_radius, glow_radius), glow_radius)
            surface.blit(glow_surface, (self.x - glow_radius, self.y - glow_radius), special_flags=pygame.BLEND_RGBA_ADD)

            # Heart with pink border, smaller size
            draw_heart(surface, self.x, self.y, self.size * 5, PINK, border=True)

# Main center heart with animated scale
class CenterHeart:
    def __init__(self):
        self.scale = 0.0
        self.max_scale = 1.0
        self.growth_speed = 0.005  # Slower growth
        self.visible = False
        self.start_ticks = pygame.time.get_ticks()
        self.draw_progress = 0  # Number of degrees drawn
        self.drawing = True
        self.filled = False

    def update(self):
        if self.drawing:
            self.draw_progress += 1  # Slower outline drawing
            if self.draw_progress >= 360:
                self.draw_progress = 360
                self.drawing = False
                self.filled = True
        elif self.scale < self.max_scale:
            # Grow after outline is drawn
            self.scale += self.growth_speed * (1 - self.scale / self.max_scale)
        else:
            # Pulse effect using sine wave after fully grown
            t = (pygame.time.get_ticks() - self.start_ticks) / 600.0  # Slower pulse
            self.scale = self.max_scale + 0.05 * math.sin(t)
        self.visible = self.draw_progress > 0 or self.scale > 0

    def draw(self, surface):
        if self.visible:
            if self.drawing:
                # Draw animated outline
                points = []
                for t in range(0, self.draw_progress, 1):
                    t_rad = math.radians(t)
                    x_heart = 7 * 16 * math.sin(t_rad) ** 3  # Larger heart (was 5)
                    y_heart = -7 * (13 * math.cos(t_rad) - 5 * math.cos(2 * t_rad)
                                    - 2 * math.cos(3 * t_rad) - math.cos(4 * t_rad))
                    points.append((WIDTH // 2 + x_heart, HEIGHT // 2 + y_heart))
                if len(points) > 1:
                    pygame.draw.lines(surface, RED, False, points, 4)
            else:
                # Fill and pulse
                draw_heart(surface, WIDTH // 2, HEIGHT // 2, 7 * self.scale, RED)  # Larger heart
                # Draw 'Love for you' in the center
                love_font = pygame.font.SysFont("Arial", 32, bold=True)
                love_text = love_font.render("Love for you", True, WHITE)
                text_rect = love_text.get_rect(center=(WIDTH // 2, HEIGHT // 2))
                surface.blit(love_text, text_rect)

# Animated text fade-in
class FadingText:
    def __init__(self, text, x, y, duration=120, char_fade=20):  # Slower fade
        self.text = text
        self.x = x
        self.y = y
        self.duration = duration
        self.char_fade = char_fade  # frames per character fade
        self.frame = 0
        self.chars_shown = 0
        self.char_alphas = [0] * len(text)
        self.done = False
        # Use the same font as above for emoji support
        self.surfaces = [text_font.render(c, True, WHITE).convert_alpha() for c in text]

    def update(self):
        if not self.done:
            self.frame += 1
            # Reveal next character every char_fade frames
            if self.chars_shown < len(self.text) and self.frame // self.char_fade > self.chars_shown:
                self.chars_shown += 1
            # Fade in each shown character
            for i in range(self.chars_shown):
                if self.char_alphas[i] < 255:
                    self.char_alphas[i] += int(255 / self.char_fade)
                    if self.char_alphas[i] > 255:
                        self.char_alphas[i] = 255
            if self.chars_shown == len(self.text) and all(a >= 255 for a in self.char_alphas):
                self.done = True

    def draw(self, screen):
        x_offset = 0
        t = pygame.time.get_ticks() / 400.0  # Animation time
        for i, surf in enumerate(self.surfaces):
            s = surf.copy()
            s.set_alpha(self.char_alphas[i])
            rect = s.get_rect()
            # Wave effect: each char moves up/down in a sine wave
            wave_y = self.y + int(8 * math.sin(t + i * 0.5))
            rect.topleft = (self.x + x_offset, wave_y)
            screen.blit(s, rect)
            x_offset += rect.width

# Love letter animation class
class LoveLetter:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.letter_y = y + 40
        self.opening = True
        self.open_progress = 0 # 0 to 1
        self.slide_progress = 0 # 0 to 1
        self.done = False

    def update(self):
        if self.opening:
            self.open_progress += 0.008 # Slower open
            if self.open_progress >= 1:
                self.open_progress = 1
                self.opening = False
        elif not self.done:
            self.slide_progress += 0.008 # Slower slide
            if self.slide_progress >= 1:
                self.slide_progress = 1
                self.done = True

    def draw(self, surface):
        # Envelope base
        pygame.draw.rect(surface, (255, 230, 200), (self.x, self.y + 40, 80, 50), border_radius=8)
        # Envelope flap (animated open)
        flap_height = int(30 * (1 - self.open_progress))
        pygame.draw.polygon(surface, (255, 200, 200), [
            (self.x, self.y + 40),
            (self.x + 40, self.y + 10 - flap_height),
            (self.x + 80, self.y + 40)
        ])
        # Letter (slides out)
        letter_slide = int(40 * self.slide_progress)
        pygame.draw.rect(surface, WHITE, (self.x + 10, self.y + 45 - letter_slide, 60, 40), border_radius=4)
        # Heart seal on letter
        pygame.draw.circle(surface, PINK, (self.x + 40, self.y + 65 - letter_slide), 7)
        # Optional: add a small heart on the envelope
        pygame.draw.polygon(surface, RED, [
            (self.x + 40, self.y + 60),
            (self.x + 35, self.y + 55),
            (self.x + 30, self.y + 60),
            (self.x + 40, self.y + 75),
            (self.x + 50, self.y + 60),
            (self.x + 45, self.y + 55)
        ])

# Animated rose (vector art)
class AnimatedRose:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.angle = 0
        self.angle_speed = 0.5  # degrees per frame

    def update(self):
        self.angle += self.angle_speed
        if self.angle > 360:
            self.angle -= 360

    def draw(self, surface):
        cx, cy = self.x, self.y
        # Stem
        pygame.draw.line(surface, (34, 139, 34), (cx, cy+20), (cx, cy+60), 6)  # ForestGreen
        # Leaves
        pygame.draw.ellipse(surface, (46, 139, 87), (cx-18, cy+40, 20, 12))  # SeaGreen
        pygame.draw.ellipse(surface, (46, 139, 87), (cx-2, cy+50, 20, 12))
        # Petals (animated rotation)
        for i in range(5):
            petal_angle = math.radians(self.angle + i * 72)
            px = cx + 22 * math.cos(petal_angle)
            py = cy + 22 * math.sin(petal_angle)
            pygame.draw.ellipse(surface, (229, 57, 53), (px-12, py-16, 24, 32))  # Red petals
        # Center
        pygame.draw.circle(surface, (183, 28, 28), (cx, cy), 14)

# Initialize objects
small_hearts = [SmallHeart() for _ in range(10)]  # Reduced from 30 to 10
center_heart = CenterHeart()
love_letter = LoveLetter(60, HEIGHT // 2 - 60)
animated_rose = AnimatedRose(WIDTH - 90, HEIGHT - 120)  # Bottom right corner
# Center the text horizontally and place at top
try:
    emoji_font = pygame.font.SysFont("Segoe UI Emoji", 36, bold=True)
    test_surface = emoji_font.render("From your Shreyash❤️😁", True, WHITE)
    if test_surface.get_width() > 0:
        text_font = emoji_font
    else:
        text_font = font
except:
    text_font = font
from_text = "From your Shreyash❤️😁"
text_surface = text_font.render(from_text, True, WHITE)
text_x = WIDTH // 2 - text_surface.get_width() // 2
text_y = 40  # Top of the window
text = FadingText(from_text, text_x, text_y)

# Add a flag to track if the diary page is open
open_diary_page = False
open_diary_win = None  # Track the diary window instance

def open_diary_entry_page():
    import tkinter as tk
    import time
    from threading import Thread
    global open_diary_page, open_diary_win
    if not hasattr(open_diary_entry_page, 'root'):
        open_diary_entry_page.root = tk.Tk()
        open_diary_entry_page.root.withdraw()
    diary_win = tk.Toplevel(open_diary_entry_page.root)
    open_diary_win = diary_win
    diary_win.title("Diary Entry")
    diary_win.geometry("420x350")
    diary_win.configure(bg="#fff0f6")
    # Romantic background theme (gradient + faded hearts)
    bg_canvas = tk.Canvas(diary_win, width=420, height=350, highlightthickness=0)
    bg_canvas.place(x=0, y=0, relwidth=1, relheight=1)
    # Draw a vertical pink gradient
    for i in range(0, 350):
        color = f"#ff{hex(240 - i//2)[2:]:>02}f6"
        bg_canvas.create_line(0, i, 420, i, fill=color)
    # Draw faded hearts
    def faded_heart(cx, cy, size, color):
        points = []
        for t in range(0, 360, 8):
            t_rad = math.radians(t)
            x_heart = size * 16 * math.sin(t_rad) ** 3
            y_heart = -size * (13 * math.cos(t_rad) - 5 * math.cos(2 * t_rad) - 2 * math.cos(3 * t_rad) - math.cos(4 * t_rad))
            points.append((cx + x_heart, cy + y_heart))
        bg_canvas.create_polygon(points, fill=color, outline="", stipple="gray25")
    faded_heart(60, 80, 2, "#f8bbd0")
    faded_heart(350, 60, 1.5, "#f48fb1")
    faded_heart(200, 300, 2.5, "#fce4ec")
    faded_heart(320, 220, 1.2, "#f8bbd0")
    faded_heart(120, 200, 1.7, "#f48fb1")
    # Romantic border frame (above bg_canvas)
    border = tk.Frame(diary_win, bg="#f8bbd0", bd=6, relief="ridge")
    border.place(relx=0, rely=0, relwidth=1, relheight=1)
    # Top frame for heart animation only (rose removed)
    top_frame = tk.Frame(border, bg="#f8bbd0")
    top_frame.pack(pady=(10, 0), fill=tk.X)
    # Heart animation (centered at the top)
    canvas = tk.Canvas(top_frame, width=90, height=90, bg="#fff0f6", highlightthickness=0)
    canvas.pack(side=tk.TOP, pady=(0, 0), anchor="n")
    def draw_heart_anim():
        for scale in range(1, 21):
            canvas.delete("all")
            points = []
            for t in range(0, 360, 2):
                t_rad = math.radians(t)
                x_heart = scale * 2.2 * 16 * math.sin(t_rad) ** 3
                y_heart = -scale * 2.2 * (13 * math.cos(t_rad) - 5 * math.cos(2 * t_rad) - 2 * math.cos(3 * t_rad) - math.cos(4 * t_rad))
                points.append((45 + x_heart, 45 + y_heart))
            canvas.create_polygon(points, fill="#e75480", outline="#ad1457", width=2)
            canvas.update()
            time.sleep(0.08)
        # Pulse
        for _ in range(10):
            for pulse in [1.0, 1.1, 1.0]:
                canvas.delete("all")
                points = []
                for t in range(0, 360, 2):
                    t_rad = math.radians(t)
                    x_heart = pulse * 22 * math.sin(t_rad) ** 3
                    y_heart = -pulse * 22 * (13 * math.cos(t_rad) - 5 * math.cos(2 * t_rad) - 2 * math.cos(3 * t_rad) - math.cos(4 * t_rad))
                    points.append((45 + x_heart, 45 + y_heart))
                canvas.create_polygon(points, fill="#e75480", outline="#ad1457", width=2)
                canvas.update()
                time.sleep(0.12)
    Thread(target=draw_heart_anim, daemon=True).start()
    # Romantic Sayarii
    sayarii = (
        "\u2764\ufe0f\u2764\ufe0f\u2764\ufe0f\n"
        "Every time I smile, believe me, you are the reason behind it...\n"
        "\u2764\ufe0f\u2764\ufe0f\u2764\ufe0f"
    )
    sayarii_label = tk.Label(border, text=sayarii, font=("Arial", 14, "italic"), fg="#ad1457", bg="#fff0f6", justify="center")
    sayarii_label.pack(pady=(10, 5))
    # Beautiful English thoughts (quotes)
    thoughts = [
        "Love is not about how many days, months, or years you have been together. Love is about how much you love each other every single day.",
        "You are the poem I never knew how to write, and this life is the story I have always wanted to tell.",
        "In you, I have found the love of my life and my closest, truest friend.",
        "Every moment spent with you is like a beautiful dream come true.",
        "I look at you and see the rest of my life in front of my eyes."
    ]
    thoughts_text = '\u2764\ufe0f Beautiful Thoughts:\n' + '\n'.join(f'• {q}' for q in thoughts)
    thoughts_label = tk.Label(border, text=thoughts_text, font=("Arial", 11, "italic"), fg="#6d4c41", bg="#fff0f6", justify="left", wraplength=380)
    thoughts_label.pack(pady=(2, 2))
    # Diary text area frame with rose image
    text_frame = tk.Frame(border, bg="#fff0f6")
    text_frame.pack(pady=10)
    # Draw a rose image on the left of the text box using Canvas (vector art, not file)
    rose_img_canvas = tk.Canvas(text_frame, width=60, height=60, bg="#fff0f6", highlightthickness=0)
    rose_img_canvas.pack(side=tk.LEFT, padx=(0, 10))
    def draw_static_rose():
        cx, cy = 30, 35
        # Stem (green)
        rose_img_canvas.create_line(cx, cy, cx, cy+18, fill="#228B22", width=4, smooth=True)  # ForestGreen
        # Leaves (green)
        rose_img_canvas.create_oval(cx-14, cy+6, cx-2, cy+18, fill="#2E8B57", outline="")  # SeaGreen
        rose_img_canvas.create_oval(cx+2, cy+6, cx+14, cy+18, fill="#2E8B57", outline="")
        # Petals (red)
        for i in range(5):
            petal_angle = i * 72
            rad = math.radians(petal_angle)
            px = cx + 12 * math.cos(rad)
            py = cy - 12 * math.sin(rad)
            rose_img_canvas.create_oval(px-8, py-8, px+8, py+8, fill="#e53935", outline="#b71c1c", width=2)  # Red petals
        # Center (dark red)
        rose_img_canvas.create_oval(cx-7, cy-7, cx+7, cy+7, fill="#b71c1c", outline="#e53935", width=2)
    draw_static_rose()
    # Diary text area
    text = tk.Text(text_frame, width=34, height=6, font=("Arial", 12), bg="#fff8fa", fg="#ad1457", bd=2, relief="groove")
    text.pack(side=tk.LEFT)
    # Save button
    def save_entry():
        entry = text.get("1.0", tk.END).strip()
        with open("diary_entry.txt", "w", encoding="utf-8") as f:
            f.write(entry)
        # Confirmation popup
        popup = tk.Toplevel(diary_win)
        popup.title("Saved!")
        popup.geometry("200x80")
        popup.configure(bg="#fff0f6")
        msg = tk.Label(popup, text="Diary saved!", font=("Arial", 12), fg="#ad1457", bg="#fff0f6")
        msg.pack(pady=10)
        ok_btn = tk.Button(popup, text="OK", command=popup.destroy, font=("Arial", 10, "bold"), bg="#d81b60", fg="white", bd=0, padx=10, pady=2)
        ok_btn.pack()
        # Open new tab with animated rose background after save
        def open_rose_animation_tab():
            rose_win = tk.Toplevel(diary_win)
            rose_win.title("Rose - Thank You")
            rose_win.geometry("400x400")
            rose_win.configure(bg="#fff0f6")
            # Removed rose image section
            note = tk.Label(rose_win, text="Thank youu!\nYou are special.", font=("Arial", 20, "bold italic"), fg="#d81b60", bg="#fff0f6", justify="center")
            note.pack(pady=(120, 30))
            rose_win.lift()
            rose_win.focus_force()
        # Open the rose animation tab after a short delay so user sees the confirmation
        popup.after(600, open_rose_animation_tab)
    save_btn = tk.Button(border, text="Save", command=save_entry, font=("Arial", 11, "bold"), bg="#43a047", fg="white", bd=0, padx=16, pady=4, relief="ridge")
    save_btn.pack(pady=(0, 6))
    # Close button
    def close_diary():
        global open_diary_page, open_diary_win
        open_diary_page = False
        open_diary_win = None
        diary_win.destroy()
    close_btn = tk.Button(border, text="Close", command=close_diary, font=("Arial", 11, "bold"), bg="#d81b60", fg="white", bd=0, padx=16, pady=4, relief="ridge")
    close_btn.pack(pady=(0, 10))
    diary_win.protocol("WM_DELETE_WINDOW", close_diary)

# Main loop
running = True
while running:
    screen.fill(BLACK)
    # Draw floating hearts
    for heart in small_hearts:
        heart.update()
        heart.draw(screen)
    # Love letter animation at the side
    love_letter.update()
    love_letter.draw(screen)
    # Add a short note below the love letter
    note_font = pygame.font.SysFont("Arial", 18, bold=True)
    note_text = note_font.render("Click the love letter", True, (255, 182, 193))  # Light pink
    note_rect = note_text.get_rect()
    note_rect.topleft = (love_letter.x, love_letter.y + 100)
    screen.blit(note_text, note_rect)
    # Center heart animation
    center_heart.update()
    center_heart.draw(screen)
    # Animated rose
    animated_rose.update()
    animated_rose.draw(screen)
    # Animated text
    text.update()
    text.draw(screen)
    # Handle click event for the heart and love letter
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            mx, my = event.pos
            # Check if click is inside the main heart area (approximate with a circle)
            heart_radius = int(7 * center_heart.scale * 16)
            heart_clicked = (mx - WIDTH // 2) ** 2 + (my - HEIGHT // 2) ** 2 < heart_radius ** 2
            # Check if click is inside the love letter envelope (approximate with a rectangle)
            letter_x, letter_y = love_letter.x, love_letter.y + 40
            letter_w, letter_h = 80, 50
            letter_clicked = letter_x <= mx <= letter_x + letter_w and letter_y <= my <= letter_y + letter_h
            if (heart_clicked or letter_clicked) and not open_diary_page:
                open_diary_page = True
                open_diary_entry_page()
    # Update Tkinter diary window if open
    if open_diary_win is not None:
        try:
            open_diary_win.update()
        except:
            open_diary_win = None
    pygame.display.flip()
    clock.tick(60)  # Limit to 60 FPS

# Quit Pygame
pygame.quit()


