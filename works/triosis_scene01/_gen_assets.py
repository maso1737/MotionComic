# -*- coding: utf-8 -*-
# D4 作画: TrioSisBrothers / Scene 01 レイヤーPNG＋音声WAV生成
# 設計憲章「3Dではない、でも生きている」/ 紙=watercolor / トーン=halftone
# 出力: img/*.png (1080x1920 透過・transformはJSON側) , snd/*.wav
import os, math, random, struct, wave
from PIL import Image, ImageDraw, ImageFilter

random.seed(20260517)
W, H = 1080, 1920
HERE = os.path.dirname(os.path.abspath(__file__))
IMG = os.path.join(HERE, "img"); SND = os.path.join(HERE, "snd")
os.makedirs(IMG, exist_ok=True); os.makedirs(SND, exist_ok=True)

def new(): return Image.new("RGBA", (W, H), (0, 0, 0, 0))

def watercolor(img, cx, cy, rad, color, blobs=26, amax=70):
    """紙にじみ: 半透明ブロブを重ねて水彩風の不定形を作る"""
    lay = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(lay)
    for _ in range(blobs):
        a = random.uniform(0, 2*math.pi); r = rad*random.uniform(0.25, 1.0)
        x = cx + math.cos(a)*r; y = cy + math.sin(a)*r
        rr = rad*random.uniform(0.18, 0.5)
        al = int(amax*random.uniform(0.35, 1.0))
        d.ellipse([x-rr, y-rr, x+rr, y+rr], fill=color+(al,))
    lay = lay.filter(ImageFilter.GaussianBlur(rad*0.10+4))
    img.alpha_composite(lay)

def halftone(img, box, color, step=15, rmax=4.2, angle=18):
    """トーン: マスク内に網点。紙の濃淡を少ない文法で。"""
    x0, y0, x1, y1 = box
    lay = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(lay)
    ca, sa = math.cos(math.radians(angle)), math.sin(math.radians(angle))
    j = -int((x1-x0+y1-y0))
    while j < (x1-x0+y1-y0):
        i = -int((x1-x0+y1-y0))
        while i < (x1-x0+y1-y0):
            px = x0 + ca*i - sa*j; py = y0 + sa*i + ca*j
            if x0 <= px <= x1 and y0 <= py <= y1:
                t = (py-y0)/max(1, y1-y0)
                rr = rmax*(0.35+0.65*t)
                d.ellipse([px-rr, py-rr, px+rr, py+rr], fill=color+(70,))
            i += step
        j += step
    img.alpha_composite(lay)

def paper_edge(img):
    """全レイヤー共通: 輪郭をわずかに揺らし“描いた紙”の質感"""
    return img.filter(ImageFilter.GaussianBlur(0.6))

def save(img, name):
    paper_edge(img).save(os.path.join(IMG, name)); print("img/"+name)

# ---------- L_sky : 不動の空（晴れ→翳り→凪を内包する素地） ----------
def gen_sky():
    img = new(); d = ImageDraw.Draw(img)
    for y in range(H):
        t = y/H
        r = int(244 - 40*t); g = int(239 - 18*t); b = int(230 + 8*t)
        d.line([(0, y), (W, y)], fill=(r, g, b, 255))
    watercolor(img, 760, 360, 230, (255, 246, 214), blobs=30, amax=46)  # 陽だまり
    watercolor(img, 250, 1500, 300, (210, 222, 232), blobs=24, amax=34)
    save(img, "L_sky.png")

# ---------- L_far : 遠景の雪丘＋淡い太陽 ----------
def gen_far():
    img = new(); d = ImageDraw.Draw(img)
    d.ellipse([700, 230, 880, 410], fill=(255, 240, 205, 120))
    for hx, hy, hr, c in [(220, 1250, 520, (228, 232, 238)),
                          (760, 1330, 600, (236, 238, 242)),
                          (520, 1480, 760, (244, 245, 248))]:
        d.ellipse([hx-hr, hy, hx+hr, hy+hr*1.4], fill=c+(180,))
    watercolor(img, 520, 1400, 460, (222, 228, 236), blobs=20, amax=30)
    save(img, "L_far.png")

