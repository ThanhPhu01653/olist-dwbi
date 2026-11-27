"""Sau build.js: đặt tên placeholder trong layout, xoá slide trống của template. Chạy: python fix_names.py"""
from pptx import Presentation
NAMES = {"BIA": ["mon_hoc", "tieu_de", "phu_de", "nhom", "giang_vien"], "CHUYEN_PHAN": ["so_phan", "tieu_de", "noi_dung"],
         "NOI_DUNG": ["muc", "tieu_de", "noi_dung", "phan"], "NOI_DUNG_KL": ["muc", "tieu_de", "noi_dung", "phan", "ket_luan"],
         "HINH": ["muc", "tieu_de", "chu_thich", "phan"], "HINH_KL": ["muc", "tieu_de", "chu_thich", "phan", "ket_luan"],
         "HAI_COT_KL": ["muc", "tieu_de", "cot_trai", "phan", "ket_luan"], "PHU_LUC": ["muc", "tieu_de", "noi_dung", "phan"],
         "CAM_ON": ["tieu_de", "noi_dung"]}
for f, drop in [("out/Olist_Nhom19_template.pptx", True), ("out/Olist_Nhom19_giao_dien_mau.pptx", False)]:
    p = Presentation(f)
    for l in p.slide_layouts:
        if l.name in NAMES:
            phs = sorted([ph for ph in l.placeholders if int(ph.placeholder_format.type) != 13], key=lambda ph: ph.placeholder_format.idx)
            assert len(phs) == len(NAMES[l.name]), (l.name, len(phs))
            for ph, n in zip(phs, NAMES[l.name]):
                ph._element.nvSpPr.cNvPr.set("name", n)
    if drop:
        lst = p.slides._sldIdLst
        for s in list(lst):
            p.part.drop_rel(s.rId); lst.remove(s)
    p.save(f)
print("ok")
