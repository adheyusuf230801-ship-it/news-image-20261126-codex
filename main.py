"""Deterministic, standard-library-only newspaper illustration for make.fun."""
import math
import os
import struct
import zlib

W = H = 1024
PAPER = (245, 242, 232)
INK = (24, 42, 57)
RED = (164, 49, 43)
BLUE = (102, 128, 143)
PALE = (220, 227, 226)
MID = (155, 175, 182)
FONT_ROWS = {
'A':'01110 10001 10001 11111 10001 10001 10001',
'B':'11110 10001 10001 11110 10001 10001 11110',
'C':'01111 10000 10000 10000 10000 10000 01111',
'D':'11110 10001 10001 10001 10001 10001 11110',
'E':'11111 10000 10000 11110 10000 10000 11111',
'F':'11111 10000 10000 11110 10000 10000 10000',
'G':'01111 10000 10000 10111 10001 10001 01111',
'H':'10001 10001 10001 11111 10001 10001 10001',
'I':'11111 00100 00100 00100 00100 00100 11111',
'J':'00111 00010 00010 00010 10010 10010 01100',
'K':'10001 10010 10100 11000 10100 10010 10001',
'L':'10000 10000 10000 10000 10000 10000 11111',
'M':'10001 11011 10101 10101 10001 10001 10001',
'N':'10001 11001 11001 10101 10011 10011 10001',
'O':'01110 10001 10001 10001 10001 10001 01110',
'P':'11110 10001 10001 11110 10000 10000 10000',
'Q':'01110 10001 10001 10001 10101 10010 01101',
'R':'11110 10001 10001 11110 10100 10010 10001',
'S':'01111 10000 10000 01110 00001 00001 11110',
'T':'11111 00100 00100 00100 00100 00100 00100',
'U':'10001 10001 10001 10001 10001 10001 01110',
'V':'10001 10001 10001 10001 10001 01010 00100',
'W':'10001 10001 10001 10101 10101 10101 01010',
'X':'10001 10001 01010 00100 01010 10001 10001',
'Y':'10001 10001 01010 00100 00100 00100 00100',
'Z':'11111 00001 00010 00100 01000 10000 11111',
'0':'01110 10001 10011 10101 11001 10001 01110',
'1':'00100 01100 00100 00100 00100 00100 01110',
'2':'01110 10001 00001 00010 00100 01000 11111',
'3':'11110 00001 00001 01110 00001 00001 11110',
'4':'00010 00110 01010 10010 11111 00010 00010',
'5':'11111 10000 10000 11110 00001 00001 11110',
'6':'01110 10000 10000 11110 10001 10001 01110',
'7':'11111 00001 00010 00100 01000 01000 01000',
'8':'01110 10001 10001 01110 10001 10001 01110',
'9':'01110 10001 10001 01111 00001 00001 01110',
'.':'00000 00000 00000 00000 00000 00110 00110',
',':'00000 00000 00000 00000 00110 00100 01000',
"'":'00100 00100 01000 00000 00000 00000 00000',
'-':'00000 00000 00000 11111 00000 00000 00000',
':':'00000 00110 00110 00000 00110 00110 00000',
';':'00000 00110 00110 00000 00110 00100 01000',
'!':'00100 00100 00100 00100 00100 00000 00100',
'?':'01110 10001 00001 00010 00100 00000 00100',
'(':'00010 00100 01000 01000 01000 00100 00010',
')':'01000 00100 00010 00010 00010 00100 01000',
'/':'00001 00010 00010 00100 01000 01000 10000',
'%':'11001 11010 00010 00100 01000 01011 10011',
'&':'01100 10010 10100 01000 10101 10010 01101',
' ':'00000 00000 00000 00000 00000 00000 00000',
}
FONT = {c: tuple(row.split()) for c, row in FONT_ROWS.items()}


