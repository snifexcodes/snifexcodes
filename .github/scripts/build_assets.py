#!/usr/bin/env python3
"""
Builds every 3D image in assets/ for the profile README.

Edit the CONFIG block, then:
    pip install fonttools brotli
    python3 .github/scripts/build_assets.py

All text is converted to vector paths (Unbounded + Space Grotesk, both OFL),
so the images look identical on every OS. Animations are pure CSS/SMIL,
which GitHub renders inside <img> tags.
"""
import math
import random
from pathlib import Path

from fontTools.pens.svgPathPen import SVGPathPen
from fontTools.pens.transformPen import TransformPen
from fontTools.ttLib import TTFont

ROOT = Path(__file__).resolve().parents[2]
ASSETS = ROOT / "assets"
FONTS = Path(__file__).resolve().parent / "fonts"

# ───────────────────────────── CONFIG ─────────────────────────────
NAME = "RAJ"
TAGLINE = "FULL-STACK DEVELOPER  ·  AUTOMATION  ·  LINUX"
SUBLINE = "BCA @ Tilak Maharashtra Vidyapeeth"

SKILLS = [  # (label, colour)
    ("HTML", "#e34c26"), ("CSS", "#2965f1"), ("JS", "#f7df1e"), ("PHP", "#777bb4"),
    ("Python", "#3776ab"), ("Java", "#f89820"), ("MySQL", "#00a3c4"), ("Linux", "#fcc624"),
    ("Bash", "#4eaa25"), ("Git", "#f05032"),
]

PROJECTS = [  # file stem, kicker, title, description, tags, icon, accent
    ("project-1", "PYTHON · SCRAPER", "Paper Analyzer",
     "Scrapes TMV's DSpace repository and finds exam questions that repeat across years, then builds a PDF report.",
     ["Python", "Scraping", "PDF"], "papers", "#22d3ee"),
    ("project-2", "WEB APP", "AI Chat UI",
     "Single-page chat interface with built-in diagram rendering and support for multiple AI providers.",
     ["HTML", "JS", "LLM APIs"], "chat", "#a78bfa"),
    ("project-3", "PYTHON · MCP", "Binance MCP",
     "MCP server and trading-bot tooling for crypto futures on Binance.",
     ["Python", "MCP", "Binance API"], "bars", "#f472b6"),
    ("project-4", "JAVA · MINECRAFT", "Flashback Bridge",
     "Mod patch that bridges CreamyKeys audio into Flashback replays and exports.",
     ["Java", "Modding"], "bridge", "#fbbf24"),
]
FEATURED = dict(
    kicker="FEATURED  ·  PYTHON  ·  COMPUTER VISION",
    title="Mudra",
    subtitle="Real-time sign language to text",
    desc="Watches your hand through a webcam and turns signs into live captions in the browser. "
         "Teach it new signs, and it trains and compares four ML models on your recordings.",
    tags=["Python", "Flask", "MediaPipe", "scikit-learn"],
    sign="HELLO", conf="97%", accent="#34d399",
)
# ──────────────────────────────────────────────────────────────────

CYAN, VIOLET, PINK, AMBER = "#22d3ee", "#8b5cf6", "#ec4899", "#fbbf24"
BG0, BG1 = "#070a17", "#120b2a"
C30 = math.cos(math.radians(30))


# ── fonts → paths ────────────────────────────────────────────────
class Font:
    def __init__(self, file):
        self.f = TTFont(FONTS / file)
        self.gs = self.f.getGlyphSet()
        self.cmap = self.f.getBestCmap()
        self.upm = self.f["head"].unitsPerEm
        self.hmtx = self.f["hmtx"]

    def _g(self, ch):
        return self.cmap.get(ord(ch), self.cmap.get(32))

    def width(self, s, size, ls=0.0):
        sc = size / self.upm
        return sum(self.hmtx[self._g(c)][0] * sc for c in s) + ls * max(0, len(s) - 1)

    def d(self, s, size, x, y, ls=0.0, anchor="start"):
        w = self.width(s, size, ls)
        x -= w / 2 if anchor == "middle" else w if anchor == "end" else 0
        pen = SVGPathPen(self.gs, ntos=lambda v: f"{v:.1f}".rstrip("0").rstrip("."))
        sc = size / self.upm
        for c in s:
            g = self._g(c)
            self.gs[g].draw(TransformPen(pen, (sc, 0, 0, -sc, x, y)))
            x += self.hmtx[g][0] * sc + ls
        return pen.getCommands()

    def wrap(self, text, size, maxw):
        lines, cur = [], ""
        for word in text.split():
            t = f"{cur} {word}".strip()
            if self.width(t, size) <= maxw:
                cur = t
            else:
                lines.append(cur)
                cur = word
        return lines + [cur] if cur else lines


DISPLAY = Font("unbounded-latin-900-normal.woff2")
DISPLAY7 = Font("unbounded-latin-700-normal.woff2")
BODY = Font("space-grotesk-latin-500-normal.woff2")
BODY7 = Font("space-grotesk-latin-700-normal.woff2")


# ── colour + iso helpers ─────────────────────────────────────────
def rgb(h):
    h = h.lstrip("#")
    return tuple(int(h[i:i + 2], 16) for i in (0, 2, 4))


def shade(h, f):
    """f>0 lighten toward white, f<0 darken toward black."""
    r, g, b = rgb(h)
    if f >= 0:
        r, g, b = (int(c + (255 - c) * f) for c in (r, g, b))
    else:
        r, g, b = (int(c * (1 + f)) for c in (r, g, b))
    return f"#{r:02x}{g:02x}{b:02x}"


def iso(x, y, z, ox, oy):
    return ox + (x - y) * C30, oy + (x + y) * 0.5 - z


def poly(pts, fill, extra=""):
    return f'<polygon points="{" ".join(f"{a:.1f},{b:.1f}" for a, b in pts)}" fill="{fill}" {extra}/>'


def box(x, y, z, w, d, h, color, ox, oy, top=None, edge=True):
    P = lambda a, b, c: iso(a, b, c, ox, oy)
    st = f'stroke="{shade(color, .45)}" stroke-opacity=".35" stroke-width=".8" stroke-linejoin="round"' if edge else ""
    return "".join([
        poly([P(x, y + d, z), P(x + w, y + d, z), P(x + w, y + d, z + h), P(x, y + d, z + h)], shade(color, -.18), st),
        poly([P(x + w, y, z), P(x + w, y + d, z), P(x + w, y + d, z + h), P(x + w, y, z + h)], shade(color, -.45), st),
        poly([P(x, y, z + h), P(x + w, y, z + h), P(x + w, y + d, z + h), P(x, y + d, z + h)], top or shade(color, .25), st),
    ])


