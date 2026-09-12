#!/usr/bin/env python3
"""Compose an Omarchy theme preview in the style of the stock themes:
a bar across the top and four windows tiled over the wallpaper."""
import re, sys, math, random
from PIL import Image, ImageDraw, ImageFont, ImageFilter

W, H = 1800, 1012
FONT = "/usr/share/fonts/TTF/JetBrainsMonoNerdFont-Regular.ttf"
FONTB = "/usr/share/fonts/TTF/JetBrainsMonoNerdFont-Bold.ttf"

def load_colors(path):
    return dict(re.findall(r'^(\w+)\s*=\s*"(#[0-9a-fA-F]{6})"', open(path).read(), re.M))

def rgb(h, a=255):
    h = h.lstrip('#')
    return (int(h[0:2],16), int(h[2:4],16), int(h[4:6],16), a)

def mix(c1, c2, t):
    a, b = rgb(c1), rgb(c2)
    return tuple(int(a[i]+(b[i]-a[i])*t) for i in range(3))+(255,)

class Pane:
    """One tiled window: titlebar-ish top strip plus a text body."""
    def __init__(self, img, draw, box, C, radius, title=None, tabs=None):
        self.d = draw; self.C = C
        self.x0, self.y0, self.x1, self.y1 = box
        self.r = radius
        # window body
        draw.rounded_rectangle(box, radius=radius, fill=rgb(C['background']))
        # active border
        draw.rounded_rectangle(box, radius=radius, outline=rgb(C['accent']), width=2)
        self.cy = self.y0 + 10
        if tabs:
            self._tabs(tabs)

    def _tabs(self, tabs):
        C, d = self.C, self.d
        f = ImageFont.truetype(FONT, 13)
        d.rectangle([self.x0+2, self.y0+2, self.x1-2, self.y0+26], fill=rgb(C['lighter_background']))
        x = self.x0 + 14
        for i, t in enumerate(tabs):
            col = C['accent'] if i == 0 else C['dark_foreground']
            d.text((x, self.y0+8), t, font=f, fill=rgb(col))
            if i == 0:
                d.line([x, self.y0+24, x+f.getlength(t), self.y0+24], fill=rgb(C['accent']), width=2)
            x += f.getlength(t) + 26
        self.cy = self.y0 + 36

    def line(self, segs, size=13, indent=12, lh=18):
        """segs: list of (text, colour-key or hex)"""
        f = ImageFont.truetype(FONT, size)
        x = self.x0 + indent
        for text, col in segs:
            c = self.C.get(col, col)
            self.d.text((x, self.cy), text, font=f, fill=rgb(c))
            x += f.getlength(text)
        self.cy += lh

    def blank(self, n=1, lh=18):
        self.cy += lh*n

def bar(img, d, C):
    h = 30
    d.rectangle([0, 0, W, h], fill=rgb(C['dark_background']))
    f = ImageFont.truetype(FONT, 14)
    fb = ImageFont.truetype(FONTB, 14)
    x = 14
    d.text((x, 7), "", font=f, fill=rgb(C["accent"])); x += 30
    for i, name in enumerate(["1", "2", "3", "4", "5"]):
        active = (i == 1)
        col = C['accent'] if active else C['dark_foreground']
        d.text((x, 7), name, font=fb if active else f, fill=rgb(col))
        if active:
            d.line([x-3, 25, x+12, 25], fill=rgb(C['accent']), width=2)
        x += 22
    clock = "Saturday 15:47"
    d.text((W/2 - f.getlength(clock)/2, 7), clock, font=f, fill=rgb(C['light_foreground']))
    tray = "      "
    d.text((W - 24 - f.getlength(tray), 7), tray, font=f, fill=rgb(C['light_foreground']))

