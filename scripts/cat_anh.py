"""Cắt ảnh chụp màn hình cho slide (giữ file gốc, ghi file mới).

    python scripts/cat_anh.py figures/human_takes/x.png figures/5-1_x.png --trim
        # tự bỏ viền một màu (nền trắng/đen thừa quanh nội dung)
    python scripts/cat_anh.py in.png out.png --box 0 22 965 346
        # cắt theo toạ độ pixel: trái trên phải dưới (xem bằng Paint: góc dưới trái hiện toạ độ chuột)
    python scripts/cat_anh.py in.png out.png --box ... --scale 2
        # phóng ảnh nhỏ lên 2 lần (chữ nét hơn khi chèn to)

Quy tắc: ảnh trên slide chỉ giữ phần chứng minh điều tiêu đề nói; tỉ lệ ngang (rộng/cao) nên từ 1,4 đến 2,4.
"""
import argparse
from PIL import Image, ImageChops

ap = argparse.ArgumentParser()
ap.add_argument("src"); ap.add_argument("dst")
ap.add_argument("--box", nargs=4, type=int, metavar=("TRAI", "TREN", "PHAI", "DUOI"))
ap.add_argument("--trim", action="store_true")
ap.add_argument("--scale", type=float, default=1.0)
a = ap.parse_args()
im = Image.open(a.src).convert("RGB")
if a.box:
    im = im.crop(tuple(a.box))
if a.trim:
    bg = Image.new("RGB", im.size, im.getpixel((0, 0)))
    bbox = ImageChops.difference(im, bg).getbbox()
    if bbox:
        pad = 8
        im = im.crop((max(bbox[0] - pad, 0), max(bbox[1] - pad, 0), min(bbox[2] + pad, im.width), min(bbox[3] + pad, im.height)))
if a.scale != 1.0:
    im = im.resize((round(im.width * a.scale), round(im.height * a.scale)), Image.LANCZOS)
im.save(a.dst)
r = im.width / im.height
print(f"{a.dst}: {im.width}x{im.height}, tỉ lệ {r:.2f}" + ("  (NÊN cắt thêm: ảnh quá dẹt)" if r > 2.6 else "  (NÊN cắt ngang: ảnh dọc khó chiếu)" if r < 1.2 else ""))