def svg(w, h, label, defs, css, body):
    return (f'<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="{h}" viewBox="0 0 {w} {h}" '
            f'role="img" aria-label="{label}"><title>{label}</title><defs>{defs}</defs>'
            f'<style>{css}@media (prefers-reduced-motion:reduce){{*{{animation:none!important}}}}</style>{body}</svg>\n')


def arrow(x, y, s, color):
    return (f'<path d="M{x} {y}h{s}m-{s * .38:.1f}-{s * .38:.1f}l{s * .38:.1f} {s * .38:.1f}-{s * .38:.1f} {s * .38:.1f}" '
            f'fill="none" stroke="{color}" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round"/>')


BG_DEFS = f"""
<linearGradient id="bg" x1="0" y1="0" x2="1" y2="1"><stop offset="0" stop-color="{BG0}"/><stop offset="1" stop-color="{BG1}"/></linearGradient>
<radialGradient id="glowV" cx=".5" cy=".45" r=".55"><stop offset="0" stop-color="{VIOLET}" stop-opacity=".38"/><stop offset="1" stop-color="{VIOLET}" stop-opacity="0"/></radialGradient>
<radialGradient id="glowC" cx=".15" cy=".2" r=".5"><stop offset="0" stop-color="{CYAN}" stop-opacity=".22"/><stop offset="1" stop-color="{CYAN}" stop-opacity="0"/></radialGradient>
<radialGradient id="glowP" cx=".9" cy=".85" r=".5"><stop offset="0" stop-color="{PINK}" stop-opacity=".22"/><stop offset="1" stop-color="{PINK}" stop-opacity="0"/></radialGradient>
<linearGradient id="neon" x1="0" x2="1"><stop offset="0" stop-color="{CYAN}"/><stop offset=".5" stop-color="{VIOLET}"/><stop offset="1" stop-color="{PINK}"/></linearGradient>
"""


def stars(n, w, h, seed, ymax=None):
    rnd = random.Random(seed)
    out = []
    for i in range(n):
        x, y = rnd.uniform(10, w - 10), rnd.uniform(10, ymax or h - 10)
        r = rnd.choice([.6, .8, 1, 1.2, 1.6])
        out.append(f'<circle cx="{x:.0f}" cy="{y:.0f}" r="{r}" fill="#fff" class="tw" '
                   f'style="animation-delay:-{rnd.uniform(0, 4):.1f}s;animation-duration:{rnd.uniform(2.5, 5):.1f}s"/>')
    return "".join(out)


STAR_CSS = ".tw{animation:tw 4s ease-in-out infinite;opacity:.25}@keyframes tw{50%{opacity:1}}"