def editor(img, d, C, r):
    p = Pane(img, d, (16, 42, 900, 660), C, r, tabs=[" theme.lua", " colors.toml", " README.md"])
    fg, dim, acc = 'foreground', 'dark_foreground', 'accent'
    rows = [
        [("  1  ", dim), ("-- ", 'muted'), ("NZ theme: palette sampled from the photographs", 'muted')],
        [("  2  ", dim)],
        [("  3  ", dim), ("local ", 'magenta'), ("palette ", fg), ("= ", fg), ("{", 'yellow')],
        [("  4  ", dim), ("  background ", 'blue'), ("= ", fg), ('"'+C['background']+'"', 'green'), (",", fg)],
        [("  5  ", dim), ("  foreground ", 'blue'), ("= ", fg), ('"'+C['foreground']+'"', 'green'), (",", fg)],
        [("  6  ", dim), ("  accent     ", 'blue'), ("= ", fg), ('"'+C['accent']+'"', 'green'), (",", fg)],
        [("  7  ", dim), ("  cyan       ", 'blue'), ("= ", fg), ('"'+C['cyan']+'"', 'green'), (",", fg)],
        [("  8  ", dim), ("}", 'yellow')],
        [("  9  ", dim)],
        [(" 10  ", dim), ("function ", 'magenta'), ("M.contrast", 'blue'), ("(", fg), ("fg", 'orange'), (", ", fg), ("bg", 'orange'), (")", fg)],
        [(" 11  ", dim), ("  local ", 'magenta'), ("l1, l2 ", fg), ("= ", fg), ("lum", 'blue'), ("(fg), ", fg), ("lum", 'blue'), ("(bg)", fg)],
        [(" 12  ", dim), ("  if ", 'magenta'), ("l1 < l2 ", fg), ("then ", 'magenta'), ("l1, l2 = l2, l1 ", fg), ("end", 'magenta')],
        [(" 13  ", dim), ("  return ", 'magenta'), ("(l1 + ", fg), ("0.05", 'orange'), (") / (l2 + ", fg), ("0.05", 'orange'), (")", fg)],
        [(" 14  ", dim), ("end", 'magenta')],
        [(" 15  ", dim)],
        [(" 16  ", dim), ("-- every colour clears 4.5:1 against the background", 'muted')],
        [(" 17  ", dim), ("assert", 'blue'), ("(M.", fg), ("contrast", 'blue'), ("(palette.cyan, palette.background) ", fg), ("> ", 'magenta'), ("4.5", 'orange'), (")", fg)],
        [(" 18  ", dim)],
        [(" 19  ", dim), ("-- one key reaches the window border and every shell surface", 'muted')],
        [(" 20  ", dim), ("M.border ", 'blue'), ("= ", fg), ('"accent cyan 45deg"', 'green')],
        [(" 21  ", dim)],
        [(" 22  ", dim), ("function ", 'magenta'), ("M.apply", 'blue'), ("(", fg), ("name", 'orange'), (")", fg)],
        [(" 23  ", dim), ("  for ", 'magenta'), ("key, value ", fg), ("in ", 'magenta'), ("pairs", 'blue'), ("(palette) ", fg), ("do", 'magenta')],
        [(" 24  ", dim), ("    hl.", fg), ("set", 'blue'), ("(name, key, value)", fg)],
        [(" 25  ", dim), ("  end", 'magenta')],
        [(" 26  ", dim), ("  hl.", fg), ("config", 'blue'), ("({ decoration = { rounding = ", fg), ("0", 'orange'), (" } })", fg)],
        [(" 27  ", dim), ("end", 'magenta')],
        [(" 28  ", dim)],
        [(" 29  ", dim), ("return ", 'magenta'), ("M", fg)],
        [(" 30  ", dim), ("~", 'dark_foreground')],
        [(" 31  ", dim), ("~", 'dark_foreground')],
    ]
    for row in rows:
        p.line(row, size=13.5, lh=19)
    # status line
    d.rectangle([18, 634, 898, 658], fill=rgb(C['lighter_background']))
    f = ImageFont.truetype(FONTB, 12)
    d.text((28, 640), " NORMAL", font=f, fill=rgb(C["accent"]))
    f2 = ImageFont.truetype(FONT, 12)
    d.text((116, 640), " main    theme.lua", font=f2, fill=rgb(C["light_foreground"]))
    d.text((700, 640), "utf-8   lua   17:42   99%", font=f2, fill=rgb(C["dark_foreground"]))

def terminal(img, d, C, r):
    p = Pane(img, d, (16, 672, 900, 996), C, r)
    fg, dim = 'foreground', 'dark_foreground'
    p.cy = 686
    rows = [
        [("~/Dev/omarchy-theme ", 'cyan'), ("", 'magenta'), (" main ", 'magenta'), ("$ ", fg), ("omarchy theme list", 'green')],
        [("  Catppuccin   Everforest   Gruvbox   Kanagawa", 'light_foreground')],
        [("  Nord   Rose Pine   Tokyo Night", 'light_foreground')],
        [("", fg)],
        [("~/Dev/omarchy-theme ", 'cyan'), ("", 'magenta'), (" main ", 'magenta'), ("$ ", fg), ("git status --short", 'green')],
        [(" M ", 'yellow'), ("colors.toml", fg)],
        [(" M ", 'yellow'), ("hyprland.lua", fg)],
        [("?? ", 'red'), ("backgrounds/", fg)],
        [("", fg)],
        [("~/Dev/omarchy-theme ", 'cyan'), ("", 'magenta'), (" main ", 'magenta'), ("$ ", fg), ("./check-contrast", 'green')],
        [("  accent  ", 'light_foreground'), ("PASS", 'green'), ("   9.6:1", dim)],
        [("  cyan    ", 'light_foreground'), ("PASS", 'green'), ("   7.6:1", dim)],
        [("  orange  ", 'light_foreground'), ("PASS", 'green'), ("   6.0:1", dim)],
        [("  muted   ", 'light_foreground'), ("INFO", 'blue'), ("   2.7:1  structural", dim)],
        [("", fg)],
        [("~/Dev/omarchy-theme ", 'cyan'), ("", 'magenta'), (" main ", 'magenta'), ("$ ", fg), ("█", 'bright_foreground')],
    ]
    for row in rows:
        p.line(row, size=13.5, lh=19)

