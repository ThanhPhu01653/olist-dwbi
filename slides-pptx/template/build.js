// Giao diện PowerPoint cho bộ slide Nhóm 19 (Olist DW & BI) – tím pastel, nhấn vàng pastel.
// Bố cục tham khảo cách trình bày thoáng của nhóm 5 (dấu nhóm góc trái, tiêu đề lớn, số trang dạng viên thuốc,
// trang chuyển phần có mảng màu xéo), màu và chi tiết khác hẳn.
// Chạy: python make_shapes.py ; npm i pptxgenjs ; node build.js ; python fix_names.py
const pptxgen = require("pptxgenjs");
const path = require("path");
const fs = require("fs");
const { applyTheme } = require("./apply_theme.js");
const A = (f) => path.join(__dirname, "assets", f);
const FIG = (f) => path.join(process.env.FIGDIR || path.join(__dirname, "..", "..", "figures", "slide"), f);

const THEME = {
  name: "Nhom19 Lavender",
  headFontFace: "Arial",
  bodyFontFace: "Arial",
  colors: {
    dk1: "1F2328", lt1: "FFFFFF", dk2: "3A2C5E", lt2: "F4F0FB",
    accent1: "7E66B8", accent2: "F2C46D", accent3: "F28E2B", accent4: "1F6FB2",
    accent5: "2E9E6B", accent6: "5F6470", hlink: "6F55A8", folHlink: "3A2C5E",
  },
};
const C = {
  ink: "7E66B8",      // tím pastel: nền chuyển phần, bìa, tiêu đề bảng
  vio: "6F55A8",      // tím chữ: nhãn mục, số, mũi tên (đủ tương phản trên nền trắng)
  box: "6B57A6",      // nền hộp điểm nhấn (chữ trắng)
  deep: "3A2C5E",     // chữ đậm trên nền pastel
  lav: "F4F0FB",      // tím rất nhạt: nền thẻ, thanh kết luận
  lav2: "E2D9F3",     // tím nhạt: viền
  amber: "F2C46D",    // vàng pastel: nhấn thứ hai
  fact: "F28E2B",     // màu fact (cam, giống theme Power BI)
  dim: "1F6FB2",      // màu dimension (xanh, giống theme Power BI)
  text: "1F2328", grey: "5F6470", line: "DDD6EA", white: "FFFFFF", red: "C0392B",
};
const W = 13.333, H = 7.5, X0 = 0.6, CW = W - 2 * X0;

// ---------- chi tiết dùng chung ----------
function brand(o, dark) {
  // dấu nhóm: 3 cột tăng dần + chữ
  const col = dark ? [C.amber, C.amber, C.white] : [C.amber, C.vio, C.ink];
  [0.12, 0.2, 0.28].forEach((h, i) => o.push({ rect: { x: X0 + i * 0.09, y: 0.5 - h, w: 0.065, h, fill: { color: col[i] } } }));
  o.push({ text: { text: "Nhóm 19 · Olist DW & BI", options: { x: X0 + 0.36, y: 0.22, w: 4, h: 0.3, fontSize: 11, bold: true, color: dark ? "D9CCF2" : C.grey, margin: 0, valign: "middle" } } });
}
function deco(o) {
  // mảng xéo nhạt góc trên phải
  o.push({ image: { path: A("deco_tr.png"), x: 11.0, y: 0, w: 2.333, h: 0.9 } });
  o.push({ image: { path: A("hust-shield.png"), x: 12.45, y: 0.16, w: 0.38, h: 0.57 } });
}
function footer(o, dark) {
  o.push({ image: { path: A("pill_num.png"), x: 11.85, y: 7.02, w: 0.9, h: 0.3 } });
}
const pageNum = (dark) => ({ x: 11.85, y: 7.02, w: 0.9, h: 0.3, fontSize: 11, bold: true, color: C.deep, align: "center", valign: "middle" });
const phPhan = () => ({ placeholder: { options: { name: "phan", type: "body", x: X0, y: 7.02, w: 8, h: 0.3, fontSize: 11, color: C.grey, margin: 0, valign: "middle" }, text: "Phần 1 · Khảo sát" } });
const phMuc = () => ({ placeholder: { options: { name: "muc", type: "body", x: 5.6, y: 0.22, w: 5.4, h: 0.3, fontSize: 12, bold: true, color: C.vio, margin: 0, align: "right", valign: "middle" }, text: "1.1 · Mục nhỏ" } });
const phTitle = () => ({ placeholder: { options: { name: "tieu_de", type: "title", x: X0, y: 0.72, w: 11.6, h: 0.7, fontSize: 28, bold: true, color: C.text, margin: 0, valign: "middle", align: "left" }, text: "Tiêu đề: tên mục + kết luận ngắn" } });
const phBody = (x, y, w, h, name = "noi_dung") => ({ placeholder: { options: { name, type: "body", x, y, w, h, fontSize: 20, color: C.text, margin: 0.05, valign: "top", paraSpaceAfter: 8 }, text: "Nội dung" } });
const phKL = () => ({ placeholder: { options: { name: "ket_luan", type: "body", x: X0 + 0.35, y: 6.2, w: CW - 0.5, h: 0.55, fontSize: 18, bold: true, color: C.deep, align: "left", valign: "middle", margin: 0 }, text: "Thanh kết luận: một câu, có số" } });
const phCap = (y) => ({ placeholder: { options: { name: "chu_thich", type: "body", x: X0, y, w: CW, h: 0.3, fontSize: 11, italic: true, color: C.grey, align: "center", margin: 0 }, text: "Hình x.y. Chú thích hình" } });
function klBox(o) {
  o.push({ rect: { x: X0, y: 6.17, w: CW, h: 0.6, fill: { color: C.lav } } });
  o.push({ rect: { x: X0, y: 6.17, w: 0.1, h: 0.6, fill: { color: C.amber } } });
}
function contentBase(o) { brand(o); deco(o); footer(o); }

