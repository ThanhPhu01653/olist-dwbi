"""Sinh các mảng màu xéo (PNG, khử răng cưa) dùng trong slide master. Chạy: python make_shapes.py"""
from PIL import Image, ImageDraw
import os
PPI, SS = 200, 4
INK, VIO, LAV = (126, 102, 184), (168, 147, 217), (244, 240, 251)
os.makedirs("assets", exist_ok=True)
def poly(name, w, h, layers):
    W, H = int(w * PPI * SS), int(h * PPI * SS)
    im = Image.new("RGBA", (W, H), (0, 0, 0, 0)); d = ImageDraw.Draw(im)
    for col, pts in layers:
        d.polygon([(x * PPI * SS, y * PPI * SS) for x, y in pts], fill=col + (255,))
    im.resize((W // SS, H // SS), Image.LANCZOS).save(f"assets/{name}.png")
poly("bia_panel", 6.033, 7.5, [(INK, [(1.6, 0), (6.033, 0), (6.033, 7.5), (0, 7.5)]), (VIO, [(6.033, 3.9), (6.033, 7.5), (2.3, 7.5)])])
poly("phan_panel", 6.1, 7.5, [(INK, [(0, 0), (6.1, 0), (4.6, 7.5), (0, 7.5)]), (VIO, [(0, 4.6), (3.2, 7.5), (0, 7.5)])])
poly("camon_tri", 4.533, 4.1, [(VIO, [(4.533, 0), (4.533, 4.1), (0, 4.1)])])
poly("deco_tr", 2.333, 0.9, [(LAV, [(0.5, 0), (2.333, 0), (2.333, 0.9), (0, 0.9)])])
print("ok")

def pill(name, w, h, col):
    W, H = int(w * PPI * SS), int(h * PPI * SS)
    im = Image.new("RGBA", (W, H), (0, 0, 0, 0)); ImageDraw.Draw(im).rounded_rectangle([0, 0, W - 1, H - 1], radius=H // 2, fill=col + (255,))
    im.resize((W // SS, H // SS), Image.LANCZOS).save(f"assets/{name}.png")
pill("pill_vio", 2.1, 0.42, (185, 166, 227)); pill("pill_amber", 2.1, 0.42, (242, 196, 109)); pill("pill_num", 0.9, 0.3, (185, 166, 227)); pill("pill_grey", 1.1, 0.3, (95, 100, 112))
W, H = int(2.3 * PPI * SS), int(3.0 * PPI * SS)
im = Image.new("RGBA", (W, H), (0, 0, 0, 0)); ImageDraw.Draw(im).rounded_rectangle([0, 0, W - 1, H - 1], radius=int(0.15 * PPI * SS), fill=(255, 255, 255, 255))
im.resize((W // SS, H // SS), Image.LANCZOS).save("assets/card_white.png")