def monitor(img, d, C, r):
    p = Pane(img, d, (916, 42, 1784, 560), C, r)
    f = ImageFont.truetype(FONT, 12.5)
    fb = ImageFont.truetype(FONTB, 12.5)
    d.text((932, 54), "cpu", font=fb, fill=rgb(C['accent']))
    d.text((1700, 54), "3.9 GHz", font=f, fill=rgb(C['dark_foreground']))
    random.seed(7)
    # cpu core bars
    y = 76
    for core in range(8):
        pct = random.randint(4, 86)
        d.text((932, y), f"C{core}", font=f, fill=rgb(C['light_foreground']))
        bx0, bx1 = 968, 1330
        d.rectangle([bx0, y+3, bx1, y+11], fill=rgb(C['lighter_background']))
        w = int((bx1-bx0)*pct/100)
        col = C['green'] if pct < 50 else (C['yellow'] if pct < 75 else C['red'])
        d.rectangle([bx0, y+3, bx0+w, y+11], fill=rgb(col))
        d.text((1344, y), f"{pct:3d}%", font=f, fill=rgb(C['light_foreground']))
        y += 20
    # memory block
    y += 10
    d.text((932, y), "mem", font=fb, fill=rgb(C["accent"]))
    y += 24
    for label, pct, col in [("used", 51, 'cyan'), ("cache", 37, 'blue'), ("swap", 4, 'magenta')]:
        d.text((932, y), f"{label:6}", font=f, fill=rgb(C['light_foreground']))
        bx0, bx1 = 992, 1330
        d.rectangle([bx0, y+3, bx1, y+11], fill=rgb(C['lighter_background']))
        d.rectangle([bx0, y+3, bx0+int((bx1-bx0)*pct/100), y+11], fill=rgb(C[col]))
        d.text((1344, y), f"{pct:3d}%", font=f, fill=rgb(C['light_foreground']))
        y += 20
    # network graph
    d.text((1400, 54), "net", font=fb, fill=rgb(C['accent']))
    gx0, gy0, gx1, gy1 = 1400, 76, 1770, 250
    d.rectangle([gx0, gy0, gx1, gy1], outline=rgb(C['lighter_background']), width=1)
    pts = []
    v = 0.5
    for i in range(0, gx1-gx0, 4):
        v = max(0.05, min(0.95, v + random.uniform(-0.16, 0.16)))
        pts.append((gx0+i, gy1 - v*(gy1-gy0)))
    d.line(pts, fill=rgb(C['cyan']), width=2)
    for (px, py) in pts:
        d.line([px, py, px, gy1], fill=mix(C['cyan'], C['background'], 0.82), width=1)
    d.line(pts, fill=rgb(C['cyan']), width=2)
    d.text((1400, 258), "down 28.9 MiB/s", font=f, fill=rgb(C['green']))
    d.text((1400, 276), "up    4.2 MiB/s", font=f, fill=rgb(C['orange']))
    # disks, filling the space under the net graph
    dy = 306
    d.text((1400, dy), "disks", font=fb, fill=rgb(C["accent"]))
    dy += 24
    for label, pct, used in [("/", 64, "596 GiB"), ("/home", 71, "812 GiB"), ("/boot", 22, "212 MiB")]:
        d.text((1400, dy), f"{label:<7}", font=f, fill=rgb(C["light_foreground"]))
        bx0, bx1 = 1462, 1700
        d.rectangle([bx0, dy+3, bx1, dy+11], fill=rgb(C["lighter_background"]))
        col = C["cyan"] if pct < 70 else C["orange"]
        d.rectangle([bx0, dy+3, bx0+int((bx1-bx0)*pct/100), dy+11], fill=rgb(col))
        d.text((1712, dy), f"{pct:3d}%", font=f, fill=rgb(C["light_foreground"]))
        d.text((1462, dy+16), used, font=f, fill=rgb(C["dark_foreground"]))
        dy += 40
    d.text((1400, dy+6), "uptime 3d 23:15", font=f, fill=rgb(C["dark_foreground"]))
    d.text((1400, dy+24), "load   1.17 1.00 0.83", font=f, fill=rgb(C["dark_foreground"]))

    # process table
    ty = 330
    d.text((932, ty), "proc", font=fb, fill=rgb(C['accent']))
    ty += 22
    hdr = f"{'pid':>7}  {'program':<18}{'user':<10}{'mem':>8}{'cpu%':>7}"
    d.text((932, ty), hdr, font=f, fill=rgb(C['dark_foreground'])); ty += 18
    procs = [("809869","hyprland","andy","231M",3.1),("690183","cliamp","andy","109M",1.4),
             ("730555","brave","andy","511M",8.2),("534063","foot","andy","239M",0.6),
             ("7717","nvim","andy","102M",0.4),("810231","btop","andy","18M",1.9),
             ("341341","quickshell","andy","178M",2.2),("802955","xfreerdp","andy","96M",5.7),
             ("129331","pipewire","andy","22M",0.3)]
    for pid, prog, user, mem, cpu in procs:
        col = C['foreground'] if cpu < 5 else C['yellow']
        d.text((932, ty), f"{pid:>7}  ", font=f, fill=rgb(C['dark_foreground']))
        d.text((1000, ty), f"{prog:<18}", font=f, fill=rgb(col))
        d.text((1152, ty), f"{user:<10}", font=f, fill=rgb(C['light_foreground']))
        d.text((1240, ty), f"{mem:>8}", font=f, fill=rgb(C['blue']))
        d.text((1320, ty), f"{cpu:>6.1f}", font=f, fill=rgb(C['cyan']))
        ty += 18

