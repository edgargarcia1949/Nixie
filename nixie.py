import pygame
import time

pygame.init()

box_width = 80
box_height = 120
spacing = 10
colon_gap = 18
background = (40, 40, 40)
colon_color = (255, 165, 0)

# Load the digit images from the same folder as this script.
original_images = [
    pygame.image.load(f"digit{i}.png")
    for i in range(10)
]

# Sizes ordered from smallest to largest.
sizes = [0.5, 0.75, 1.0]
size_index = 2  # Start at full size.


def get_layout(scale):
    scaled_box_width = round(box_width * scale)
    scaled_box_height = round(box_height * scale)
    scaled_spacing = round(spacing * scale)
    scaled_colon_gap = round(colon_gap * scale)

    digit_x_positions = []
    x = 0

    for i in range(6):
        digit_x_positions.append(x)
        x += scaled_box_width + scaled_spacing
        if i in (1, 3):
            x += scaled_colon_gap

    window_width = (
        6 * scaled_box_width
        + 5 * scaled_spacing
        + 2 * scaled_colon_gap
        + round(50 * scale)
    )

    return (
        scaled_box_width,
        scaled_box_height,
        scaled_colon_gap,
        digit_x_positions,
        window_width,
    )


def fit_images(scale, target_box_width, target_box_height):
    fitted = []

    for image in original_images:
        fit_scale = min(
            target_box_width / image.get_width(),
            target_box_height / image.get_height(),
        )
        new_size = (
            max(1, round(image.get_width() * fit_scale)),
            max(1, round(image.get_height() * fit_scale)),
        )
        fitted.append(pygame.transform.scale(image, new_size))

    return fitted


def make_window(scale):
    (
        target_box_width,
        target_box_height,
        _,
        _,
        window_width,
    ) = get_layout(scale)

    window_height = round(box_height * scale)
    window = pygame.display.set_mode((window_width, window_height))
    fitted = fit_images(scale, target_box_width, target_box_height)
    return window, fitted


# Create the display before calling convert_alpha().
initial_layout = get_layout(sizes[size_index])
screen = pygame.display.set_mode((initial_layout[4], round(box_height * sizes[size_index])))
pygame.display.set_caption("Nixie Clock")

original_images = [image.convert_alpha() for image in original_images]
fitted_images = fit_images(
    sizes[size_index],
    initial_layout[0],
    initial_layout[1],
)


clock = pygame.time.Clock()
is_12_hour = False
running = True

while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        elif event.type == pygame.KEYDOWN and event.mod & pygame.KMOD_CTRL:
            if event.key in (pygame.K_MINUS, pygame.K_KP_MINUS):
                if size_index > 0:
                    size_index -= 1
                    screen, fitted_images = make_window(sizes[size_index])

            elif event.key in (
                pygame.K_EQUALS,
                pygame.K_PLUS,
                pygame.K_KP_PLUS,
            ):
                if size_index < len(sizes) - 1:
                    size_index += 1
                    screen, fitted_images = make_window(sizes[size_index])
            elif event.key == pygame.K_1:
                is_12_hour = not is_12_hour
            elif event.key == pygame.K_q:
                running = False

    scale = sizes[size_index]
    (
        target_box_width,
        target_box_height,
        scaled_colon_gap,
        digit_x_positions,
        _,
    ) = get_layout(scale)

    screen.fill(background)

    now = time.localtime()
    if is_12_hour:
        indicator = "AM" if now.tm_hour < 12 else "PM"
        font = pygame.font.Font(None, max(1, round(28 * scale)))
        label = font.render(indicator, True, (255, 165, 0))
        x = digit_x_positions[5] + target_box_width + round(8 * scale)
        y = (screen.get_height() - label.get_height()) // 2
        screen.blit(label, (x, y))
        hour_12 = now.tm_hour % 12
        if hour_12 == 0:
            hour_12 = 12
        digits = f"{hour_12:2d}{now.tm_min:02d}{now.tm_sec:02d}"
    else:
        digits = f"{now.tm_hour:2d}{now.tm_min:02d}{now.tm_sec:02d}"

    for i, digit_char in enumerate(digits):
        if digit_char == " ":
            continue
        image = fitted_images[int(digit_char)]
        y = (screen.get_height() - image.get_height()) // 2
        screen.blit(image, (digit_x_positions[i], y))

    # Draw the two dots in each colon.
    for digit_index in (1, 3):
        colon_x = (
            digit_x_positions[digit_index]
            + target_box_width
            + round(spacing * scale)
            + scaled_colon_gap // 2
        )
        radius = max(1, round(4 * scale))
        pygame.draw.circle(
            screen, colon_color, (colon_x, screen.get_height() // 3), radius
        )
        pygame.draw.circle(
            screen, colon_color, (colon_x, 2 * screen.get_height() // 3), radius
        )

    pygame.display.flip()
    clock.tick(10)

pygame.quit()