# ── HERO ─────────────────────────────────────────────────────────
def hero(m=False):
    W, H = (600, 600) if m else (900, 400)
    size = 132
    cx, base = W / 2, (236 if m else 196)
    nd = DISPLAY.d(NAME, size, cx, base, ls=10, anchor="middle")
    nw = DISPLAY.width(NAME, size, 10)

    # isometric floor grid
    ox, oy = W / 2, (430 if m else 238)
    grid = []
    for i in range(-9, 10):
        a, b = iso(i * 40, -360, 0, ox, oy), iso(i * 40, 360, 0, ox, oy)
        grid.append(f'<line x1="{a[0]:.0f}" y1="{a[1]:.0f}" x2="{b[0]:.0f}" y2="{b[1]:.0f}"/>')
        a, b = iso(-360, i * 40, 0, ox, oy), iso(360, i * 40, 0, ox, oy)
        grid.append(f'<line x1="{a[0]:.0f}" y1="{a[1]:.0f}" x2="{b[0]:.0f}" y2="{b[1]:.0f}"/>')

    layers = 18
    extrude = "".join(
        f'<use href="#nm" transform="translate({i * .55:.2f} {i * .9:.2f})" fill="{shade("#3b1d8f", -i / layers * .7)}"/>'
        for i in range(layers, 0, -1))

    # floating cubes: (screen x, screen y, size, colour, delay)
    cubes = ([(70, 64, 30, CYAN, 0), (520, 56, 26, PINK, -.8), (64, 300, 20, PINK, -1.6),
              (540, 296, 22, AMBER, -2.4), (90, 500, 18, VIOLET, -3.1), (515, 505, 20, CYAN, -1.1)] if m else
             [(110, 120, 34, CYAN, 0), (140, 238, 22, PINK, -1.6), (790, 110, 30, PINK, -.8),
              (772, 236, 24, AMBER, -2.4), (70, 300, 16, VIOLET, -3.1), (840, 300, 18, CYAN, -1.1)])
    cube_svg = []
    for x, y, s, col, dl in cubes:
        cube_svg.append(
            f'<ellipse cx="{x}" cy="{y + s * 1.9:.0f}" rx="{s * .9:.0f}" ry="{s * .28:.0f}" fill="#000" opacity=".45" '
            f'class="sh" style="animation-delay:{dl}s"/>'
            f'<g class="bob" style="animation-delay:{dl}s">{box(-s / 2, -s / 2, 0, s, s, s, col, x, y + s * .5)}</g>')

    # orbit ring: ellipse split into back/front halves, sphere travels around
    rx, ry, ocy = nw / 2 + 70, 46, base - size * .36
    back = f"M{cx - rx:.1f} {ocy} A{rx:.1f} {ry} 0 0 1 {cx + rx:.1f} {ocy}"
    front = f"M{cx + rx:.1f} {ocy} A{rx:.1f} {ry} 0 0 1 {cx - rx:.1f} {ocy}"
    motion = back + f" A{rx:.1f} {ry} 0 0 1 {cx - rx:.1f} {ocy}"
    T = 7
    sphere = lambda r, vis: (
        f'<circle r="{r}" fill="url(#orb)" opacity="0">'
        f'<animateMotion dur="{T}s" repeatCount="indefinite" path="{motion}"/>'
        f'<animate attributeName="opacity" dur="{T}s" repeatCount="indefinite" calcMode="discrete" '
        f'keyTimes="0;.5" values="{vis}"/></circle>')

    if m:
        parts_ = [t.strip() for t in TAGLINE.split("·")]
        lines = [parts_[0], "  ·  ".join(parts_[1:])] if len(parts_) > 1 else parts_
        tag = " ".join(BODY7.d(l, 23, cx, 330 + i * 34, ls=3.5, anchor="middle") for i, l in enumerate(lines))
        sub = BODY.d(SUBLINE, 19, cx, 330 + len(lines) * 34 + 12, ls=.6, anchor="middle")
    else:
        tag = BODY7.d(TAGLINE, 15.5, cx, 272, ls=3.2, anchor="middle")
        sub = BODY.d(SUBLINE, 14, cx, 298, ls=.6, anchor="middle")

    defs = BG_DEFS + f"""
<path id="nm" d="{nd}"/>
<linearGradient id="face" gradientUnits="userSpaceOnUse" x1="{cx - nw / 2}" y1="0" x2="{cx + nw / 2}" y2="0">
 <stop offset="0" stop-color="{CYAN}"/><stop offset=".5" stop-color="#c4b5fd"/><stop offset="1" stop-color="{PINK}"/></linearGradient>
<linearGradient id="shine" gradientUnits="userSpaceOnUse" x1="0" y1="0" x2="160" y2="0">
 <stop offset="0" stop-color="#fff" stop-opacity="0"/><stop offset=".5" stop-color="#fff" stop-opacity=".75"/><stop offset="1" stop-color="#fff" stop-opacity="0"/>
 <animateTransform attributeName="gradientTransform" type="translate" values="-200 0;1100 0;1100 0" keyTimes="0;.45;1" dur="5s" repeatCount="indefinite"/></linearGradient>
<radialGradient id="orb" cx=".35" cy=".35" r=".7"><stop offset="0" stop-color="#fff"/><stop offset=".35" stop-color="{CYAN}"/><stop offset="1" stop-color="{VIOLET}"/></radialGradient>
<radialGradient id="fade" cx=".5" cy=".8" r=".62"><stop offset=".25" stop-color="#fff"/><stop offset="1" stop-color="#fff" stop-opacity="0"/></radialGradient>
<linearGradient id="vfade" x1="0" y1="0" x2="0" y2="1"><stop offset="{.7 if m else .56}" stop-color="#fff" stop-opacity="0"/><stop offset="{.92 if m else .86}" stop-color="#fff"/></linearGradient>
<mask id="gm"><rect width="{W}" height="{H}" fill="url(#fade)"/></mask>
<mask id="gv"><rect width="{W}" height="{H}" fill="url(#vfade)"/></mask>
<clipPath id="card"><rect width="{W}" height="{H}" rx="22"/></clipPath>
<filter id="blur" x="-50%" y="-50%" width="200%" height="200%"><feGaussianBlur stdDeviation="10"/></filter>
"""
    css = STAR_CSS + """
.fl{animation:fl 6s ease-in-out infinite}@keyframes fl{50%{transform:translateY(-8px)}}
.bob{animation:bob 4.5s ease-in-out infinite}@keyframes bob{50%{transform:translateY(-14px)}}
.sh{transform-box:fill-box;transform-origin:center;animation:sh 4.5s ease-in-out infinite}@keyframes sh{50%{transform:scale(.7);opacity:.2}}
.nsh{transform-box:fill-box;transform-origin:center;animation:nsh 6s ease-in-out infinite}@keyframes nsh{50%{transform:scale(.88);opacity:.35}}
.grid{animation:gr 8s linear infinite}@keyframes gr{to{transform:translate(34.64px,20px)}}
.pulse{animation:pu 3s ease-in-out infinite}@keyframes pu{50%{opacity:.55}}
"""
    body = f"""
<g clip-path="url(#card)">
 <rect width="{W}" height="{H}" fill="url(#bg)"/>
 <rect width="{W}" height="{H}" fill="url(#glowC)"/><rect width="{W}" height="{H}" fill="url(#glowP)"/>
 <ellipse cx="{cx}" cy="{base - 26}" rx="{280 if m else 330}" ry="{170 if m else 150}" fill="url(#glowV)"/>
 {stars(70, W, H, 3, 290 if m else 230)}
 <g mask="url(#gv)"><g mask="url(#gm)"><g class="grid" stroke="{VIOLET}" stroke-opacity=".55" stroke-width="1">{''.join(grid)}</g></g></g>
 <path d="{back}" fill="none" stroke="url(#neon)" stroke-width="2" opacity=".45"/>
 {sphere(7, "1;0")}
 <ellipse cx="{cx}" cy="{base + 30}" rx="{nw / 2 + 10:.0f}" ry="16" fill="#000" opacity=".55" class="nsh" filter="url(#blur)"/>
 <g class="fl">
  {extrude}
  <use href="#nm" fill="url(#face)"/>
  <use href="#nm" fill="url(#shine)"/>
 </g>
 <path d="{front}" fill="none" stroke="url(#neon)" stroke-width="2.6" class="pulse"/>
 {sphere(10, "0;1")}
 {''.join(cube_svg)}
 <path d="{tag}" fill="#e9e3ff"/>
 <path d="{sub}" fill="#94a3b8"/>
</g>
<rect x=".75" y=".75" width="{W - 1.5}" height="{H - 1.5}" rx="22" fill="none" stroke="url(#neon)" stroke-opacity=".5" stroke-width="1.5"/>
"""
    return svg(W, H, f"{NAME} — {TAGLINE.title()} — {SUBLINE}", defs, css, body)