function defineLayouts(pres) {
  pres.layout = "LAYOUT_WIDE";
  pres.theme = { headFontFace: THEME.headFontFace, bodyFontFace: THEME.bodyFontFace };

  // 1. Bìa: chữ bên trái trên nền trắng, mảng tím xéo bên phải
  let o = [];
  o.push({ image: { path: A("logo-full-s.png"), x: X0, y: 0.35, w: 2.5, h: 0.75 } });
  o.push({ image: { path: A("bia_panel.png"), x: 7.3, y: 0, w: 6.033, h: H } });
  o.push({ image: { path: A("card_white.png"), x: 9.85, y: 0.9, w: 2.3, h: 3.0 } });
  o.push({ image: { path: A("fami-shield-s.png"), x: 10.25, y: 1.1, w: 1.5, h: 2.25 } });
  pres.defineSlideMaster({ title: "BIA", background: { color: C.white }, objects: o.concat([
    { placeholder: { options: { name: "mon_hoc", type: "body", x: X0, y: 1.75, w: 7, h: 0.35, fontSize: 14, bold: true, color: C.vio, margin: 0 }, text: "Môn học" } },
    { placeholder: { options: { name: "tieu_de", type: "title", x: X0, y: 2.15, w: 7.2, h: 1.2, fontSize: 60, bold: true, color: C.ink, margin: 0, align: "left", valign: "middle" }, text: "OLIST" } },
    { placeholder: { options: { name: "phu_de", type: "body", x: X0, y: 3.4, w: 7, h: 0.9, fontSize: 18, color: C.text, margin: 0, valign: "top" }, text: "Phụ đề" } },
    { image: { path: A("pill_vio.png"), x: X0, y: 4.75, w: 2.1, h: 0.42 } },
    { text: { text: "Thực hiện", options: { x: X0, y: 4.75, w: 2.1, h: 0.42, fontSize: 13, bold: true, color: C.deep, align: "center", margin: 0 } } },
    { image: { path: A("pill_amber.png"), x: X0 + 3.0, y: 4.75, w: 2.1, h: 0.42 } },
    { text: { text: "Giảng viên", options: { x: X0 + 3.0, y: 4.75, w: 2.1, h: 0.42, fontSize: 13, bold: true, color: C.deep, align: "center", margin: 0 } } },
    { placeholder: { options: { name: "nhom", type: "body", x: X0, y: 5.3, w: 2.1, h: 0.5, fontSize: 15, bold: true, color: C.text, align: "center", margin: 0 }, text: "Nhóm 19" } },
    { placeholder: { options: { name: "giang_vien", type: "body", x: X0 + 3.0, y: 5.3, w: 3.4, h: 0.5, fontSize: 15, bold: true, color: C.text, align: "left", margin: [0,0,0,0], margin: 0 }, text: "GVHD" } },
  ]) });

  // 2. Chuyển phần: mảng tím xéo bên trái, tên phần bên phải
  o = [];
  o.push({ image: { path: A("phan_panel.png"), x: 0, y: 0, w: 6.1, h: H } });
  brand(o, true); footer(o);
  pres.defineSlideMaster({ title: "CHUYEN_PHAN", background: { color: C.white }, slideNumber: pageNum(), objects: o.concat([
    { placeholder: { options: { name: "so_phan", type: "body", x: X0, y: 2.9, w: 3.8, h: 0.9, fontSize: 40, bold: true, color: C.white, margin: 0 }, text: "PHẦN 1" } },
    { placeholder: { options: { name: "tieu_de", type: "title", x: 6.6, y: 2.75, w: 6.1, h: 1.0, fontSize: 44, bold: true, color: C.vio, margin: 0, align: "left" }, text: "Tên phần" } },
    { rect: { x: 6.6, y: 3.85, w: 0.9, h: 0.06, fill: { color: C.amber } } },
    { placeholder: { options: { name: "noi_dung", type: "body", x: 6.6, y: 4.1, w: 6.1, h: 1.5, fontSize: 18, color: C.grey, margin: 0, valign: "top" }, text: "Các mục nhỏ" } },
  ]) });

  // 3. Nội dung (không / có kết luận)
  for (const [name, kl] of [["NOI_DUNG", false], ["NOI_DUNG_KL", true]]) {
    o = []; contentBase(o); if (kl) klBox(o);
    const items = [phMuc(), phTitle(), phBody(X0, 1.65, CW, kl ? 4.35 : 5.2), phPhan()];
    if (kl) items.push(phKL());
    pres.defineSlideMaster({ title: name, background: { color: C.white }, slideNumber: pageNum(), objects: o.concat(items) });
  }

  // 4. Hình lớn (vùng hình để trống, code tự đặt ảnh vừa khung)
  for (const [name, kl] of [["HINH", false], ["HINH_KL", true]]) {
    o = []; contentBase(o); if (kl) klBox(o);
    const items = [phMuc(), phTitle(), phCap(kl ? 5.8 : 6.62), phPhan()];
    if (kl) items.push(phKL());
    pres.defineSlideMaster({ title: name, background: { color: C.white }, slideNumber: pageNum(), objects: o.concat(items) });
  }

  // 5. Hai cột (chữ trái, hình/bảng/thẻ phải), có kết luận
  o = []; contentBase(o); klBox(o);
  pres.defineSlideMaster({ title: "HAI_COT_KL", background: { color: C.white }, slideNumber: pageNum(), objects: o.concat([
    phMuc(), phTitle(), phBody(X0, 1.65, 4.7, 4.35, "cot_trai"), phPhan(), phKL(),
  ]) });

  // 6. Phụ lục
  o = []; contentBase(o);
  o.push({ image: { path: A("pill_grey.png"), x: 4.4, y: 0.22, w: 1.1, h: 0.3 } });
  o.push({ text: { text: "PHỤ LỤC", options: { x: 4.4, y: 0.22, w: 1.1, h: 0.3, fontSize: 10, bold: true, color: C.white, align: "center", margin: 0 } } });
  pres.defineSlideMaster({ title: "PHU_LUC", background: { color: C.white }, slideNumber: pageNum(), objects: o.concat([
    phMuc(), phTitle(), phBody(X0, 1.65, CW, 5.2), phPhan(),
  ]) });

  // 7. Cảm ơn
  o = [];
  o.push({ image: { path: A("camon_tri.png"), x: 8.8, y: 3.4, w: 4.533, h: 4.1 } });
  brand(o, true);
  pres.defineSlideMaster({ title: "CAM_ON", background: { color: C.ink }, objects: o.concat([
    { placeholder: { options: { name: "tieu_de", type: "title", x: X0, y: 1.9, w: 9.5, h: 1.8, fontSize: 48, bold: true, color: C.white, align: "left", valign: "bottom", margin: 0 }, text: "Cảm ơn thầy và các bạn" } },
    { rect: { x: X0, y: 3.85, w: 0.9, h: 0.06, fill: { color: C.amber } } },
    { placeholder: { options: { name: "noi_dung", type: "body", x: X0, y: 4.1, w: 10, h: 1.0, fontSize: 22, color: C.white, align: "left", margin: 0 }, text: "Hỏi đáp" } },
  ]) });
}

