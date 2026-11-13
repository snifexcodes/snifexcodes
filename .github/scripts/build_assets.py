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
def hero():
    W, H = 900, 400
    size = 132
    cx, base = W / 2, 196
    nd = DISPLAY.d(NAME, size, cx, base, ls=10, anchor="middle")
    nw = DISPLAY.width(NAME, size, 10)

    # isometric floor grid
    ox, oy = W / 2, 238
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
    cubes = [(110, 120, 34, CYAN, 0), (140, 238, 22, PINK, -1.6), (790, 110, 30, PINK, -.8),
             (772, 236, 24, AMBER, -2.4), (70, 300, 16, VIOLET, -3.1), (840, 300, 18, CYAN, -1.1)]
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
<linearGradient id="vfade" x1="0" y1="0" x2="0" y2="1"><stop offset=".56" stop-color="#fff" stop-opacity="0"/><stop offset=".86" stop-color="#fff"/></linearGradient>
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
 <ellipse cx="{cx}" cy="170" rx="330" ry="150" fill="url(#glowV)"/>
 {stars(70, W, H, 3, 230)}
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
def title(text, file):
    W, H = 900, 76
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
<rect x="40" y="{base - 10}" width="{l1 - 54:.1f}" height="2" rx="1" fill="url(#lf)"/>
<rect x="{l2 + 14:.1f}" y="{base - 10}" width="{W - 54 - l2:.1f}" height="2" rx="1" fill="url(#rf)"/>
<circle cx="{l1 - 14}" cy="{base - 9}" r="3" fill="{CYAN}" class="dot" style="--dx:-{l1 - 60:.0f}px"/>
<circle cx="{l2 + 14}" cy="{base - 9}" r="3" fill="{PINK}" class="dot" style="--dx:{W - 60 - l2:.0f}px;animation-delay:-1.5s"/>
<g class="spin">{cube_l}</g><g class="spin" style="animation-delay:-3s">{cube_r}</g>
{ext}<use href="#t" fill="url(#tf)"/>
"""
    (ASSETS / file).write_text(svg(W, H, text.title(), defs, css, body), encoding="utf-8")


# ── SKILL BLOCKS ─────────────────────────────────────────────────
def skills():
    W, H = 900, 210
    n = len(SKILLS)
    s = 40
    gap = (W - 80) / n
    oy = 112
    parts = []
    # platform slab
    pw = W - 60
    parts.append(f'<rect x="30" y="{oy + 34}" width="{pw}" height="14" rx="7" fill="url(#neon)" opacity=".18"/>'
                 f'<rect x="30" y="{oy + 30}" width="{pw}" height="6" rx="3" fill="url(#neon)" opacity=".55"/>')
    for i, (label, col) in enumerate(SKILLS):
        x = 40 + gap * (i + .5)
        dl = -i * .28
        parts.append(
            f'<ellipse cx="{x:.1f}" cy="{oy + 33}" rx="{s * .9:.0f}" ry="5" fill="#000" opacity=".5" class="sh" style="animation-delay:{dl:.2f}s"/>'
            f'<g class="bob" style="animation-delay:{dl:.2f}s">{box(-s / 2, -s / 2, 0, s, s, s, col, x, oy - s * .1)}'
            f'{poly([iso(-s / 2 + 6, -s / 2 + 6, s, x, oy - s * .1), iso(-s / 2 + 18, -s / 2 + 6, s, x, oy - s * .1), iso(-s / 2 + 6, -s / 2 + 18, s, x, oy - s * .1)], "#fff", 'opacity=".35"')}</g>'
            f'<path d="{BODY7.d(label, 13, x, oy + 68, ls=.5, anchor="middle")}" fill="#cbd5e1"/>')
    defs = BG_DEFS + '<clipPath id="card"><rect width="900" height="210" rx="22"/></clipPath>'
    css = STAR_CSS + """
.bob{animation:bob 2.8s ease-in-out infinite}@keyframes bob{50%{transform:translateY(-16px)}}
.sh{transform-box:fill-box;transform-origin:center;animation:sh 2.8s ease-in-out infinite}@keyframes sh{50%{transform:scale(.6);opacity:.15}}"""
    body = f"""<g clip-path="url(#card)"><rect width="{W}" height="{H}" fill="url(#bg)"/>
<rect width="{W}" height="{H}" fill="url(#glowC)"/><rect width="{W}" height="{H}" fill="url(#glowP)"/>{stars(26, W, 120, 9)}
{''.join(parts)}</g>
<rect x=".75" y=".75" width="{W - 1.5}" height="{H - 1.5}" rx="22" fill="none" stroke="url(#neon)" stroke-opacity=".4" stroke-width="1.5"/>"""
    (ASSETS / "skills.svg").write_text(
        svg(W, H, "Tech stack: " + ", ".join(l for l, _ in SKILLS), defs, css, body), encoding="utf-8")


# ── PROJECT ICONS (iso, drawn around ox,oy) ──────────────────────
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


def project(stem, kicker, ttl, desc, tags, kind, accent, idx):
    W, H = 440, 250
    x0, y0, cw, ch = 10, 8, 414, 222
    lines = BODY.wrap(desc, 13.5, 236)[:4]
    text = "".join(f'<path d="{BODY.d(l, 13.5, 34, 104 + i * 20)}" fill="#a8b3c7"/>' for i, l in enumerate(lines))
    chips, cx = [], 34
    for t in tags:
        w = BODY7.width(t, 11, .4) + 18
        chips.append(f'<rect x="{cx}" y="190" width="{w:.1f}" height="22" rx="11" fill="{accent}" fill-opacity=".12" stroke="{accent}" stroke-opacity=".5"/>'
                     f'<path d="{BODY7.d(t, 11, cx + w / 2, 205, ls=.4, anchor="middle")}" fill="{shade(accent, .35)}"/>')
        cx += w + 7
    defs = f"""