# ── SECTION TITLES ───────────────────────────────────────────────
def title(text, file, m=False):
    W, H = (560, 76) if m else (900, 76)
    size, ls = 24, 7
    cx, base = W / 2, 48
    d = DISPLAY.d(text, size, cx, base, ls=ls, anchor="middle")
    tw = DISPLAY.width(text, size, ls)
    ext = "".join(f'<use href="#t" transform="translate({i * .5:.1f} {i * .8:.1f})" fill="{shade("#4c1d95", -i / 8)}"/>'
                  for i in range(7, 0, -1))
    l1, l2 = cx - tw / 2 - 36, cx + tw / 2 + 36
    defs = BG_DEFS + f"""<path id="t" d="{d}"/>
<linearGradient id="lf" x1="1" x2="0"><stop offset="0" stop-color="{CYAN}"/><stop offset="1" stop-color="{CYAN}" stop-opacity="0"/></linearGradient>
<linearGradient id="rf" x1="0" x2="1"><stop offset="0" stop-color="{PINK}"/><stop offset="1" stop-color="{PINK}" stop-opacity="0"/></linearGradient>
<linearGradient id="tf" gradientUnits="userSpaceOnUse" x1="{cx - tw / 2}" x2="{cx + tw / 2}"><stop offset="0" stop-color="{CYAN}"/><stop offset=".5" stop-color="#ddd6fe"/><stop offset="1" stop-color="{PINK}"/></linearGradient>"""
    css = """.dot{animation:dt 3s ease-in-out infinite}@keyframes dt{0%{transform:translateX(0);opacity:0}15%,85%{opacity:1}100%{transform:translateX(var(--dx));opacity:0}}
.spin{transform-box:fill-box;transform-origin:center;animation:sp 6s ease-in-out infinite}@keyframes sp{50%{transform:translateY(-4px) }}"""
    cube_l = box(-7, -7, 0, 14, 14, 14, CYAN, l1 + 4, base - 6)
    cube_r = box(-7, -7, 0, 14, 14, 14, PINK, l2 - 4, base - 6)
    body = f"""
<rect x="{12 if m else 40}" y="{base - 10}" width="{l1 - 14 - (12 if m else 40):.1f}" height="2" rx="1" fill="url(#lf)"/>
<rect x="{l2 + 14:.1f}" y="{base - 10}" width="{W - (12 if m else 40) - 14 - l2:.1f}" height="2" rx="1" fill="url(#rf)"/>
<circle cx="{l1 - 14}" cy="{base - 9}" r="3" fill="{CYAN}" class="dot" style="--dx:-{l1 - 60:.0f}px"/>
<circle cx="{l2 + 14}" cy="{base - 9}" r="3" fill="{PINK}" class="dot" style="--dx:{W - 60 - l2:.0f}px;animation-delay:-1.5s"/>
<g class="spin">{cube_l}</g><g class="spin" style="animation-delay:-3s">{cube_r}</g>
{ext}<use href="#t" fill="url(#tf)"/>
"""
    (ASSETS / file).write_text(svg(W, H, text.title(), defs, css, body), encoding="utf-8")


# ── SKILL BLOCKS ─────────────────────────────────────────────────
def skills(m=False):
    W = 560 if m else 900
    per_row = 5 if m else len(SKILLS)
    rows = [SKILLS[k:k + per_row] for k in range(0, len(SKILLS), per_row)]
    s_ = 48 if m else 40
    row_h = 178 if m else 0
    H = (90 + row_h * len(rows)) if m else 210
    parts = []
    for r, row in enumerate(rows):
        oy = (112 if not m else 118 + r * row_h)
        gap = (W - (40 if m else 80)) / len(row)
        x0 = 20 if m else 40
        pw = W - (30 if m else 60)
        px = 15 if m else 30
        parts.append(f'<rect x="{px}" y="{oy + 34}" width="{pw}" height="14" rx="7" fill="url(#neon)" opacity=".18"/>'
                     f'<rect x="{px}" y="{oy + 30}" width="{pw}" height="6" rx="3" fill="url(#neon)" opacity=".55"/>')
        for i, (label, col) in enumerate(row):
            k = r * per_row + i
            x = x0 + gap * (i + .5)
            dl = -k * .28
            by = oy - s_ * .1
            parts.append(
                f'<ellipse cx="{x:.1f}" cy="{oy + 33}" rx="{s_ * .9:.0f}" ry="5" fill="#000" opacity=".5" class="sh" style="animation-delay:{dl:.2f}s"/>'
                f'<g class="bob" style="animation-delay:{dl:.2f}s">{box(-s_ / 2, -s_ / 2, 0, s_, s_, s_, col, x, by)}'
                f'{poly([iso(-s_ / 2 + 6, -s_ / 2 + 6, s_, x, by), iso(-s_ / 2 + 18, -s_ / 2 + 6, s_, x, by), iso(-s_ / 2 + 6, -s_ / 2 + 18, s_, x, by)], "#fff", 'opacity=".35"')}</g>'
                f'<path d="{BODY7.d(label, 16 if m else 13, x, oy + (74 if m else 68), ls=.5, anchor="middle")}" fill="#cbd5e1"/>')
    defs = BG_DEFS + f'<clipPath id="card"><rect width="{W}" height="{H}" rx="22"/></clipPath>'
    css = STAR_CSS + """
.bob{animation:bob 2.8s ease-in-out infinite}@keyframes bob{50%{transform:translateY(-16px)}}
.sh{transform-box:fill-box;transform-origin:center;animation:sh 2.8s ease-in-out infinite}@keyframes sh{50%{transform:scale(.6);opacity:.15}}"""
    body = f"""<g clip-path="url(#card)"><rect width="{W}" height="{H}" fill="url(#bg)"/>
<rect width="{W}" height="{H}" fill="url(#glowC)"/><rect width="{W}" height="{H}" fill="url(#glowP)"/>{stars(26, W, 60 if m else 120, 9)}
{''.join(parts)}</g>
<rect x=".75" y=".75" width="{W - 1.5}" height="{H - 1.5}" rx="22" fill="none" stroke="url(#neon)" stroke-opacity=".4" stroke-width="1.5"/>"""
    (ASSETS / ("skills-m.svg" if m else "skills.svg")).write_text(
        svg(W, H, "Tech stack: " + ", ".join(l for l, _ in SKILLS), defs, css, body), encoding="utf-8")