# ---------- L_mid : 雪原の地面（兄弟の土地・トーン） ----------
def gen_mid():
    img = new(); d = ImageDraw.Draw(img)
    d.polygon([(0, 1320), (W, 1230), (W, H), (0, H)], fill=(248, 248, 250, 235))
    watercolor(img, 540, 1620, 520, (228, 232, 240), blobs=28, amax=40)
    halftone(img, (60, 1500, 1020, 1860), (150, 165, 185), step=17, rmax=4.0)
    d.line([(0, 1320), (W, 1230)], fill=(170, 178, 190, 150), width=4)
    save(img, "L_mid.png")

# ---------- 兄弟（frame_inside）----------
def gen_kakashi():  # ☦️ カカシ兄: 十字・細長・布が遅れる
    img = new(); d = ImageDraw.Draw(img)
    cx = 380
    d.line([(cx, 760), (cx, 1560)], fill=(120, 92, 64, 255), width=22)      # 支柱
    d.line([(cx-150, 980), (cx+150, 980)], fill=(120, 92, 64, 255), width=20)  # 横木
    watercolor(img, cx, 880, 120, (190, 150, 110), blobs=18, amax=70)        # 頭(布袋)
    d.ellipse([cx-78, 800, cx+78, 956], fill=(214, 196, 168, 255))
    d.ellipse([cx-26, 850, cx-10, 868], fill=(60, 50, 40, 255))
    d.ellipse([cx+12, 850, cx+28, 868], fill=(60, 50, 40, 255))
    d.polygon([(cx-150, 770), (cx+150, 770), (cx+100, 815), (cx-100, 815)],
              fill=(150, 110, 70, 255))                                       # 帽子
    d.polygon([(cx-150, 1000), (cx+150, 1000), (cx+120, 1430), (cx-120, 1330)],
              fill=(170, 120, 96, 235))                                       # 布(遅れる)
    halftone(img, (cx-150, 1000, cx+150, 1430), (110, 80, 60), step=14, rmax=3.4)
    save(img, "L_kakashi.png")

def gen_yuki():  # ⛄️ 雪だるま弟: 丸い・重い・水滴
    img = new(); d = ImageDraw.Draw(img)
    cx, by = 620, 1500
    watercolor(img, cx, by-90, 250, (235, 240, 248), blobs=24, amax=80)
    d.ellipse([cx-150, by-300, cx+150, by], fill=(250, 251, 254, 255))        # 胴
    d.ellipse([cx-100, by-470, cx+100, by-270], fill=(252, 253, 255, 255))    # 頭
    for ex in (-34, 30):
        d.ellipse([cx+ex-12, by-410, cx+ex+12, by-386], fill=(40, 44, 52, 255))
    d.arc([cx-44, by-380, cx+44, by-320], 20, 160, fill=(60, 50, 44, 255), width=7)
    d.polygon([(cx, by-356), (cx+60, by-344), (cx, by-330)], fill=(232, 150, 70, 255))
    for ddx, ddy in [(-120, -120), (118, -90), (-70, -30), (96, -10)]:        # 水滴
        d.ellipse([cx+ddx-9, by+ddy, cx+ddx+9, by+ddy+18], fill=(150, 195, 220, 200))
    halftone(img, (cx-150, by-300, cx+150, by), (170, 185, 205), step=16, rmax=3.6)
    save(img, "L_yuki.png")