def files(img, d, C, r):
    box = (916, 572, 1784, 996)
    d.rounded_rectangle(box, radius=r, fill=rgb(C['dark_background']))
    d.rounded_rectangle(box, radius=r, outline=rgb(C['selection']), width=2)
    f = ImageFont.truetype(FONT, 13)
    fb = ImageFont.truetype(FONTB, 13.5)
    # header
    d.rectangle([918, 574, 1782, 606], fill=rgb(C['lighter_background']))
    d.text((936, 583), "  Files", font=fb, fill=rgb(C["foreground"]))
    d.text((1120, 583), " Home    Dev    omarchy-theme", font=f, fill=rgb(C["light_foreground"]))
    d.text((1752, 583), "", font=f, fill=rgb(C["red"]))
    # sidebar
    d.rectangle([918, 606, 1090, 994], fill=rgb(C['background']))
    sy = 622
    for icon, name, sel in [("", "Home", False), ("", "Recent", False), ("", "Starred", False),
                            ("", "Dev", True), ("", "Pictures", False), ("", "Downloads", False),
                            ("", "Trash", False)]:
        if sel:
            d.rounded_rectangle([926, sy-5, 1082, sy+19], radius=4, fill=rgb(C['selection']))
        d.text((938, sy), f"{icon}  {name}", font=f,
               fill=rgb(C['accent'] if sel else C['light_foreground']))
        sy += 34
    # file grid
    gx, gy = 1112, 640
    items = [("", "backgrounds", 'accent'), ("", "colors.toml", 'cyan'), ("", "hyprland.lua", 'blue'),
             ("", "README.md", 'light_foreground'), ("", "preview.png", 'magenta'), ("", "CREDITS.md", 'light_foreground'),
             ("", "unlock.png", 'magenta'), ("", "LICENSE", 'dark_foreground')]
    fi = ImageFont.truetype(FONT, 34)
    for i, (icon, name, col) in enumerate(items):
        cx = gx + (i % 4)*168
        cy = gy + (i // 4)*150
        d.text((cx+42, cy), icon, font=fi, fill=rgb(C[col]))
        tw = f.getlength(name)
        d.text((cx+72-tw/2, cy+56), name, font=f, fill=rgb(C['light_foreground']))

def compose(colors_path, wallpaper, out, radius):
    C = load_colors(colors_path)
    wp = Image.open(wallpaper).convert("RGB")
    # cover-fit
    s = max(W/wp.width, H/wp.height)
    wp = wp.resize((math.ceil(wp.width*s), math.ceil(wp.height*s)), Image.LANCZOS)
    left = (wp.width - W)//2; top = (wp.height - H)//2
    img = wp.crop((left, top, left+W, top+H)).convert("RGBA")
    d = ImageDraw.Draw(img, "RGBA")
    bar(img, d, C)
    editor(img, d, C, radius)
    terminal(img, d, C, radius)
    monitor(img, d, C, radius)
    files(img, d, C, radius)
    img.convert("RGB").save(out)
    print("wrote", out, img.size)

if __name__ == "__main__":
    compose(sys.argv[1], sys.argv[2], sys.argv[3], int(sys.argv[4]))