def icon(kind, ox, oy, accent):
    if kind == "papers":
        out = ""
        for i, z in enumerate((0, 12, 24)):
            cls = ' class="lift"' if i == 2 else ""
            out += f"<g{cls}>{box(-34, -26, z, 68, 52, 7, shade('#e2e8f0', -.05 * (2 - i)), ox, oy)}"
            if i == 2:
                for k in range(4):
                    a, b = iso(-26, -18 + k * 10, z + 7, ox, oy), iso(18 - k * 7, -18 + k * 10, z + 7, ox, oy)
                    c = accent if k == 1 else "#94a3b8"
                    out += f'<line x1="{a[0]:.1f}" y1="{a[1]:.1f}" x2="{b[0]:.1f}" y2="{b[1]:.1f}" stroke="{c}" stroke-width="2.4" stroke-linecap="round"/>'
            out += "</g>"
        out += f'<g class="lift2">{box(14, -40, 46, 14, 14, 14, PINK, ox, oy)}</g>'
        return out
    if kind == "chat":
        out = f'<g class="lift">{box(-40, -24, 6, 64, 40, 16, VIOLET, ox, oy)}'
        for k in range(3):
            px, py = iso(-26 + k * 16, -4, 22, ox, oy)
            out += f'<ellipse cx="{px:.1f}" cy="{py:.1f}" rx="4.5" ry="2.6" fill="#fff" class="typing" style="animation-delay:{k * .2:.1f}s"/>'
        out += "</g>"
        out += f'<g class="lift2">{box(-4, -34, 46, 34, 24, 12, CYAN, ox, oy)}</g>'
        return out
    if kind == "bars":
        out = box(-44, -30, 0, 88, 60, 5, "#1e293b", ox, oy, edge=False)
        hs = [26, 48, 34, 70]
        for k, h in enumerate(hs):
            col = "#22c55e" if k in (1, 3) else "#ef4444"
            bx = -36 + k * 20
            top_y = iso(bx, -6, 5 + h, ox, oy)[1] - 14
            bot_y = iso(bx + 14, 8, 0, ox, oy)[1] + 4
            out += (f'<clipPath id="bc{k}"><rect x="{ox - 80}" y="{bot_y}" width="160" height="0">'
                    f'<animate attributeName="y" dur="4s" repeatCount="indefinite" keyTimes="0;.35;.85;1" '
                    f'values="{bot_y:.0f};{top_y:.0f};{top_y:.0f};{bot_y:.0f}" begin="{k * .15:.2f}s"/>'
                    f'<animate attributeName="height" dur="4s" repeatCount="indefinite" keyTimes="0;.35;.85;1" '
                    f'values="0;{bot_y - top_y:.0f};{bot_y - top_y:.0f};0" begin="{k * .15:.2f}s"/></rect></clipPath>'
                    f'<g clip-path="url(#bc{k})">{box(bx, -6, 5, 14, 14, h, col, ox, oy)}</g>')
        return out
    if kind == "bridge":
        out = box(-50, -14, 0, 28, 28, 28, CYAN, ox, oy)
        out += box(22, -14, 0, 28, 28, 28, PINK, ox, oy)
        out += box(-22, -5, 18, 44, 10, 4, "#64748b", ox, oy)
        a, b = iso(-22, 0, 24, ox, oy), iso(22, 0, 24, ox, oy)
        out += (f'<circle r="5" fill="{AMBER}"><animateMotion dur="1.8s" repeatCount="indefinite" '
                f'path="M{a[0]:.1f} {a[1]:.1f} L{b[0]:.1f} {b[1]:.1f}"/></circle>')
        px, py = iso(36, 0, 44, ox, oy)
        for k in range(3):
            out += (f'<path d="M{px + 8 + k * 7:.1f} {py - 8 - k * 3:.1f} q6 {8 + k * 3} 0 {16 + k * 6}" fill="none" '
                    f'stroke="{AMBER}" stroke-width="2" stroke-linecap="round" class="wave" style="animation-delay:{k * .25:.2f}s"/>')
        return out
    return ""


def card(stem, kicker, ttl, desc, tags, kind, accent, idx):
    """One 440x250 project card → (defs, css, body) with ids/classes made unique by idx."""
    x0, y0, cw, ch = 10, 8, 414, 222
    lines = BODY.wrap(desc, 13.5, 236)[:4]
    text = "".join(f'<path d="{BODY.d(l, 13.5, 34, 104 + i * 20)}" fill="#a8b3c7"/>' for i, l in enumerate(lines))
    chips, cx = [], 34
    for t in tags:
        w = BODY7.width(t, 11, .4) + 18
        chips.append(f'<rect x="{cx}" y="190" width="{w:.1f}" height="22" rx="11" fill="{accent}" fill-opacity=".12" stroke="{accent}" stroke-opacity=".5"/>'
                     f'<path d="{BODY7.d(t, 11, cx + w / 2, 205, ls=.4, anchor="middle")}" fill="{shade(accent, .35)}"/>')
        cx += w + 7
    shared = f"""
<linearGradient id="cb" x1="0" y1="0" x2="1" y2="1"><stop offset="0" stop-color="#141a35"/><stop offset="1" stop-color="#1a1036"/></linearGradient>
<linearGradient id="ed" x1="0" x2="1"><stop offset="0" stop-color="{CYAN}"/><stop offset=".5" stop-color="{VIOLET}"/><stop offset="1" stop-color="{PINK}"/></linearGradient>
"""
    defs = (shared if idx == 0 else "") + f"""<radialGradient id="ig{idx}" cx=".5" cy=".5" r=".5"><stop offset="0" stop-color="{accent}" stop-opacity=".35"/><stop offset="1" stop-color="{accent}" stop-opacity="0"/></radialGradient>
"""
    if idx == 0:
        defs += '<filter id="gl" x="-10%" y="-10%" width="120%" height="120%"><feGaussianBlur stdDeviation="3"/></filter>'
    per = 2 * (cw + ch)
    css = f"""
.card{idx}{{animation:fl 6s ease-in-out infinite;animation-delay:-{idx * 1.5}s}}@keyframes fl{{50%{{transform:translateY(-5px)}}}}
.run{idx}{{stroke-dasharray:140 {per - 140};animation:run{idx} 6s linear infinite;animation-delay:-{idx * 1.2}s}}@keyframes run{idx}{{to{{stroke-dashoffset:-{per}}}}}
.lift{{animation:lf 3.2s ease-in-out infinite}}@keyframes lf{{50%{{transform:translateY(-7px)}}}}
.lift2{{animation:lf 3.2s ease-in-out infinite;animation-delay:-1.6s}}
.typing{{animation:ty 1.2s ease-in-out infinite}}@keyframes ty{{0%,100%{{opacity:.25}}40%{{opacity:1}}}}
.wave{{animation:ty 1.2s ease-in-out infinite}}
"""
    body = f"""
<g class="card{idx}">
 <rect x="{x0 + 6}" y="{y0 + 12}" width="{cw}" height="{ch}" rx="20" fill="#05060f"/>
 <rect x="{x0 + 3}" y="{y0 + 6}" width="{cw}" height="{ch}" rx="20" fill="{shade(accent, -.75)}"/>
 <rect x="{x0}" y="{y0}" width="{cw}" height="{ch}" rx="20" fill="url(#cb)" stroke="#2a2f55"/>
 <rect x="{x0}" y="{y0}" width="{cw}" height="{ch}" rx="20" fill="none" stroke="url(#ed)" stroke-width="3" class="run{idx}" filter="url(#gl)"/>
 <rect x="{x0}" y="{y0}" width="{cw}" height="{ch}" rx="20" fill="none" stroke="url(#ed)" stroke-width="1.5" class="run{idx}"/>
 <circle cx="352" cy="104" r="78" fill="url(#ig{idx})"/>
 {icon(kind, 352, 122, accent)}
 <path d="{BODY7.d(kicker, 10.5, 34, 44, ls=1.6)}" fill="{accent}"/>
 <path d="{DISPLAY7.d(ttl, 19, 34, 74)}" fill="#f8fafc"/>
 {text}
 {''.join(chips)}
 <path d="{BODY7.d('VIEW', 11, 386, 205, ls=1.4, anchor='end')}" fill="#e2e8f0"/>
 {arrow(392, 201, 11, '#e2e8f0')}
</g>"""
    return defs, css, body