def gen_teru():  # 🕊️ てるてる坊主: 自由浮遊・影が先
    img = new(); d = ImageDraw.Draw(img)
    cx, cy = 820, 760
    d.ellipse([cx-150, cy-26, cx-30, cy+30], fill=(60, 70, 90, 40))           # 先行する影
    watercolor(img, cx, cy, 120, (255, 255, 255), blobs=16, amax=120)
    d.ellipse([cx-86, cy-86, cx+86, cy+86], fill=(255, 255, 255, 255))        # 頭
    d.polygon([(cx-78, cy+60), (cx+78, cy+60), (cx+130, cy+360),
               (cx-130, cy+360)], fill=(252, 252, 254, 240))                  # 布
    for ex in (-30, 26):
        d.ellipse([cx+ex-9, cy-12, cx+ex+9, cy+10], fill=(70, 78, 96, 255))
    d.arc([cx-26, cy+18, cx+26, cy+54], 200, 340, fill=(120, 90, 110, 255), width=5)
    d.line([(cx, cy-86), (cx, cy-150)], fill=(180, 180, 190, 180), width=3)   # 切れた紐
    save(img, "L_teru.png")

# ---------- 姉妹（traveler / 手前・越境）----------
def gen_ane():  # ☂️ 雨傘姉: 面で守る・やりすぎ（大きな傘）
    img = new(); d = ImageDraw.Draw(img)
    cx, cy = 560, 540
    d.pieslice([cx-360, cy-300, cx+360, cy+340], 180, 360,
               fill=(46, 64, 104, 255))                                       # 大きな傘
    for k in range(-3, 4):
        d.line([(cx, cy), (cx+k*110, cy+58)], fill=(30, 42, 70, 255), width=5)
    d.line([(cx, cy), (cx, cy+560)], fill=(60, 50, 44, 255), width=12)        # 柄
    d.ellipse([cx-26, cy+560, cx+26, cy+612], fill=(200, 90, 80, 255))        # 体
    halftone(img, (cx-360, cy-260, cx+360, cy+330), (24, 34, 60), step=15, rmax=4.6)
    watercolor(img, cx, cy+40, 300, (40, 56, 92), blobs=20, amax=34)
    save(img, "L_ane.png")

def gen_imouto():  # ⛱️ 日傘妹: 快適・光調整（明るい日傘）
    img = new(); d = ImageDraw.Draw(img)
    cx, cy = 760, 700
    d.pieslice([cx-240, cy-210, cx+240, cy+230], 180, 360,
               fill=(255, 224, 188, 255))
    d.arc([cx-240, cy-210, cx+240, cy+230], 180, 360, fill=(240, 180, 140, 255), width=6)
    d.line([(cx, cy), (cx, cy+420)], fill=(150, 110, 80, 255), width=9)
    d.ellipse([cx-22, cy+420, cx+22, cy+466], fill=(245, 180, 120, 255))
    watercolor(img, cx, cy+10, 210, (255, 234, 200), blobs=18, amax=46)
    halftone(img, (cx-220, cy-180, cx+220, cy+220), (230, 170, 120), step=18, rmax=3.2)
    save(img, "L_imouto.png")

def gen_sue():  # 🌂 折りたたみ末っ子: 最適化・隙間（小さく畳まれた）
    img = new(); d = ImageDraw.Draw(img)
    cx, cy = 540, 1180
    d.polygon([(cx-26, cy-150), (cx+26, cy-150), (cx+14, cy+150),
               (cx-14, cy+150)], fill=(70, 120, 110, 255))                    # 畳んだ傘
    d.line([(cx, cy+150), (cx, cy+250)], fill=(90, 80, 70, 255), width=7)
    d.ellipse([cx-18, cy+250, cx+18, cy+288], fill=(120, 170, 150, 255))
    d.line([(cx-26, cy-150), (cx+26, cy-150)], fill=(50, 90, 84, 255), width=6)
    watercolor(img, cx, cy, 90, (80, 130, 116), blobs=12, amax=40)
    save(img, "L_sue.png")

# ---------- FX ----------
def gen_fore():  # 手前の葉・雪片（速いパララックス）
    img = new(); d = ImageDraw.Draw(img)
    for _ in range(46):
        x = random.uniform(0, W); y = random.uniform(0, H)
        r = random.uniform(6, 20)
        if random.random() < 0.5:
            d.ellipse([x-r, y-r, x+r, y+r], fill=(255, 255, 255, random.randint(60, 150)))
        else:
            d.polygon([(x, y-r), (x+r, y), (x, y+r), (x-r, y)],
                      fill=(150, 175, 120, random.randint(70, 140)))
    img = img.filter(ImageFilter.GaussianBlur(1.4))
    save(img, "L_fore.png")

