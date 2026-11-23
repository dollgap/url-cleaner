"""Generate PWA icons (192/512 + maskable) for 링크 깔끔이: dark navy tile + sky-blue chain-link glyph."""
from PIL import Image, ImageDraw, ImageFilter

BG = (8, 13, 20)              # #080d14 app background
BG_GLOW = (26, 46, 71)        # soft top glow
ACCENT = (82, 184, 255)       # #52b8ff
ACCENT_DEEP = (43, 143, 224)  # #2b8fe0
WORK = 1600                   # drawing resolution for the glyph


def background(size):
    """Full-bleed vertical gradient, lighter at the top (works for any + maskable)."""
    grad = Image.new("RGB", (size, size))
    gd = ImageDraw.Draw(grad)
    for y in range(size):
        t = y / size
        f = (1 - t) ** 1.7
        gd.line([(0, y), (size, y)], fill=tuple(
            int(BG_GLOW[i] * f + BG[i] * (1 - f)) for i in range(3)
        ))
    return grad


def stadium(size, cx, cy, w, h):
    """Filled stadium (capsule) mask centred at (cx, cy) in unit coordinates."""
    m = Image.new("L", (size, size), 0)
    r = h / 2
    ImageDraw.Draw(m).rounded_rectangle(
        [(cx - w / 2) * size, (cy - h / 2) * size, (cx + w / 2) * size, (cy + h / 2) * size],
        radius=r * size, fill=255
    )
    return m


def glyph(size, scale):
    """Two interlocking stadium rings, drawn vertically then rotated 45°."""
    L = WORK
    layer = Image.new("L", (L, L), 0)

    w = 0.30 * scale
    h = 0.365 * scale
    stroke = 0.076 * scale
    gap = 0.200 * scale

    for sign in (-1, 1):
        cy = 0.5 + sign * gap / 2
        outer = stadium(L, 0.5, cy, w, h)
        inner = stadium(L, 0.5, cy, w - 2 * stroke, h - 2 * stroke)
        layer.paste(255, (0, 0), outer)
        layer.paste(0, (0, 0), inner)

    bar = stadium(L, 0.5, 0.5, stroke * 1.0, gap + stroke)
    layer.paste(255, (0, 0), bar)

    layer = layer.rotate(45, resample=Image.BICUBIC, center=(L / 2, L / 2))
    return layer.resize((size, size), Image.LANCZOS)


def make(size, scale=1.18):
    img = background(size).convert("RGBA")
    g = glyph(size, scale)

    glow = g.filter(ImageFilter.GaussianBlur(radius=size * 0.05)).point(lambda v: int(v * 0.5))
    img.paste(Image.new("RGBA", (size, size), ACCENT + (255,)), (0, 0), glow)

    grad = Image.new("RGB", (size, size))
    gd = ImageDraw.Draw(grad)
    for y in range(size):
        t = y / size
        gd.line([(0, y), (size, y)], fill=tuple(
            int(ACCENT[i] * (1 - t) + ACCENT_DEEP[i] * t) for i in range(3)
        ))
    img.paste(grad, (0, 0), g)
    return img


if __name__ == "__main__":
    make(512, 1.18).save("work/url-cleaner-repo/icon-512.png", optimize=True)
    make(192, 1.18).save("work/url-cleaner-repo/icon-192.png", optimize=True)
    make(512, 0.96).save("work/url-cleaner-repo/icon-maskable-512.png", optimize=True)
    print("icons written")