# ── FEATURED PROJECT (hand-tracking card) ───────────────────────
HAND = {  # open-palm landmarks, wrist at origin, y up = negative
    0: (0, 0), 1: (-30, -20), 2: (-52, -45), 3: (-68, -68), 4: (-80, -90),
    5: (-20, -72), 6: (-24, -106), 7: (-26, -129), 8: (-28, -150),
    9: (0, -76), 10: (1, -114), 11: (2, -139), 12: (3, -161),
    13: (19, -71), 14: (23, -105), 15: (26, -127), 16: (28, -146),
    17: (35, -61), 18: (43, -87), 19: (48, -105), 20: (52, -122),
}
BONES = [(0, 1), (1, 2), (2, 3), (3, 4), (0, 5), (5, 6), (6, 7), (7, 8), (5, 9), (9, 10), (10, 11), (11, 12),
         (9, 13), (13, 14), (14, 15), (15, 16), (13, 17), (0, 17), (17, 18), (18, 19), (19, 20)]
TIPS = (4, 8, 12, 16, 20)


def hand(ox, oy, sc):
    P = {k: (ox + x * sc, oy + y * sc) for k, (x, y) in HAND.items()}
    bones = "".join(f'<line x1="{P[a][0]:.1f}" y1="{P[a][1]:.1f}" x2="{P[b][0]:.1f}" y2="{P[b][1]:.1f}"/>' for a, b in BONES)
    joints = "".join(f'<circle cx="{P[k][0]:.1f}" cy="{P[k][1]:.1f}" r="{4 * sc:.1f}"/>' for k in P if k not in TIPS)
    tips = "".join(f'<circle cx="{P[k][0]:.1f}" cy="{P[k][1]:.1f}" r="{6 * sc:.1f}"/>' for k in TIPS)
    pings = "".join(f'<circle cx="{P[k][0]:.1f}" cy="{P[k][1]:.1f}" r="{6 * sc:.1f}" class="ping" style="animation-delay:{i * .3:.1f}s"/>'
                    for i, k in enumerate(TIPS))
    origin = f"transform-origin:{ox:.1f}px {oy:.1f}px"
    trail = lambda d, o: f'<g class="sway" style="{origin};animation-delay:{d}s" opacity="{o}" fill="{PINK}">{tips}</g>'
    return (f'<ellipse cx="{ox}" cy="{oy - 80 * sc:.1f}" rx="{110 * sc:.0f}" ry="{120 * sc:.0f}" fill="url(#hg)"/>'
            + trail(-.36, .12) + trail(-.24, .2) + trail(-.12, .32)
            + f'<g class="sway" style="{origin}">'
              f'<g stroke="url(#bone)" stroke-width="{3.2 * sc:.1f}" stroke-linecap="round">{bones}</g>'
              f'<g fill="#e0f2fe">{joints}</g><g fill="{PINK}" filter="url(#tipglow)">{tips}</g>'
              f'<g fill="none" stroke="{PINK}">{pings}</g></g>')


