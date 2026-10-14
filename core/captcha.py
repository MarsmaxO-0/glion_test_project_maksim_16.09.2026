"""Slide-puzzle captcha: the server cuts a piece out of a generated picture,
the visitor drags a slider until the piece fits, the server checks the offset.

The target position lives only in the session; the page receives the
background with a hole and the piece image, never the answer.
"""
import base64
import io
import random
import time

from PIL import Image, ImageDraw, ImageFilter

WIDTH, HEIGHT = 320, 160
PIECE = 48          # piece body (without the knob)
KNOB = 10           # knob radius
TOLERANCE = 6       # px
MAX_ATTEMPTS = 5
TTL = 10 * 60       # seconds a puzzle stays valid

PALETTES = [
    [(20, 49, 92), (28, 68, 128), (60, 105, 172)],
    [(191, 74, 60), (212, 97, 78), (240, 161, 146)],
    [(247, 228, 220), (240, 161, 146), (191, 74, 60)],
    [(125, 87, 73), (176, 127, 107), (247, 230, 224)],
]


def _background(rng):
    """Abstract picture: gradient, soft circles and a few lines, so every puzzle looks different."""
    palette = rng.choice(PALETTES)
    img = Image.new('RGB', (WIDTH, HEIGHT))
    draw = ImageDraw.Draw(img)
    c0, c1 = palette[0], palette[1]
    for x in range(WIDTH):
        t = x / WIDTH
        draw.line([(x, 0), (x, HEIGHT)], fill=tuple(int(c0[i] + (c1[i] - c0[i]) * t) for i in range(3)))
    for _ in range(rng.randint(5, 9)):
        r = rng.randint(14, 48)
        cx, cy = rng.randint(0, WIDTH), rng.randint(0, HEIGHT)
        col = rng.choice(palette)
        draw.ellipse([cx - r, cy - r, cx + r, cy + r], fill=col)
    for _ in range(rng.randint(3, 6)):
        draw.line([(rng.randint(0, WIDTH), rng.randint(0, HEIGHT)), (rng.randint(0, WIDTH), rng.randint(0, HEIGHT))],
                  fill=rng.choice(palette), width=rng.randint(2, 5))
    return img.filter(ImageFilter.GaussianBlur(1.2))


def _piece_mask():
    """Puzzle-piece silhouette: square body with a knob on top and on the right."""
    size = PIECE + KNOB * 2
    mask = Image.new('L', (size, size), 0)
    d = ImageDraw.Draw(mask)
    off = KNOB
    d.rounded_rectangle([off, off, off + PIECE, off + PIECE], radius=6, fill=255)
    d.ellipse([off + PIECE // 2 - KNOB, 0, off + PIECE // 2 + KNOB, KNOB * 2], fill=255)          # top knob
    d.ellipse([off + PIECE - KNOB, off + PIECE // 2 - KNOB, off + PIECE + KNOB, off + PIECE // 2 + KNOB], fill=255)  # right knob
    return mask


def _png_data_url(img):
    buf = io.BytesIO()
    img.save(buf, format='PNG', optimize=True)
    return 'data:image/png;base64,' + base64.b64encode(buf.getvalue()).decode()


def new_puzzle(session):
    """Generate a puzzle, remember its answer in the session, return data for the page."""
    rng = random.Random()
    bg = _background(rng)
    mask = _piece_mask()
    size = mask.size[0]
    x = rng.randint(WIDTH // 2, WIDTH - size - 8)
    y = rng.randint(4, HEIGHT - size - 4)

    piece = Image.new('RGBA', (size, size), (0, 0, 0, 0))
    piece.paste(bg.crop((x, y, x + size, y + size)), (0, 0), mask)
    edge = ImageDraw.Draw(piece)
    edge.bitmap((0, 0), mask.filter(ImageFilter.FIND_EDGES), fill=(255, 255, 255, 180))

    hole = Image.new('RGBA', (size, size), (20, 30, 50, 150))
    bg = bg.convert('RGBA')
    bg.paste(hole, (x, y), mask)

    session['captcha'] = {'x': x, 'created': time.time(), 'attempts': 0}
    return {'bg': _png_data_url(bg), 'piece': _png_data_url(piece), 'y': y, 'size': size, 'width': WIDTH, 'height': HEIGHT}


def verify(session, value):
    """Check the slider offset against the stored answer. Single use: the puzzle is cleared after any check."""
    state = session.get('captcha')
    if not state:
        return False
    state['attempts'] = state.get('attempts', 0) + 1
    session['captcha'] = state
    fresh = time.time() - state.get('created', 0) <= TTL
    try:
        ok = abs(int(value) - int(state['x'])) <= TOLERANCE
    except (TypeError, ValueError):
        ok = False
    if ok and fresh and state['attempts'] <= MAX_ATTEMPTS:
        session.pop('captcha', None)
        return True
    if not fresh or state['attempts'] >= MAX_ATTEMPTS:
        session.pop('captcha', None)
    return False