<linearGradient id="cb" x1="0" y1="0" x2="1" y2="1"><stop offset="0" stop-color="#141a35"/><stop offset="1" stop-color="#1a1036"/></linearGradient>
<linearGradient id="ed" x1="0" x2="1"><stop offset="0" stop-color="{CYAN}"/><stop offset=".5" stop-color="{VIOLET}"/><stop offset="1" stop-color="{PINK}"/></linearGradient>
<radialGradient id="ig" cx=".5" cy=".5" r=".5"><stop offset="0" stop-color="{accent}" stop-opacity=".35"/><stop offset="1" stop-color="{accent}" stop-opacity="0"/></radialGradient>
<filter id="gl" x="-10%" y="-10%" width="120%" height="120%"><feGaussianBlur stdDeviation="3"/></filter>"""
    per = 2 * (cw + ch)
    css = f"""
.card{{animation:fl 6s ease-in-out infinite;animation-delay:-{idx * 1.5}s}}@keyframes fl{{50%{{transform:translateY(-5px)}}}}
.run{{stroke-dasharray:140 {per - 140};animation:run 6s linear infinite;animation-delay:-{idx * 1.2}s}}@keyframes run{{to{{stroke-dashoffset:-{per}}}}}
.lift{{animation:lf 3.2s ease-in-out infinite}}@keyframes lf{{50%{{transform:translateY(-7px)}}}}
.lift2{{animation:lf 3.2s ease-in-out infinite;animation-delay:-1.6s}}
.typing{{animation:ty 1.2s ease-in-out infinite}}@keyframes ty{{0%,100%{{opacity:.25}}40%{{opacity:1}}}}
.wave{{animation:ty 1.2s ease-in-out infinite}}
"""
    body = f"""
<g class="card">
 <rect x="{x0 + 6}" y="{y0 + 12}" width="{cw}" height="{ch}" rx="20" fill="#05060f"/>
 <rect x="{x0 + 3}" y="{y0 + 6}" width="{cw}" height="{ch}" rx="20" fill="{shade(accent, -.75)}"/>
 <rect x="{x0}" y="{y0}" width="{cw}" height="{ch}" rx="20" fill="url(#cb)" stroke="#2a2f55"/>
 <rect x="{x0}" y="{y0}" width="{cw}" height="{ch}" rx="20" fill="none" stroke="url(#ed)" stroke-width="3" class="run" filter="url(#gl)"/>
 <rect x="{x0}" y="{y0}" width="{cw}" height="{ch}" rx="20" fill="none" stroke="url(#ed)" stroke-width="1.5" class="run"/>
 <circle cx="352" cy="104" r="78" fill="url(#ig)"/>
 {icon(kind, 352, 122, accent)}
 <path d="{BODY7.d(kicker, 10.5, 34, 44, ls=1.6)}" fill="{accent}"/>
 <path d="{DISPLAY7.d(ttl, 19, 34, 74)}" fill="#f8fafc"/>
 {text}
 {''.join(chips)}
 <path d="{BODY7.d('VIEW', 11, 386, 205, ls=1.4, anchor='end')}" fill="#e2e8f0"/>
 {arrow(392, 201, 11, '#e2e8f0')}
</g>"""
    (ASSETS / f"{stem}.svg").write_text(svg(W, H, f"{ttl}: {desc}", defs, css, body), encoding="utf-8")


# ── ENTER-3D BUTTON ──────────────────────────────────────────────
def button():
    W, H = 900, 140
    bw, bh, depth = 520, 66, 10
    bx, by = (W - bw) / 2, 26
    label = "ENTER THE 3D PORTFOLIO"
    ld = DISPLAY7.d(label, 17, W / 2 - 12, by + 41, ls=2.2, anchor="middle")
    lw = DISPLAY7.width(label, 17, 2.2)
    hint = BODY.d("drag to orbit  ·  click planets to open projects  ·  works on mobile", 12.5, W / 2, by + bh + depth + 30, ls=.6, anchor="middle")
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
 <g class="nudge">{arrow(ax, by + 35, 16, '#fff')}</g>
</g>
<path d="{hint}" fill="#94a3b8"/>"""
    (ASSETS / "enter-3d.svg").write_text(svg(W, H, "Enter the interactive 3D portfolio", defs, css, body), encoding="utf-8")


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
    (ASSETS / "hero.svg").write_text(hero(), encoding="utf-8")
    for t, f in (("TECH STACK", "title-stack.svg"), ("PROJECTS", "title-projects.svg"), ("3D ACTIVITY", "title-activity.svg")):
        title(t, f)
    skills()
    for i, p in enumerate(PROJECTS):
        project(*p, idx=i)
    button()
    footer()
    pc = ROOT / "profile-3d-contrib" / "profile-3d-neon.svg"
    if not pc.exists():
        pc.parent.mkdir(exist_ok=True)
        placeholder("../profile-3d-contrib/profile-3d-neon.svg", 900, 300, "building your 3D contribution skyline on the first Actions run…")
    for f in sorted(ASSETS.glob("*.svg")):
        print(f"{f.name:22s} {f.stat().st_size / 1024:6.1f} KB")