def featured(m=False):
    F = FEATURED
    acc = F["accent"]
    if m:
        W, H = 440, 540
        x0, y0, cw, ch = 10, 8, 414, 512
        hx, hy, hs = 205, 236, .9
        bx, by = 262, 52
        tx, ty, tw = 34, 296, 360
    else:
        W, H = 900, 300
        x0, y0, cw, ch = 10, 8, 874, 272
        hx, hy, hs = 720, 254, 1.0
        bx, by = 772, 44
        tx, ty, tw = 40, 52, 470
    k_y, t_y, s_y = ty, ty + (46 if m else 50), ty + (76 if m else 82)
    d_y = s_y + 32
    lines = BODY.wrap(F["desc"], 14, tw)[:4]
    desc = "".join(f'<path d="{BODY.d(l, 14, tx, d_y + i * 21)}" fill="#a8b3c7"/>' for i, l in enumerate(lines))
    chip_y = d_y + len(lines) * 21 + 12
    chips, cx = [], tx
    for t in F["tags"]:
        w = BODY7.width(t, 11.5, .4) + 20
        chips.append(f'<rect x="{cx:.1f}" y="{chip_y}" width="{w:.1f}" height="24" rx="12" fill="{acc}" fill-opacity=".12" stroke="{acc}" stroke-opacity=".5"/>'
                     f'<path d="{BODY7.d(t, 11.5, cx + w / 2, chip_y + 16, ls=.4, anchor="middle")}" fill="{shade(acc, .4)}"/>')
        cx += w + 7
    if m:  # grow the card to fit the text, put VIEW REPO under the chips
        view_x, view_y = x0 + cw - 6, chip_y + 58
        ch = view_y + 26 - y0
        H = y0 + ch + 18
    else:
        view_x, view_y = tx + tw + 30, chip_y + 16
    # sign bubble with a hold-to-add ring
    bw_ = BODY7.width(F["sign"], 16, 1.5) + 92
    bx = min(bx, x0 + cw - bw_ - 22)
    bubble = (f'<g class="pop">'
              f'<rect x="{bx}" y="{by}" width="{bw_:.0f}" height="44" rx="22" fill="#0b1224" fill-opacity=".85" stroke="{acc}" stroke-opacity=".6"/>'
              f'<circle cx="{bx + 22}" cy="{by + 22}" r="11" fill="none" stroke="#1f2a44" stroke-width="3.5"/>'
              f'<circle cx="{bx + 22}" cy="{by + 22}" r="11" fill="none" stroke="{acc}" stroke-width="3.5" stroke-linecap="round" '
              f'pathLength="1" class="hold" transform="rotate(-90 {bx + 22} {by + 22})"/>'
              f'<path d="{BODY7.d(F["sign"], 16, bx + 42, by + 28, ls=1.5)}" fill="#f8fafc"/>'
              f'<path d="{BODY.d(F["conf"], 12, bx + bw_ - 14, by + 27, anchor="end")}" fill="{acc}"/></g>')
    per = 2 * (cw + ch)
    defs = f"""
<linearGradient id="fcb" x1="0" y1="0" x2="1" y2="1"><stop offset="0" stop-color="#0f1d2e"/><stop offset=".55" stop-color="#141a35"/><stop offset="1" stop-color="#1a1036"/></linearGradient>
<linearGradient id="fed" x1="0" x2="1"><stop offset="0" stop-color="{acc}"/><stop offset=".5" stop-color="{CYAN}"/><stop offset="1" stop-color="{VIOLET}"/></linearGradient>
<linearGradient id="bone" x1="0" y1="1" x2="0" y2="0"><stop offset="0" stop-color="{CYAN}"/><stop offset="1" stop-color="{VIOLET}"/></linearGradient>
<radialGradient id="hg" cx=".5" cy=".5" r=".5"><stop offset="0" stop-color="{acc}" stop-opacity=".22"/><stop offset="1" stop-color="{acc}" stop-opacity="0"/></radialGradient>
<filter id="tipglow" x="-100%" y="-100%" width="300%" height="300%"><feGaussianBlur stdDeviation="2.2" result="b"/><feMerge><feMergeNode in="b"/><feMergeNode in="SourceGraphic"/></feMerge></filter>
<filter id="fgl" x="-10%" y="-10%" width="120%" height="120%"><feGaussianBlur stdDeviation="3"/></filter>
<pattern id="dots" width="18" height="18" patternUnits="userSpaceOnUse"><circle cx="2" cy="2" r="1" fill="#fff" opacity=".05"/></pattern>"""
    css = f"""
.card{{animation:fl 6s ease-in-out infinite}}@keyframes fl{{50%{{transform:translateY(-5px)}}}}
.run{{stroke-dasharray:180 {per - 180};animation:run 7s linear infinite}}@keyframes run{{to{{stroke-dashoffset:-{per}}}}}
.sway{{animation:sw 4s ease-in-out infinite}}@keyframes sw{{0%,100%{{transform:rotate(-5deg)}}50%{{transform:rotate(5deg)}}}}
.ping{{transform-box:fill-box;transform-origin:center;opacity:0;animation:pg 2s ease-out infinite}}@keyframes pg{{0%{{opacity:.9;transform:scale(1)}}100%{{opacity:0;transform:scale(2.8)}}}}
.hold{{stroke-dasharray:1;stroke-dashoffset:1;animation:hd 2.4s ease-in-out infinite}}@keyframes hd{{0%{{stroke-dashoffset:1}}70%,100%{{stroke-dashoffset:0}}}}
.pop{{animation:po 2.4s ease-in-out infinite}}@keyframes po{{0%,70%{{transform:none}}80%{{transform:translateY(-3px)}}100%{{transform:none}}}}
.live{{animation:lv 1.4s ease-in-out infinite}}@keyframes lv{{50%{{opacity:.3}}}}"""
    live_txt = "LIVE  ·  21 LANDMARKS"
    if m:
        rec_x, rec_y = x0 + 26, y0 + 34
    else:
        rec_x, rec_y = 560, y0 + 34
    body = f"""
<g class="card">
 <rect x="{x0 + 6}" y="{y0 + 12}" width="{cw}" height="{ch}" rx="22" fill="#05060f"/>
 <rect x="{x0 + 3}" y="{y0 + 6}" width="{cw}" height="{ch}" rx="22" fill="{shade(acc, -.75)}"/>
 <rect x="{x0}" y="{y0}" width="{cw}" height="{ch}" rx="22" fill="url(#fcb)" stroke="#24304f"/>
 <rect x="{x0}" y="{y0}" width="{cw}" height="{ch}" rx="22" fill="url(#dots)"/>
 <rect x="{x0}" y="{y0}" width="{cw}" height="{ch}" rx="22" fill="none" stroke="url(#fed)" stroke-width="3" class="run" filter="url(#fgl)"/>
 <rect x="{x0}" y="{y0}" width="{cw}" height="{ch}" rx="22" fill="none" stroke="url(#fed)" stroke-width="1.6" class="run"/>
 {hand(hx, hy, hs)}
 {bubble}
 <circle cx="{rec_x:.1f}" cy="{rec_y}" r="4" fill="#ef4444" class="live"/>
 <path d="{BODY7.d(live_txt, 10, rec_x + 10, rec_y + 4, ls=1.2)}" fill="#64748b"/>
 <path d="{BODY7.d(F['kicker'], 11, tx, k_y, ls=1.8)}" fill="{acc}"/>
 <path d="{DISPLAY.d(F['title'], 40 if not m else 36, tx, t_y, ls=1)}" fill="#f8fafc"/>
 <path d="{BODY7.d(F['subtitle'], 17, tx, s_y, ls=.3)}" fill="#e2e8f0"/>
 {desc}
 {''.join(chips)}
 <path d="{BODY7.d('VIEW REPO', 11.5, view_x - 18, view_y, ls=1.4, anchor='end')}" fill="#e2e8f0"/>
 {arrow(view_x - 12, view_y - 4, 11, '#e2e8f0')}
</g>"""
    (ASSETS / ("featured-m.svg" if m else "featured.svg")).write_text(
        svg(W, H, f"Featured project — {F['title']}: {F['subtitle']}. {F['desc']}", defs, css, body), encoding="utf-8")


# ── ENTER-3D BUTTON ──────────────────────────────────────────────