// ---------- slide mẫu ----------
function fitImage(slide, file, box) {
  if (!fs.existsSync(file)) { slide.addText("[ảnh: " + path.basename(file) + "]", { ...box, align: "center", color: C.grey, isTextBox: true }); return; }
  const { execSync } = require("child_process");
  const [pw, ph] = execSync(`${process.env.PYTHON || "python"} -c "from PIL import Image;im=Image.open(r'${file}');print(*im.size)"`).toString().trim().split(" ").map(Number);
  const maxW = pw / 250, maxH = ph / 250; // không thấp hơn 250 ppi
  let w = Math.min(box.w, maxW), h = w * ph / pw;
  if (h > box.h) { h = Math.min(box.h, maxH); w = h * pw / ph; }
  slide.addImage({ path: file, x: box.x + (box.w - w) / 2, y: box.y + (box.h - h) / 2, w, h });
}
const bullets = (arr, o = {}) => arr.map((t, i) => ({ text: t, options: { bullet: { indent: 18 }, breakLine: i < arr.length - 1, ...o } }));
const box = (s, pres, x, y, w, h, fill, line) => s.addShape(pres.shapes.ROUNDED_RECTANGLE, { x, y, w, h, fill: { color: fill }, line: line ? { color: line, width: 1 } : { type: "none" }, rectRadius: 0.08 });
const T = (s, t, x, y, w, h, o = {}) => s.addText(t, { x, y, w, h, margin: 0, isTextBox: true, color: C.text, ...o });