def gen_kira():  # ⑤一瞬の微粒子（常時うっすら→bloomで立つ）
    img = new(); d = ImageDraw.Draw(img)
    for _ in range(120):
        x = random.uniform(120, W-120); y = random.uniform(500, 1500)
        r = random.uniform(2, 7)
        d.ellipse([x-r, y-r, x+r, y+r], fill=(255, 252, 230, random.randint(40, 110)))
    for sx, sy in [(540, 980), (700, 880), (430, 1120), (820, 1040)]:
        for ang in range(0, 360, 45):
            ex = sx+math.cos(math.radians(ang))*26
            ey = sy+math.sin(math.radians(ang))*26
            d.line([(sx, sy), (ex, ey)], fill=(255, 250, 220, 150), width=3)
    img = img.filter(ImageFilter.GaussianBlur(0.8))
    save(img, "L_kira.png")

for fn in (gen_sky, gen_far, gen_mid, gen_kakashi, gen_yuki, gen_teru,
           gen_ane, gen_imouto, gen_sue, gen_fore, gen_kira):
    fn()

# ================= 音声 WAV（BGM=うっすら / SE=しっかり） =================
SR = 22050
def wav(name, samples):
    path = os.path.join(SND, name)
    with wave.open(path, "w") as w:
        w.setnchannels(1); w.setsampwidth(2); w.setframerate(SR)
        w.writeframes(b"".join(struct.pack("<h",
            int(max(-1, min(1, s))*32767)) for s in samples))
    print("snd/"+name)

def bgm():  # 柔らかいパッド（ループ・うっすら）8秒
    dur = 8.0; n = int(SR*dur); out = []
    chord = [196.0, 233.08, 293.66]  # G B D 系・低く穏やか
    for i in range(n):
        t = i/SR; s = 0.0
        for f in chord:
            s += math.sin(2*math.pi*f*t) * 0.16
        s += math.sin(2*math.pi*98*t) * 0.10
        env = 0.5 + 0.5*math.sin(2*math.pi*t/dur)  # ループ端を滑らかに
        out.append(s*env*0.5)
    wav("bgm_main.wav", out)

def se_noise(dur, f0, f1, shape, amp=0.85):
    n = int(SR*dur); out = []
    for i in range(n):
        t = i/SR; p = i/n
        nz = (random.uniform(-1, 1))
        f = f0 + (f1-f0)*p
        tone = math.sin(2*math.pi*f*t)
        if shape == "basa":   env = math.exp(-6*p)*(0.7+0.3*nz)
        elif shape == "hyu":  env = math.sin(math.pi*p)*(0.5+0.5*abs(nz))
        elif shape == "crash":env = math.exp(-9*p)*abs(nz)
        else:                 env = math.exp(-5*p)
        out.append((0.6*nz+0.4*tone)*env*amp)
    return out

def se_chime(dur=0.9):  # ⑤キラッ: 澄んだ減衰ベル
    n = int(SR*dur); out = []
    for i in range(n):
        t = i/SR; p = i/n; env = math.exp(-4.5*p)
        s = (math.sin(2*math.pi*1320*t)*0.6 +
             math.sin(2*math.pi*1980*t)*0.3 +
             math.sin(2*math.pi*2640*t)*0.15)
        out.append(s*env*0.7)
    return out

wav("bgm_main.wav", []) if False else bgm()
wav("se_basa.wav",  se_noise(0.55, 800, 300, "basa"))
wav("se_hyu.wav",   se_noise(1.10, 240, 90,  "hyu"))
wav("se_kira.wav",  se_chime(0.95))
wav("se_crash.wav", se_noise(0.70, 600, 120, "crash"))
print("DONE")