def projects(m=False):
    W, H = (440, 4 * 256 + 4) if m else (900, 520)
    defs, css, body = [], [], []
    for i, p in enumerate(PROJECTS):
        d, c, b = card(*p, idx=i)
        x, y = (0, i * 256) if m else ((i % 2) * 455 + 2, (i // 2) * 262)
        defs.append(d); css.append(c)
        body.append(f'<g transform="translate({x} {y})">{b}</g>')
    label = "Projects: " + "; ".join(f"{p[2]} — {p[3]}" for p in PROJECTS)
    (ASSETS / ("projects-m.svg" if m else "projects.svg")).write_text(
        svg(W, H, label, "".join(defs), "".join(css), "".join(body)), encoding="utf-8")

def button(m=False):
    W, H = (560, 170) if m else (900, 140)
    bw, bh, depth = (500, 84, 12) if m else (520, 66, 10)
    bx, by = (W - bw) / 2, 26
    label = "ENTER 3D PORTFOLIO" if m else "ENTER THE 3D PORTFOLIO"
    fs = 22 if m else 17
    ld = DISPLAY7.d(label, fs, W / 2 - 14, by + bh / 2 + fs * .38, ls=2.2, anchor="middle")
    lw = DISPLAY7.width(label, fs, 2.2)
    hint_txt = "drag  ·  orbit  ·  tap a planet" if m else "drag to orbit  ·  click planets to open projects  ·  works on mobile"
    hint = BODY.d(hint_txt, 17 if m else 12.5, W / 2, by + bh + depth + (36 if m else 30), ls=.6, anchor="middle")
    defs = f"""
<linearGradient id="kt" x1="0" x2="1"><stop offset="0" stop-color="{CYAN}"/><stop offset=".5" stop-color="{VIOLET}"/><stop offset="1" stop-color="{PINK}"/></linearGradient>
<linearGradient id="ks" x1="0" x2="1"><stop offset="0" stop-color="#0e7490"/><stop offset=".5" stop-color="#4c1d95"/><stop offset="1" stop-color="#9d174d"/></linearGradient>
<linearGradient id="gloss" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#fff" stop-opacity=".45"/><stop offset=".5" stop-color="#fff" stop-opacity="0"/></linearGradient>
<linearGradient id="sw" gradientUnits="userSpaceOnUse" x1="0" x2="120"><stop offset="0" stop-color="#fff" stop-opacity="0"/><stop offset=".5" stop-color="#fff" stop-opacity=".55"/><stop offset="1" stop-color="#fff" stop-opacity="0"/>
 <animateTransform attributeName="gradientTransform" type="translate" values="{bx - 140} 0;{bx + bw + 20} 0;{bx + bw + 20} 0" keyTimes="0;.4;1" dur="3.5s" repeatCount="indefinite"/></linearGradient>
<filter id="bl" x="-20%" y="-60%" width="140%" height="220%"><feGaussianBlur stdDeviation="16"/></filter>
<clipPath id="kc"><rect x="{bx}" y="{by}" width="{bw}" height="{bh}" rx="18"/></clipPath>"""
    css = f""".press{{animation:pr 3.5s ease-in-out infinite}}@keyframes pr{{0%,78%,100%{{transform:none}}84%{{transform:translateY({depth - 3}px)}}}}
.halo{{animation:ha 3.5s ease-in-out infinite}}@keyframes ha{{0%,100%{{opacity:.45}}84%{{opacity:.9}}}}
.nudge{{animation:nu 1.2s ease-in-out infinite}}@keyframes nu{{50%{{transform:translateX(5px)}}}}"""
    ax = W / 2 + lw / 2 - 2
    body = f"""
<rect x="{bx + 20}" y="{by + 14}" width="{bw - 40}" height="{bh}" rx="30" fill="url(#kt)" filter="url(#bl)" class="halo"/>
<rect x="{bx}" y="{by + depth}" width="{bw}" height="{bh}" rx="18" fill="url(#ks)"/>
<g class="press">
 <rect x="{bx}" y="{by}" width="{bw}" height="{bh}" rx="18" fill="url(#kt)"/>
 <g clip-path="url(#kc)"><rect x="{bx}" y="{by}" width="{bw}" height="{bh}" fill="url(#gloss)"/><rect x="{bx}" y="{by}" width="{bw}" height="{bh}" fill="url(#sw)"/></g>
 <path d="{ld}" fill="#0b0720" transform="translate(0 1.5)" opacity=".35"/>
 <path d="{ld}" fill="#fff"/>
 <g class="nudge">{arrow(ax, by + bh / 2 + 2, 16, '#fff')}</g>
</g>
<path d="{hint}" fill="#94a3b8"/>"""
    (ASSETS / ("enter-3d-m.svg" if m else "enter-3d.svg")).write_text(svg(W, H, "Enter the interactive 3D portfolio", defs, css, body), encoding="utf-8")


# ── FOOTER ───────────────────────────────────────────────────────
def footer():
    W, H = 900, 160

    def wave(amp, base, wl, ph, width=1800):
        pts = [f"M0 {H}"] + [f"L{x} {base + amp * math.sin(2 * math.pi * x / wl + ph):.1f}" for x in range(0, width + 1, 12)]
        return " ".join(pts) + f" L{width} {H}Z"

    ws = [(10, 62, 450, 0, CYAN, .3, 14, 1), (12, 74, 300, 1.2, VIOLET, .4, 10, -1),
          (9, 88, 225, 2.4, PINK, .5, 7, 1), (7, 102, 450, 3.1, "url(#wb)", 1, 18, -1)]
    css, paths = [STAR_CSS], []
    for i, (a, b, wl, ph, col, op, dur, dr) in enumerate(ws):
        f, t = (0, -900) if dr == 1 else (-900, 0)
        css.append(f".w{i}{{animation:w{i} {dur}s linear infinite}}@keyframes w{i}{{from{{transform:translateX({f}px)}}to{{transform:translateX({t}px)}}}}")
        paths.append(f'<path class="w{i}" d="{wave(a, b, wl, ph)}" fill="{col}" fill-opacity="{op}"/>')
    txt = DISPLAY7.d("THANKS FOR STOPPING BY", 15, W / 2, 140, ls=3, anchor="middle")
    defs = f"""<linearGradient id="wb" x1="0" x2="1"><stop offset="0" stop-color="#0e7490"/><stop offset=".5" stop-color="#5b21b6"/><stop offset="1" stop-color="#9d174d"/></linearGradient>
<clipPath id="c"><rect width="{W}" height="{H}" rx="22"/></clipPath>"""
    body = f'<g clip-path="url(#c)">{"".join(paths)}</g><path d="{txt}" fill="#fff"/>'
    (ASSETS / "footer.svg").write_text(svg(W, H, "Thanks for stopping by", defs, "".join(css), body), encoding="utf-8")


def placeholder(file, w, h, msg):
    d = BODY.d(msg, 14, w / 2, h / 2 + 5, ls=.5, anchor="middle")
    (ASSETS / file).write_text(svg(w, h, msg, BG_DEFS, ".p{animation:p 1.4s ease-in-out infinite}@keyframes p{50%{opacity:.4}}",
                                   f'<rect width="{w}" height="{h}" rx="22" fill="url(#bg)"/><path d="{d}" fill="#94a3b8" class="p"/>'),
                               encoding="utf-8")


if __name__ == "__main__":
    ASSETS.mkdir(exist_ok=True)
    for f in ASSETS.glob("*.svg"):
        f.unlink()
    for m in (False, True):
        sfx = "-m" if m else ""
        (ASSETS / f"hero{sfx}.svg").write_text(hero(m), encoding="utf-8")
        for t, f in (("TECH STACK", "title-stack"), ("PROJECTS", "title-projects"), ("3D ACTIVITY", "title-activity")):
            title(t, f"{f}{sfx}.svg", m)
        skills(m)
        featured(m)
        projects(m)
        button(m)
    footer()
    pc = ROOT / "profile-3d-contrib" / "profile-3d-neon.svg"
    if not pc.exists():
        pc.parent.mkdir(exist_ok=True)
        placeholder("../profile-3d-contrib/profile-3d-neon.svg", 900, 300, "building your 3D contribution skyline on the first Actions run…")
    for f in sorted(ASSETS.glob("*.svg")):
        print(f"{f.name:22s} {f.stat().st_size / 1024:6.1f} KB")
