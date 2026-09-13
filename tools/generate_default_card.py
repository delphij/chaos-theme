#!/usr/bin/env python3
"""
Generate a minimalist, elegant default social sharing card for the Chaos theme.
Adheres to Japanese traditional Wairo aesthetics (Sumi, Hi-iro, Ruri-iro) and
modern typography standards. Output size: 1200x630 px.
"""

import os
from PIL import Image, ImageDraw, ImageFont

def main():
    script_dir = os.path.dirname(os.path.abspath(__file__))
    theme_root = os.path.dirname(script_dir)
    output_dir = os.path.join(theme_root, "static", "images")
    os.makedirs(output_dir, exist_ok=True)
    output_file = os.path.join(output_dir, "default-card.png")

    W, H = 1200, 630
    # Background: Deep Sumi (墨) #0F1014
    card = Image.new("RGBA", (W, H), (15, 16, 20, 255))

    # Right side: Zen Geometric Abstract Motif (Concentric rings, rotated square, clean lines)
    cx, cy = 920, 315

    # Ambient soft glow (Ruri-iro #1C355E & Hi-iro #8C2A2A)
    glow_layer = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    g_draw = ImageDraw.Draw(glow_layer)
    for r in range(240, 140, -10):
        g_draw.ellipse([(cx - r, cy - r), (cx + r, cy + r)], fill=(28, 53, 94, 8))
    for r in range(160, 80, -10):
        g_draw.ellipse([(cx - r, cy - r), (cx + r, cy + r)], fill=(160, 48, 48, 10))

    card = Image.alpha_composite(card, glow_layer)

    # Background subtle grid lines ONLY on the right half (x >= 650)
    grid_layer = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    gr_draw = ImageDraw.Draw(grid_layer)
    for x in range(650, W, 70):
        alpha = int(18 * ((x - 650) / (W - 650)))
        gr_draw.line([(x, 0), (x, H)], fill=(255, 255, 255, alpha), width=1)
    for y in range(40, H, 70):
        gr_draw.line([(650, y), (W, y)], fill=(255, 255, 255, 12), width=1)

    card = Image.alpha_composite(card, grid_layer)
    draw = ImageDraw.Draw(card)

    # Fine geometric vector lines
    # Concentric circles
    draw.ellipse([(cx - 160, cy - 160), (cx + 160, cy + 160)], outline=(224, 75, 75, 160), width=2)  # Hi-iro
    draw.ellipse([(cx - 110, cy - 110), (cx + 110, cy + 110)], outline=(230, 230, 235, 80), width=1)
    draw.ellipse([(cx - 50, cy - 50), (cx + 50, cy + 50)], outline=(224, 75, 75, 220), width=2)

    # Square rotated 45 deg
    diag = 150
    pts = [(cx, cy - diag), (cx + diag, cy), (cx, cy + diag), (cx - diag, cy)]
    draw.polygon(pts, outline=(90, 135, 195, 110), width=1)  # Ruri-iro

    # Axis crosshair
    draw.line([(cx - 200, cy), (cx + 200, cy)], fill=(255, 255, 255, 45), width=1)
    draw.line([(cx, cy - 200), (cx, cy + 200)], fill=(255, 255, 255, 45), width=1)

    # Center dot
    draw.ellipse([(cx - 7, cy - 7), (cx + 7, cy + 7)], fill=(245, 245, 248, 255))

    # Typography on Left
    font_title = ImageFont.truetype("/System/Library/Fonts/HelveticaNeue.ttc", 76, index=1)
    font_badge = ImageFont.truetype("/System/Library/Fonts/HelveticaNeue.ttc", 15, index=1)
    font_sub = ImageFont.truetype("/System/Library/Fonts/HelveticaNeue.ttc", 25, index=0)
    font_sub2 = ImageFont.truetype("/System/Library/Fonts/Hiragino Sans GB.ttc", 20, index=0)
    font_tags = ImageFont.truetype("/System/Library/Fonts/Menlo.ttc", 16, index=0)

    left_margin = 92

    # Badge
    dot_r = 5
    dot_y = 112
    draw.ellipse([(left_margin, dot_y - dot_r), (left_margin + dot_r * 2, dot_y + dot_r)], fill=(224, 72, 72, 255))
    draw.text((left_margin + 20, dot_y - 8), "HUGO THEME · MINIMALIST & FAST", font=font_badge, fill=(160, 165, 178, 255))

    # Main Title: Chaos
    draw.text((left_margin, 155), "Chaos", font=font_title, fill=(248, 248, 250, 255))

    # Subtitle
    draw.text((left_margin, 260), "Clarity, performance, and typography.", font=font_sub, fill=(215, 218, 228, 255))
    draw.text((left_margin, 302), "极简主义 · 和色美学 · 专注排版与极致性能", font=font_sub2, fill=(145, 150, 164, 255))

    # Subtle Hairline
    draw.line([(left_margin, 375), (left_margin + 520, 375)], fill=(42, 46, 56, 255), width=1)

    # Feature bullets
    draw.text((left_margin, 410), "0ms Instant Transitions · KaTeX · Dark/Light Mode", font=font_tags, fill=(170, 175, 190, 255))
    draw.text((left_margin, 446), "WCAG 2.1 AA · Semantic HTML · Zero External CDN", font=font_tags, fill=(135, 140, 155, 255))

    # Subtle outer border
    draw.rectangle([(0, 0), (W - 1, H - 1)], outline=(36, 40, 48, 255), width=1)

    card.save(output_file, optimize=True)
    print(f"Generated theme social card at {output_file}")

if __name__ == "__main__":
    main()