function samples(pres) {
  const P = ["Mở đầu", "Phần 1 · Khảo sát", "Phần 2 · Phân tích và thiết kế", "Phần 3 · Xây dựng hệ thống", "Phần 4 · Chủ đề mở rộng", "Phần 5 · Tổng kết"];
  // 1 Bìa
  let s = pres.addSlide({ masterName: "BIA" });
  s.addText("Kho dữ liệu và Kinh doanh thông minh · MI4214 · Mã lớp 174394", { placeholder: "mon_hoc" });
  s.addText("OLIST", { placeholder: "tieu_de" });
  s.addText("Xây dựng kho dữ liệu Quản lý đơn hàng: từ hai hệ thống nguồn đến bộ dashboard Power BI", { placeholder: "phu_de" });
  s.addText("Nhóm 19", { placeholder: "nhom" });
  s.addText("ThS. Nguyễn Danh Tú", { placeholder: "giang_vien" });

  // 2 Thành viên (viên số)
  s = pres.addSlide({ masterName: "NOI_DUNG" });
  s.addText("Mở đầu", { placeholder: "muc" }); s.addText("Thành viên nhóm", { placeholder: "tieu_de" }); s.addText("Mở đầu", { placeholder: "phan" });
  const mem = [["Phạm Thị Phương Anh", "20237414"], ["Nguyễn Thị Thanh Hiền", "20237433"], ["Đỗ Thị Hồng Lê", "20237454"], ["Lương Hồng Phúc", "20237474"], ["Trần Thanh Phú", "20237473"]];
  mem.forEach(([n, id], i) => {
    const y = 1.75 + i * 0.95;
    box(s, pres, X0, y, 7.6, 0.75, C.lav);
    s.addShape(pres.shapes.OVAL, { x: X0 + 0.2, y: y + 0.15, w: 0.45, h: 0.45, fill: { color: i === 4 ? C.amber : C.vio } });
    T(s, String(i + 1), X0 + 0.2, y + 0.15, 0.45, 0.45, { fontSize: 16, bold: true, color: i === 4 ? C.deep : C.white, align: "center", valign: "middle" });
    T(s, `${n} – ${id}`, X0 + 0.9, y, 6.5, 0.75, { fontSize: 20, bold: true, valign: "middle" });
  });
  T(s, "Phân công: ghi phần phụ trách từng người", 8.7, 1.75, 4.0, 2.0, { fontSize: 16, color: C.grey, valign: "top" });

  // 3 Mục lục (5 thẻ cột)
  s = pres.addSlide({ masterName: "NOI_DUNG" });
  s.addText("Mở đầu", { placeholder: "muc" }); s.addText("Nội dung trình bày", { placeholder: "tieu_de" }); s.addText("Mở đầu", { placeholder: "phan" });
  const parts = [["Khảo sát", "Nghiệp vụ, yêu cầu phân tích, hệ thống dữ liệu, ERD"], ["Phân tích & thiết kế", "EDA, kiến trúc, ETL, OLTP → OLAP, mô hình"], ["Xây dựng hệ thống", "DB1–DB4, DAX, OLAP, publish"], ["Chủ đề mở rộng", "Lakehouse, thu thập API, D8"], ["Tổng kết", "Đối chiếu yêu cầu, bài học, hướng phát triển"]];
  const cw = (CW - 4 * 0.25) / 5;
  parts.forEach(([t, d], i) => {
    const x = X0 + i * (cw + 0.25);
    box(s, pres, x, 1.75, cw, 4.6, i === 0 ? C.ink : C.lav);
    T(s, String(i + 1).padStart(2, "0"), x, 2.1, cw, 0.9, { fontSize: 40, bold: true, color: i === 0 ? C.amber : C.vio, align: "center" });
    T(s, t, x + 0.15, 3.15, cw - 0.3, 0.8, { fontSize: 18, bold: true, color: i === 0 ? C.white : C.deep, align: "center", valign: "top" });
    T(s, d, x + 0.2, 4.05, cw - 0.4, 1.6, { fontSize: 14, color: i === 0 ? "D9CCF2" : C.grey, align: "center", valign: "top" });
  });

  // 4 Chuyển phần
  s = pres.addSlide({ masterName: "CHUYEN_PHAN" });
  s.addText("PHẦN 1", { placeholder: "so_phan" }); s.addText("Khảo sát", { placeholder: "tieu_de" });
  s.addText("Khảo sát chung, nghiệp vụ, hệ thống hiện tại, yêu cầu phân tích và hệ thống dữ liệu", { placeholder: "noi_dung" });

  // 5 Nội dung + hộp tối + kết luận
  s = pres.addSlide({ masterName: "NOI_DUNG_KL" });
  s.addText("1.4 · Hệ thống dữ liệu", { placeholder: "muc" }); s.addText("Quy mô dữ liệu: 11 bảng, 121 MB, 1,56 triệu dòng", { placeholder: "tieu_de" }); s.addText(P[1], { placeholder: "phan" });
  s.addText(bullets(["Bán hàng (oltp): 9 bảng, 1.550.922 dòng", "Marketing (crm): 2 bảng, 8.842 dòng", "Hai hệ thống chỉ gặp nhau ở seller_id"]), { x: X0, y: 1.75, w: 7.4, h: 3.8, fontSize: 20, valign: "top", paraSpaceAfter: 10, isTextBox: true });
  box(s, pres, 8.4, 1.8, 4.33, 3.6, C.box);
  T(s, "Điểm đáng chú ý", 8.7, 2.0, 3.8, 0.4, { fontSize: 16, bold: true, color: C.amber });
  T(s, bullets(["Bảng toạ độ chiếm 64% số dòng", "Chỉ 19.015 mã bưu chính", "ETL gom về mức mã bưu chính"], { color: C.white }), 8.7, 2.5, 3.8, 2.7, { fontSize: 16, color: C.white, valign: "top", paraSpaceAfter: 6 });
  s.addText("Dữ liệu nhỏ: nạp theo lô hằng ngày bằng PostgreSQL là đủ", { placeholder: "ket_luan" });

  // 6 Sơ đồ bằng shape
  s = pres.addSlide({ masterName: "NOI_DUNG_KL" });
  s.addText("1.1 · Nghiệp vụ", { placeholder: "muc" }); s.addText("Quy trình thu hút seller: MQL đến seller có đơn", { placeholder: "tieu_de" }); s.addText(P[1], { placeholder: "phan" });
  const steps = [["MQL (lead)", C.lav], ["SDR sàng lọc lead", C.lav], ["SR tư vấn, chốt deal", C.lav], ["Deal chốt (won)", "FDF0DA"], ["Seller có đơn đầu", "FDF0DA"]];
  const bw = 2.05, gap = (CW - 5 * bw) / 4, by = 2.6, bh = 1.15;
  steps.forEach(([t, col], i) => {
    const x = X0 + i * (bw + gap);
    box(s, pres, x, by, bw, bh, col, i < 3 ? C.vio : C.amber);
    T(s, t, x, by, bw, bh, { fontSize: 18, bold: true, color: C.deep, align: "center", valign: "middle" });
    if (i < 4) s.addShape(pres.shapes.LINE, { x: x + bw + 0.05, y: by + bh / 2, w: gap - 0.1, h: 0, line: { color: C.ink, width: 2, endArrowType: "triangle" } });
  });
  const tag = (i, t) => {
    const x = X0 + i * (bw + gap);
    s.addShape(pres.shapes.LINE, { x: x + bw / 2, y: by + bh, w: 0, h: 0.5, line: { color: C.grey, width: 1.25 } });
    s.addShape(pres.shapes.RECTANGLE, { x: x + 0.05, y: by + bh + 0.5, w: bw - 0.1, h: 0.5, fill: { color: C.white }, line: { color: C.grey, width: 1, dashType: "dash" } });
    T(s, t, x + 0.05, by + bh + 0.5, bw - 0.1, 0.5, { fontSize: 12, align: "center", valign: "middle", fontFace: "Consolas" });
  };
  tag(0, "crm.mql"); tag(3, "crm.closed_deals"); tag(4, "fact_lead_funnel");
  const span = (i0, i1, y, t, up) => {
    const x0 = X0 + i0 * (bw + gap) + 0.2, x1 = X0 + i1 * (bw + gap) + bw - 0.2;
    s.addShape(pres.shapes.LINE, { x: x0, y, w: x1 - x0, h: 0, line: { color: C.vio, width: 2.5, beginArrowType: "triangle", endArrowType: "triangle" } });
    T(s, t, x0, up ? y - 0.48 : y + 0.08, x1 - x0, 0.4, { fontSize: 18, bold: true, color: C.vio, align: "center" });
  };
  span(0, 3, 2.25, "liên hệ → chốt: TB 48,5 ngày", true);
  span(3, 4, 5.45, "chốt → đơn đầu: TB 51,9 ngày", false);
  s.addText("Liên hệ → chốt mất TB 48,5 ngày, chốt → đơn đầu thêm 51,9 ngày", { placeholder: "ket_luan" });

  // 7 Hình lớn
  s = pres.addSlide({ masterName: "HINH_KL" });
  s.addText("2.1 · Khám phá dữ liệu · Phân bố", { placeholder: "muc" }); s.addText("Pareto danh mục: 18/74 danh mục tạo 80% GMV", { placeholder: "tieu_de" }); s.addText(P[2], { placeholder: "phan" });
  fitImage(s, FIG("3-3-1_pareto_category.png"), { x: X0, y: 1.6, w: CW, h: 4.1 });
  s.addText("Hình 2.5. Pareto GMV theo danh mục (Python) · ảnh mẫu khổ Beamer, P13 vẽ lại đúng khung này", { placeholder: "chu_thich" });
  s.addText("Phân tích doanh thu tập trung vào 18 danh mục đầu", { placeholder: "ket_luan" });

  // 8 Bảng
  s = pres.addSlide({ masterName: "NOI_DUNG_KL" });
  s.addText("1.4 · Hệ thống dữ liệu", { placeholder: "muc" }); s.addText("Quy mô theo hệ thống nguồn", { placeholder: "tieu_de" }); s.addText(P[1], { placeholder: "phan" });
  const hd = (t) => ({ text: t, options: { bold: true, color: C.white, fill: { color: C.box } } });
  const hl = (t, b) => ({ text: t, options: { fill: { color: "FDF0DA" }, bold: !!b } });
  s.addTable([
    [hd("Hệ thống"), hd("Số bảng"), hd("Số dòng"), hd("Ghi chú")],
    ["Bán hàng (oltp)", "9", "1.550.922", "đơn, dòng hàng, thanh toán, review, khách, sản phẩm, seller…"],
    ["Marketing (crm)", "2", "8.842", "MQL và deal đã chốt"],
    [hl("Trong đó: geolocation"), hl("1"), hl("1.000.163"), hl("64% số dòng, 19.015 mã bưu chính")],
    [{ text: "Tổng", options: { bold: true } }, { text: "11", options: { bold: true } }, { text: "1.559.764", options: { bold: true } }, "121 MB"],
  ], { x: X0, y: 1.75, w: CW, colW: [3.0, 1.4, 2.0, CW - 6.4], fontSize: 16, fontFace: "Arial", color: C.text, border: { type: "solid", pt: 0.75, color: C.line }, rowH: 0.6, valign: "middle" });
  s.addText("Một bảng toạ độ chiếm gần 2/3 dữ liệu", { placeholder: "ket_luan" });

  // 9 Thẻ số
  s = pres.addSlide({ masterName: "NOI_DUNG_KL" });
  s.addText("5.1 · Kết quả", { placeholder: "muc" }); s.addText("Kết quả đạt được: kho chạy từ đầu đến cuối", { placeholder: "tieu_de" }); s.addText(P[5], { placeholder: "phan" });
  const cards = [["98.199", "đơn hàng trong kho"], ["13,49 tr", "GMV (BRL)"], ["10 · 6", "dimension · fact"], ["16/16", "bảng khớp lakehouse"]];
  const kw = (CW - 3 * 0.3) / 4;
  cards.forEach(([n, l], i) => {
    const x = X0 + i * (kw + 0.3);
    box(s, pres, x, 1.8, kw, 2.0, C.lav);
    s.addShape(pres.shapes.RECTANGLE, { x: x + 0.35, y: 1.8, w: kw - 0.7, h: 0.07, fill: { color: i % 2 ? C.amber : C.vio } });
    T(s, n, x, 2.05, kw, 1.0, { fontSize: 44, bold: true, color: C.vio, align: "center" });
    T(s, l, x, 3.1, kw, 0.5, { fontSize: 16, color: C.grey, align: "center" });
  });
  T(s, bullets(["Hai nguồn oltp và crm hợp nhất qua seller_id", "Bốn dashboard Power BI và một dashboard dữ liệu API (D8)"]), X0, 4.1, CW, 1.6, { fontSize: 20, valign: "top", paraSpaceAfter: 6 });
  s.addText("Số liệu kho khớp nguồn và khớp lakehouse ở 16/16 bảng", { placeholder: "ket_luan" });

  // 10 Hai cột: code DAX
  s = pres.addSlide({ masterName: "HAI_COT_KL" });
  s.addText("3.2 · DB1 Tổng quan", { placeholder: "muc" }); s.addText("DAX chính: tăng trưởng và cảnh báo màu", { placeholder: "tieu_de" }); s.addText(P[3], { placeholder: "phan" });
  s.addText(bullets(["GMV chỉ tính đơn không Failed", "YoY so cùng kỳ bằng SAMEPERIODLASTYEAR", "Màu cảnh báo trả về mã màu, dùng cho định dạng điều kiện"]), { placeholder: "cot_trai" });
  box(s, pres, 5.6, 1.7, 7.13, 4.2, "3B3155");
  T(s, "GMV YoY % =\nDIVIDE ( [GMV] - [GMV last year], [GMV last year] )\n\nGMV last year =\nCALCULATE ( [GMV], SAMEPERIODLASTYEAR ( dim_date[full_date] ) )", 5.85, 1.9, 6.7, 3.8, { fontSize: 14, fontFace: "Consolas", color: "E9E2F7", valign: "top" });
  s.addText("Mỗi KPI định nghĩa một lần bằng DAX, đối chiếu với SQL", { placeholder: "ket_luan" });

  // 11 Phụ lục
  s = pres.addSlide({ masterName: "PHU_LUC" });
  s.addText("2.3 · ETL", { placeholder: "muc" }); s.addText("Chi tiết: dòng bị loại theo bảng", { placeholder: "tieu_de" }); s.addText("Phụ lục", { placeholder: "phan" });
  s.addText(bullets(["Slide chi tiết để trả lời câu hỏi; không tính vào thời gian trình bày"]), { placeholder: "noi_dung" });

  // 12 Cảm ơn
  s = pres.addSlide({ masterName: "CAM_ON" });
  s.addText("Cảm ơn thầy và các bạn đã lắng nghe", { placeholder: "tieu_de" });
  s.addText("Hỏi đáp", { placeholder: "noi_dung" });
}

(async () => {
  const out = path.join(__dirname, "out"); fs.mkdirSync(out, { recursive: true });
  const p = new pptxgen(); p.company = "Nhom 19"; defineLayouts(p); samples(p);
  await p.writeFile({ fileName: path.join(out, "Olist_Nhom19_giao_dien_mau.pptx") });
  await applyTheme(path.join(out, "Olist_Nhom19_giao_dien_mau.pptx"), THEME);
  const q = new pptxgen(); q.company = "Nhom 19"; defineLayouts(q);
  q.addSlide({ masterName: "NOI_DUNG" }).addText("xoá", { placeholder: "tieu_de" });
  await q.writeFile({ fileName: path.join(out, "Olist_Nhom19_template.pptx") });
  await applyTheme(path.join(out, "Olist_Nhom19_template.pptx"), THEME);
  console.log("done");
})();