class Canvas:
    def __init__(self):
        self.pixels = bytearray(bytes(PAPER) * (W * H))

    def rect(self, x, y, width, height, color):
        x0, y0 = max(0, int(x)), max(0, int(y))
        x1, y1 = min(W, int(x + width)), min(H, int(y + height))
        if x1 <= x0 or y1 <= y0:
            return
        row = bytes(color) * (x1 - x0)
        for yy in range(y0, y1):
            start = (yy * W + x0) * 3
            self.pixels[start:start + len(row)] = row

    def ellipse(self, cx, cy, rx, ry, color):
        for y in range(int(cy - ry), int(cy + ry) + 1):
            v = 1 - ((y - cy) / ry) ** 2
            if v >= 0:
                dx = int(rx * math.sqrt(v))
                self.rect(cx - dx, y, 2 * dx + 1, 1, color)

    def line(self, x0, y0, x1, y1, color, thickness=1):
        steps = max(abs(x1 - x0), abs(y1 - y0), 1)
        for i in range(steps + 1):
            self.rect(round(x0 + (x1 - x0) * i / steps) - thickness // 2,
                      round(y0 + (y1 - y0) * i / steps) - thickness // 2,
                      thickness, thickness, color)

    def polygon(self, points, color):
        for y in range(min(p[1] for p in points), max(p[1] for p in points) + 1):
            crossings = []
            for a, b in zip(points, points[1:] + points[:1]):
                if (a[1] <= y < b[1]) or (b[1] <= y < a[1]):
                    crossings.append(a[0] + (y-a[1]) * (b[0]-a[0]) / (b[1]-a[1]))
            crossings.sort()
            for i in range(0, len(crossings), 2):
                left, right = math.ceil(crossings[i]), math.floor(crossings[i+1])
                self.rect(left, y, right-left+1, 1, color)

    def text(self, s, x, y, scale, color=INK, bounds=(0, 0, W, H)):
        # All copy is uppercase: every glyph, including punctuation, fits seven rows.
        width = text_width(s, scale)
        bx, by, bw, bh = bounds
        if not (bx <= x and by <= y and x + width <= bx + bw and y + 7*scale <= by + bh):
            raise ValueError('Text exceeds panel: ' + s)
        for c in s:
            for yy, row in enumerate(FONT[c]):
                for xx, bit in enumerate(row):
                    if bit == '1':
                        self.rect(x + xx*scale, y + yy*scale, scale, scale, color)
            x += 6*scale

    def centered(self, s, y, scale, color=INK):
        self.text(s, (W-text_width(s, scale))//2, y, scale, color)

    def paragraph(self, s, x, y, width, scale, leading, bounds, color=INK):
        words = s.split()
        lines = []
        current = ''
        for word in words:
            if text_width(word, scale) > width:
                raise ValueError('Word wider than column: ' + word)
            candidate = (current + ' ' + word).strip()
            if text_width(candidate, scale) <= width:
                current = candidate
            else:
                lines.append(current)
                current = word
        if current:
            lines.append(current)
        for line in lines:
            self.text(line, x, y, scale, color, bounds)
            y += leading
        return y

    def save(self, path):
        def chunk(kind, data):
            return struct.pack('>I', len(data)) + kind + data + struct.pack('>I', zlib.crc32(kind+data) & 0xffffffff)
        scanlines = b''.join(b'\0' + self.pixels[y*W*3:(y+1)*W*3] for y in range(H))
        png = (b'\x89PNG\r\n\x1a\n' + chunk(b'IHDR', struct.pack('>IIBBBBB', W,H,8,2,0,0,0))
               + chunk(b'IDAT', zlib.compress(scanlines, 9)) + chunk(b'IEND', b''))
        if len(png) > 1024*1024:
            raise ValueError('PNG exceeds 1 MiB')
        with open(path, 'wb') as output:
            output.write(png)


def text_width(s, scale):
    return max(0, len(s)*6-1)*scale


def cloud(c, x, y, size, color):
    c.ellipse(x, y, size, size//3, color)
    c.ellipse(x-size//3, y-size//5, size//2, size//3, color)
    c.ellipse(x+size//4, y-size//4, size//2, size//2, color)


def storm_scene(c):
    c.rect(32, 180, 960, 174, PALE)
    # Layered Manhattan silhouettes and the Empire State spire.
    for x, top, width in ((44,278,42),(90,255,48),(145,273,34),(185,236,42),
                          (234,257,36),(281,225,40),(331,259,42),(384,269,38),
                          (432,248,48),(495,270,43),(548,245,35),(599,261,41),
                          (652,232,44),(710,250,45),(765,264,42),(819,237,43),
                          (875,268,38),(930,255,50)):
        c.rect(x, top, width, 326-top, (124, 148, 160))
        for wy in range(top+9, 316, 12):
            for wx in range(x+7, x+width-4, 13):
                c.rect(wx, wy, 3, 4, PALE)
    c.rect(474, 251, 36, 75, BLUE)
    c.rect(481, 235, 22, 20, BLUE)
    c.rect(487, 223, 10, 15, BLUE)
    c.line(492, 205, 492, 231, BLUE, 2)
    for x, y, s in ((110,211,76),(245,214,86),(408,207,80),(590,212,94),(780,210,83),(927,215,64)):
        cloud(c,x,y+25,round(s*0.7),BLUE)
    for x in range(60, 975, 28):
        y = 239 + ((x*7) % 39)
        c.line(x,y,x-9,y+21,(72, 101, 120),3)
    c.rect(32,326,960,28,INK)
    c.line(45,345,978,345,MID,1)
    # Round parade envelopes held low by street crews in the storm.
    c.ellipse(245, 281, 33, 33, INK)
    c.ellipse(245, 280, 31, 31, BLUE)
    c.ellipse(236, 270, 12, 15, MID)
    c.polygon([(241,310),(249,310),(247,317),(243,317)], BLUE)
    # A simple teddy character balloon: round ears, head, belly and paws.
    for x, y, rx, ry in ((731,246,10,10),(765,246,10,10),
                          (748,261,25,23),(748,289,25,27),
                          (721,283,11,13),(775,283,11,13),
                          (733,311,11,8),(763,311,11,8)):
        c.ellipse(x,y,rx,ry,INK)
        c.ellipse(x,y-1,rx-2,ry-2,BLUE)
    c.ellipse(748,291,14,17,MID)
    c.ellipse(748,267,12,8,MID)
    c.ellipse(740,257,2,3,INK)
    c.ellipse(756,257,2,3,INK)
    c.ellipse(748,265,3,2,INK)
    for x, top in ((224,303),(266,303),(729,311),(768,311)):
        c.line(x,top,x,339,INK,1)
        c.line(x,326,x,339,PAPER,1)
        c.ellipse(x,334,2,2,PAPER)
        c.line(x,336,x,342,PAPER,2)
        c.line(x,338,x-3,336,PAPER,1)
        c.line(x,342,x-2,345,PAPER,1)
        c.line(x,342,x+2,345,PAPER,1)
    # Collapsed envelopes lie flat on the pavement, with slack folded seams.
    for x, rx in ((365,24),(559,28),(858,21)):
        c.ellipse(x,339,rx,5,BLUE)
        c.ellipse(x-5,336,rx//2,4,MID)
        c.line(x-rx+5,340,x-3,337,PALE,1)
        c.line(x-3,337,x+rx-4,341,PALE,1)
        c.line(x+rx,340,x+rx+9,342,MID,1)
    c.text('NEW YORK',53,334,1,PAPER)


def icon(c, kind, x, y):
    c.ellipse(x,y,27,27,PALE)
    if kind == 'flood':
        cloud(c,x,y-7,18,BLUE)
        for dx in (-12,0,12):
            c.line(x+dx,y+1,x+dx-4,y+9,BLUE,2)
        for yy in (y+15,y+22):
            for dx in (-20,-6,8):
                c.line(x+dx,yy,x+dx+7,yy-3,BLUE,2)
                c.line(x+dx+7,yy-3,x+dx+14,yy,BLUE,2)
    elif kind == 'jet':
        c.polygon([(x,y-24),(x+5,y-5),(x+24,y+9),(x+5,y+5),(x+4,y+17),
                   (x+11,y+23),(x,y+19),(x-11,y+23),(x-4,y+17),(x-5,y+5),(x-24,y+9),(x-5,y-5)],INK)
    elif kind == 'nuclear':
        c.ellipse(x,y,4,4,INK)
        for angle in (0,120,240):
            pts = [(x,y)]
            for a in range(angle-29,angle+30,3):
                r = math.radians(a)
                pts.append((round(x+22*math.cos(r)), round(y+22*math.sin(r))))
            c.polygon(pts,BLUE)
        c.ellipse(x,y,8,8,PALE)
        c.ellipse(x,y,4,4,INK)
    elif kind == 'satellite':
        c.rect(x-7,y-8,14,16,INK)
        for dx in (-24,11):
            c.rect(x+dx,y-13,13,26,BLUE)
            c.line(x+dx+6,y-12,x+dx+6,y+12,PALE)
            c.line(x+dx,y,x+dx+12,y,PALE)
        c.line(x-11,y,x+11,y,INK,2)
        c.line(x,y-8,x+10,y-21,INK,2)
        c.ellipse(x+11,y-22,3,3,INK)
    elif kind == 'gavel':
        c.line(x-8,y+6,x+14,y-15,INK,6)
        c.line(x-14,y-16,x+2,y,BLUE,12)
        c.rect(x-20,y+18,40,5,INK)
        c.rect(x-13,y+13,26,5,BLUE)
    elif kind == 'flag':
        c.line(x-21,y-22,x-21,y+24,INK,3)
        c.rect(x-18,y-20,39,27,BLUE)
        c.polygon([(x-18,y-20),(x-1,y-7),(x-18,y+7)],INK)
        c.line(x-15,y-16,x-3,y-7,PAPER,3)
        c.line(x-3,y-7,x-15,y+3,PAPER,3)
        c.line(x-2,y-7,x+20,y-7,PAPER,3)
    elif kind == 'health':
        c.rect(x-19,y-22,38,44,BLUE)
        c.rect(x-4,y-15,8,23,PAPER)
        c.rect(x-12,y-7,24,8,PAPER)
        c.rect(x-5,y+13,10,9,INK)


STORIES = (
    ('flood','STORM FLOODS EAST COAST','BOMB CYCLONE BRINGS COASTAL FLOODING; NEW YORK AND NEW JERSEY DECLARE EMERGENCIES.'),
    ('jet','UKRAINE HITS RUSSIAN AIR BASE','FIVE RUSSIAN MILITARY JETS DAMAGED IN A STRIKE ON SAVASLEYKA AIRBASE.'),
    ('nuclear','KIM ORDERS WIDER NUCLEAR DEPLOYMENT',"NORTH KOREA'S KIM JONG UN CALLS FOR TACTICAL NUCLEAR WEAPONS ACROSS MORE DOMAINS."),
    ('satellite','SPACEX CLEARED FOR 1M SATELLITES','US APPROVES A PLAN FOR UP TO ONE MILLION DATA-CENTRE SATELLITES IN ORBIT.'),
    ('gavel','NORWAY COURT VOIDS OIL LICENCES','SUPREME COURT RULES CLIMATE-DISPUTED OIL LICENCES INVALID.'),
    ('flag','RAMAPHOSA WINS FARMGATE REPRIEVE',"SOUTH AFRICA'S PRESIDENT ESCAPES AN IMPEACHMENT INVESTIGATION - FOR NOW."),
    ('health',"KENYA'S LAST EBOLA PATIENT GOES HOME",'DRC DEATH TOLL PASSES 5,300 AS KENYA DISCHARGES ITS FINAL PATIENT.'),
)


def render():
    c = Canvas()
    c.text('THE DAILY WORLD BRIEF',32,20,2)
    c.text('8 STORIES / ONE DAY',766,20,2)
    c.centered('WORLD IN ONE DAY',53,8)
    c.centered('THURSDAY 26 NOVEMBER 2026',120,4)
    c.rect(32,160,960,5,RED)
    storm_scene(c)
    c.text("MACY'S 100TH PARADE POSTPONED",32,373,4,RED,(32,360,960,105))
    c.paragraph('FIRST POSTPONEMENT IN 100 YEARS. THE THANKSGIVING STORM GROUNDS THE BALLOONS; THE PARADE MOVES TO SATURDAY 28 NOVEMBER.',
                32,418,950,2,19,(32,360,960,105))
    c.rect(32,466,960,2,INK)
    for i, (kind, title, body) in enumerate(STORIES[:6]):
        x = 32 + (i % 2)*486
        y = 480 + (i//2)*142
        bounds = (x,y,474,134)
        icon(c,kind,x+29,y+36)
        yy = c.paragraph(title,x+70,y+8,400,3,24,bounds)
        c.paragraph(body,x+70,yy+8,400,2,17,bounds)
        c.rect(x,y+133,474,1,MID)
    c.rect(506,480,1,418,MID)
    kind, title, body = STORIES[6]
    bounds = (32,914,960,80)
    icon(c,kind,61,951)
    c.text(title,102,922,3,bounds=bounds)
    c.paragraph(body,102,956,880,2,18,bounds)
    c.rect(32,998,960,2,INK)
    c.text('26 NOV 2026',32,1008,1)
    c.text('WORLD IN ONE DAY',903,1008,1)
    return c


def main():
    output_dir = os.environ.get('MAKEFUN_OUTPUT_DIR', '/output')
    os.makedirs(output_dir, exist_ok=True)
    render().save(os.path.join(output_dir, 'entry.png'))


if __name__ == '__main__':
    main()
