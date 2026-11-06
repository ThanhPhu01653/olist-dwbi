# HUST Beamer Theme (Đại học Bách khoa Hà Nội)

Bộ giao diện trình chiếu **LaTeX Beamer** chuẩn hóa theo **Sổ tay nhận diện thương hiệu Đại học Bách khoa Hà Nội** và bộ mẫu bài giảng điện tử PowerPoint 2026 chính thức.

> [!NOTE]
> Dự án mẫu trình chiếu này được thiết kế và chuẩn hóa với sự đồng hành và hỗ trợ của **AI Agent** (Google DeepMind / Antigravity pair programming).

---

## 📌 Tài Nguyên Gốc & Bản Trình Chiếu Mẫu

- **Tài liệu quy chuẩn thương hiệu**:
  - 📖 [Sổ tay hướng dẫn nhận diện thương hiệu ĐHBK Hà Nội](references/so_tay_huong_dan_nhan_dien_thuong_hieu_dhbk_ha_noi_pdf.pdf)
- **Bộ mẫu bài giảng PowerPoint 2026 chính thức**:
  - 🔷 [HUST Blue PPT Template (Tỉ lệ 16:9)](references/%5BHUST%5D%20-%20BLUE%20PPT%20TEMPLATE%202026%20-%2016x9.pptx)
  - 🔷 [HUST Blue PPT Template (Tỉ lệ 4:3)](references/%5BHUST%5D%20-%20BLUE%20PPT%20TEMPLATE%202026%20-%204x3.pptx)
  - 🔴 [HUST Red PPT Template (Tỉ lệ 16:9)](references/%5BHUST%5D%20-%20RED%20PPT%20TEMPLATE%202026%20-%2016x9.pptx)
  - 🔴 [HUST Red PPT Template (Tỉ lệ 4:3)](references/%5BHUST%5D%20-%20RED%20PPT%20TEMPLATE%202026%20-%204x3.pptx)
- **Bản xem trước sản phẩm (PDF Previews)**:
  - 📊 [test_deck.pdf](test_deck.pdf): Bản trình chiếu hoàn chỉnh 16:9 tông màu Xanh lam (*Blue theme*, logo Khoa Toán - Tin FaMI, thanh mảnh, thanh tiến trình, thuật toán đa ngôn ngữ).
  - 📊 [test_variants.pdf](test_variants.pdf): Bản trình chiếu hoàn chỉnh 4:3 tông màu Đỏ (*Red theme*, Viện CNTT&TT, số trang trên thanh tiêu đề, chân trang đa trích dẫn 2 cột).

---

## 1. Tính Năng Nổi Bật

- **Đúng chuẩn nhận diện thương hiệu HUST**:
  - Hệ màu quy chuẩn: Đỏ cờ (`#CE1628`), Vàng sao (`#F3C108`), Đen (`#231F20`), Xanh lam đậm (`#003366`), Đỏ thứ cấp (`#C02034`), Vàng hổ phách (`#E59C0A`), Cam (`#F57F20`).
  - Phông chữ quy chuẩn: Tiêu đề dùng **Avant Garde** (*TeX Gyre Adventor*), nội dung dùng **Lato**, **Arial** hoặc **Times New Roman** với hỗ trợ tiếng Việt đầy đủ qua Unicode / `fontspec`.
  - Họa tiết chấm tròn chuyển màu (*halftone ring pattern*) đặc trưng ở trang bìa, trang chuyển mục (*section panel*) và slide cảm ơn / kết luận (*closing slide*).
- **Linh hoạt đa tỉ lệ (Aspect Ratio)**:
  - Tự động nhận diện và căn chỉnh tọa độ vector chính xác theo kích thước khung hình: 16:9 (`aspectratio=169`), 4:3 (`aspectratio=43`), 16:10 (`aspectratio=1610`), 5:4 (`aspectratio=54`)...
- **Tùy biến cao**:
  - Hỗ trợ cả 2 tông màu chính thức: **Xanh (Blue)** và **Đỏ (Red)**.
  - Tùy chọn thanh nhấn dưới tiêu đề: thanh mảnh (`thin`) hoặc thanh dày (`thick`).
  - Tùy chọn định dạng số trang: phân số (`fraction`: 3/12), số thường (`plain`: 3), hoặc ẩn (`none`).
  - Tùy chọn 5 kiểu logo chân trang (`full`, `mark`, `wordmark`, `hust`, `none`).

---

## 2. Cấu Trúc Gói Theme

Thư mục `HUST-Beamer-Theme/` được module hóa chuyên nghiệp theo chuẩn Beamer:

```text
HUST-Beamer-Theme/
├── beamerthemeHUST.sty        # Gói theme chính (điều phối tất cả các subtheme)
├── hust-core.sty              # Lõi: Tùy chọn pgfkeys, màu thương hiệu, tỉ lệ & tọa độ vector
├── beamercolorthemeHUST.sty   # Subtheme màu sắc (structure, frametitle, blocks, footer...)
├── beamerfontthemeHUST.sty    # Subtheme phông chữ (Lato, Times, Arial, Adventor...)
├── beamerinnerthemeHUST.sty   # Subtheme thành phần bên trong (title page, panel, blocks, lists)
├── beamerouterthemeHUST.sty   # Subtheme khung ngoài (headline, frametitle, footer, dark frames)
├── hust-setup.tex             # Cấu hình mở rộng học thuật: bảng biểu, gói toán, mã code, danh sách
├── assets/                    # Thư mục 28 tài nguyên đồ họa độ nét cao (PNG vector-rendered)
├── references/                # Sổ tay nhận diện thương hiệu & 4 file mẫu PowerPoint chính thức 2026
├── test_deck.tex              # File mẫu trình chiếu 16:9 Blue hoàn chỉnh (font=lato, logo FaMI)
├── test_deck.pdf              # Bản kết xuất PDF mẫu 16:9 Blue
├── test_variants.tex          # File mẫu trình chiếu 4:3 Red hoàn chỉnh (font=cm, logo ĐHBK)
├── test_variants.pdf          # Bản kết xuất PDF mẫu 4:3 Red
├── refs.bib                   # File cơ sở dữ liệu thư mục trích dẫn (Biber / BibLaTeX)
└── README.md                  # Tài liệu hướng dẫn sử dụng chi tiết
```

---

## 3. Cài Đặt Trình Biên Dịch Trong TeXstudio

Theme khuyến nghị sử dụng **LuaLaTeX** (trình biên dịch hiện đại nhất, hỗ trợ xử lý phông chữ và hình ảnh tối ưu) hoặc **XeLaTeX**.

### 3.1. Thiết lập mặc định sang LuaLaTeX & Biber:

1. Mở **TeXstudio**.
2. Vào menu: **Options** (Tùy chọn) $\rightarrow$ **Configure TeXstudio** (Cấu hình TeXstudio).
3. Chọn thẻ **Build** (Biên dịch) ở cột bên trái:
   - Tại mục **Default Compiler** (Trình biên dịch mặc định), chọn **LuaLaTeX** (hoặc **XeLaTeX**).
   - Tại mục **Default Bibliography** (Trình xử lý tài liệu tham khảo), chọn **Biber**.
4. Nếu có sử dụng gói tô màu mã nguồn **`minted`** (C++, Java, Rust...), cần cài đặt **Python** (`pip install pygments latexminted`) và thêm cờ **`-shell-escape`** vào lệnh biên dịch LuaLaTeX (trong thẻ **Commands** $\rightarrow$ **LuaLaTeX**: `lualatex.exe -synctex=1 -shell-escape -interaction=nonstopmode %.tex`).
5. Nhấn **OK** để lưu lại. Khi mở file `.tex`, nhấn **F5** (Build & View) để biên dịch toàn bộ quy trình `LuaLaTeX -> Biber -> LuaLaTeX`.

---

## 4. Hướng Dẫn Sử Dụng Cơ Bản

Tạo một file trình chiếu mới (ví dụ `presentation.tex`):

```latex
\documentclass[aspectratio=169,10pt]{beamer}
%% Nạp theme HUST với các tùy chọn
\usetheme[
  color=blue,              % blue | red
  font=lato,               % lato | cm | times | arial
  titlefont=avantgarde,    % avantgarde (mặc định theo sổ tay) | same
  footerlogo=mark,         % full | mark | wordmark | hust | none
  bar=thin,                % thin | thick (thanh dày cho phụ đề)
  titlepage=cover,         % cover | light (nền chấm mờ cho 4:3) | solid (nền màu đặc) | dark | welcome
  coverbg=cover,           % cover | light | solid
  sectionpage=panel,       % panel | none
  numbering=fraction,      % fraction (n/N) | plain (n) | none
  progressbar=on,          % on | off (thanh tiến trình phân mục thông minh)
  headerright=off,         % off | pagenumber (số trang lên thanh tiêu đề) | logo (kèm headerlogo=...)
  headerlogo=fami-shield.png, % Hiển thị logo kèm viền trắng chuẩn sổ tay ở góc phải thanh tiêu đề
  framebg=on,              % on | off | blue | red (họa tiết thoi chéo Sổ tay trang 1 cho frame & panel)
  footermeta=on,           % on | off (tác giả, tiêu đề, ngày ngắn ở chân trang)
  logolayout=2,            % 1 | 2 | 3 | 4a | 4b
  dateaddress=on,          % on | off (kèm địa danh trước ngày tháng)
  address={Hà Nội}
]{HUST}

%% Nạp cấu hình mở rộng học thuật, toán học, bảng biểu & hộp ghi chú
\input{hust-setup}

\usepackage[backend=biber,style=numeric,sorting=none,maxcitenames=2,mincitenames=1]{biblatex}
\addbibresource{refs.bib}

\title[Tiêu đề rút gọn ở chân trang]{{\normalsize ĐỒ ÁN TỐT NGHIỆP CỬ NHÂN}\\[5pt] {\bfseries TIÊU ĐỀ BÁO CÁO / THUYẾT TRÌNH}}
\subtitle{Phần tiêu đề phụ ngắn gọn}
\author[Nguyễn Văn A]{Nguyễn Văn A - 20231234 \\ GVHD: PGS. TS. Lê Văn Thu C}
\institute{Khoa Toán - Tin,\\Đại học Bách khoa Hà Nội}
\date{\today}

\begin{document}

%% 0a. Slide chào mừng nền tối (Welcome Screen - PPT Slide 1)
\begin{hustwelcomeframe}
\end{hustwelcomeframe}

%% 0b. Slide chào mừng nền sáng (tùy chọn)
\begin{hustwelcomeframe}[bg=background, footer={DEMO SHOWCASE}]
\end{hustwelcomeframe}

%% 1. Trang bìa chính thức
\hustsetup{slogantext={}}
\begin{frame}[plain,noframenumbering]
  \titlepage
\end{frame}

%% 2. Mục lục toàn cục (tự động ẩn progress bar, hỗ trợ tách 2 cột)
\begin{frame}[noprogressbar]{\husttoctitle}{\husttocsubtitle}
  \tableofcontents[split=3,hideallsubsections]
\end{frame}

%% 3. Nội dung các phần
\section{Giới thiệu}
\subsection{Tổng quan nghiên cứu}
\begin{frame}{Tiêu đề slide}{Tiêu đề phụ của slide}
  \begin{itemize}
    \item Ý chính thứ nhất có trích dẫn\cite{bellocruz2025} và \note{ghi chú}{Giải thích ngắn gọn ở chân trang}.
  \end{itemize}
  \begin{definition}[Khái niệm cơ bản]
    Nội dung định nghĩa toán học trong môi trường chuẩn Beamer.
  \end{definition}
\end{frame}

%% 4. Phần không hiển thị slide chuyển mục (tùy chọn)
\hustsection[panel=false]
\section{Thực nghiệm & Kết luận}
\begin{frame}{Kết quả thực nghiệm}
  Nội dung kết quả...
\end{frame}

%% 5. Tài liệu tham khảo (tự động ẩn progress bar, hỗ trợ phân trang từ mục N đến M)
\begin{hustreferencesframe}[from=1, to=2]
\end{hustreferencesframe}

%% 6. Slide kết luận / cảm ơn nền tối
\begin{hustdarkframe}
  \centering
  \vspace*{0.2\paperheight}
  {\Huge\bfseries\color{white} CẢM ƠN QUÝ THẦY CÔ\\VÀ CÁC BẠN ĐÃ LẮNG NGHE!\par}
  \vspace{1.5em}
  {\large\color{white!85} Q \& A\par}
\end{hustdarkframe}
\end{document}
```

---

## 5. Bảng Tùy Chọn Chi Tiết (`\usetheme[...]` hoặc `\hustsetup{...}`)

| Tùy Chọn | Giá Trị Hợp Lệ | Mặc Định | Ý Nghĩa / Mô Tả |
| :--- | :--- | :--- | :--- |
| `color` | `blue`, `red` | `blue` | Chọn tông màu chủ đạo: Xanh lam đậm hoặc Đỏ cờ. |
| `font` | `lato`, `arial`, `times`, `cm` | `lato` | Phông chữ chính cho nội dung (`lato`: Lato; `arial`: Arial; `times`: Times New Roman; `cm`: Computer Modern / Latin Modern). |
| `titlefont` | `avantgarde`, `same` | `avantgarde` | `avantgarde` sử dụng TeX Gyre Adventor cho tiêu đề (phông nhận diện chính của HUST theo Sổ tay thương hiệu trang 13–14). Chọn `same` nếu muốn dùng cùng phông với nội dung. |
| `bar` | `thin`, `thick` | `thin` | Kiểu thanh nhấn nằm dưới dải tiêu đề:<br>• `thin`: Thanh mảnh nằm dưới dải màu. Áp dụng dải màu tối ưu chiều cao (`bandThinB`), căn lề đỉnh và đáy đối xứng tuyệt đối (đệm 6px cả trên và dưới), giải quyết dứt điểm lỗi chạm mép chữ khi có dấu tiếng Việt hoặc chữ in hoa trên cả hai tỉ lệ `16:9` và `4:3`. Cả `frametitle` và `framesubtitle` nằm chung trong dải màu chính.<br>• `thick`: Thanh dày theo mẫu bài giảng PPT gốc; khi có `framesubtitle`, phụ đề sẽ tự động chuyển xuống nằm trọn bên trong thanh dày với chữ màu trắng (`HUSTWhite`). |
| `footerlogo` | `full`, `mark`, `wordmark`, `hust`, `none` | `full` | Logo hiển thị tại góc trái chân trang:<br>• `full`: Huy hiệu + Chữ Đại học Bách khoa Hà Nội.<br>• `mark`: Chỉ huy hiệu chiếc compa và ngôi sao.<br>• `wordmark`: Chữ ĐẠI HỌC BÁCH KHOA HÀ NỘI.<br>• `hust`: Chữ HUST.<br>• `none`: Không hiển thị logo chân trang. |
| `titlepage` | `cover`, `light`, `solid`, `dark`, `welcome` | `cover` | Kiểu trang bìa:<br>• `cover`: Nền trắng với vòng chấm tròn đậm nguyên bản bên phải (`bg-cover`).<br>• `light`: Nền trắng với vòng chấm tròn làm dịu độ sáng (`+20%` lightness / `40%` tint tương tự sắc độ chấm trên nền tối), giúp chữ của tác giả/đơn vị trên khung hình hẹp như `4:3` nổi bật hoàn toàn khi đi qua vùng đồ họa.<br>• `solid`: Nền màu đặc chủ đạo (`hustmain`: Xanh hoặc Đỏ) không có vòng chấm đồ họa, toàn bộ chữ và logo HUST chuyển sang tông trắng/vàng tương phản cao.<br>• `dark`: Nền xanh/đỏ tối kèm vòng chấm tròn đồng tâm (`bg-dark`), căn giữa.<br>• `welcome`: Màn hình chào mừng HUST tròn đồng tâm. |
| `coverbg` / `titlebg` | `cover`, `light`, `solid` | `cover` | Tùy chọn phụ để chuyển đổi nhanh nền trang bìa giữa 3 chế độ: `cover` (vòng chấm đậm mặc định), `light` (vòng chấm mờ dịu mắt cho tỉ lệ hẹp `4:3`), hoặc `solid` (nền màu đặc không đồ họa). |
| `logolayout` | `1`, `2`, `3`, `4a`, `4b`, `1line`, `2lines` | `2` | Bố cục logo HUST trên trang bìa (chọn tùy chọn 1 dòng hoặc 2 dòng):<br>• `1` (hoặc `1line`): Bố cục **1 dòng Việt – Anh** (Hình 7: 1 dòng tiếng Việt + 1 dòng tiếng Anh có độ rộng bằng nhau tuyệt đối).<br>• `2` (hoặc `2lines`): Bố cục **2 dòng Việt – Anh** (Hình 7b: 2 dòng tiếng Việt + 2 dòng tiếng Anh - chuẩn bìa `logo-full`).<br>• `3`: Bố cục **Đơn vị thành viên 1 dòng** (Hình 9a: 1 dòng ĐHBKHN + gạch ngăn cách + 1 dòng tên đơn vị in hoa, khi dùng kèm `unit={...}`).<br>• `4a`: Bố cục **Đơn vị 2 dòng – ĐHBKHN 2 dòng đối xứng** (2 dòng ĐHBKHN + gạch ngăn cách + 2 dòng đơn vị, khi dùng kèm `unit={...}`).<br>• `4b`: Bố cục **Đơn vị 2 dòng – ĐHBKHN 1 dòng căn giữa** (1 dòng ĐHBKHN + gạch ngăn cách + 2 dòng đơn vị căn giữa trọng tâm huy hiệu, khi dùng kèm `unit={...}`). |
| `unit` / `logounit` | Chuỗi văn bản | Trống | Tên đơn vị thành viên trên trang bìa:<br>• Tùy chọn 1 dòng: `unit={TRƯỜNG ĐIỆN - ĐIỆN TỬ}` (Tên trường 1 dòng + gạch ngang + đơn vị 1 dòng - Hình 9a).<br>• Tùy chọn 2 dòng: `unit={VIỆN CÔNG NGHỆ ĐIỀU KHIỂN\newline VÀ TỰ ĐỘNG HÓA}` (Tự động chuyển sang bố cục 2 dòng căn giữa `layout=4b` hoặc đối xứng `layout=4a`). |
| `logovn` | Chuỗi văn bản | `ĐẠI HỌC BÁCH KHOA HÀ NỘI` | Tùy biến dòng tên trường tiếng Việt của logo chính trên trang bìa. |
| `logoen` | Chuỗi văn bản | `HANOI UNIVERSITY OF SCIENCE AND TECHNOLOGY` | Tùy biến dòng tên trường tiếng Anh của logo chính trên trang bìa. |
| `logomode` | `vector`, `image` | `vector` | Chế độ kết xuất logo trang bìa (`vector`: vẽ cụm chữ vector sắc nét kèm huy hiệu; `image`: dùng ảnh tĩnh `logo-full.png`). |
| `logo2` / `logo2image` | Đường dẫn file ảnh | Trống | Đường dẫn ảnh huy hiệu đơn vị phối hợp/thành viên thứ 2 trên trang bìa (ví dụ `logo2image=fami-shield.png`). |
| `logo2vn` | Chuỗi văn bản | `KHOA TOÁN - TIN` | Tên tiếng Việt của đơn vị phối hợp thứ 2 trên trang bìa. |
| `logo2en` | Chuỗi văn bản | `Faculty of Mathematics and Informatics` | Tên tiếng Anh của đơn vị phối hợp thứ 2 trên trang bìa. |
| `logo2color` | Tên màu | `famiblue` | Mã màu nhận diện đơn vị thứ 2 (khóa cố định `famiblue` `#0062A5` cho Khoa Toán - Tin). |
| `logo2layout` | `1`, `2` | `1` | Bố cục logo đơn vị thứ 2 trên trang bìa (chọn tùy chọn 1 dòng hoặc 2 dòng):<br>• `1`: Bố cục **1 dòng** (1 dòng tiếng Việt + 1 dòng tiếng Anh).<br>• `2`: Bố cục **2 dòng** (2 dòng tiếng Việt + 2 dòng tiếng Anh). |
| `sectionpage` | `panel`, `none` | `none` | Tự động chèn trang chuyển mục (*section transition*) chia đôi với chữ HUST bên trái khi gặp lệnh `\section`. |
| `sectionpanel` | `on`, `off`, `true`, `false` | `on` | Bật/tắt mặc định việc hiển thị slide chuyển mục khi `sectionpage=panel`. Có thể ghi đè trên từng mục bằng `\hustsection[panel=true\|false]` ngay trước `\section`. |
| `panelsocial` | `on`, `off`, `true`, `false` | `on` | Bật/tắt dải thông tin liên kết mạng xã hội (`hust.edu.vn`, `fb.com/dhbkhn`) ở góc trái dưới của trang chuyển mục (`panel`). |
| `wordmark` | `on`, `off`, `true`, `false`, `none` | `on` | Bật/tắt hiển thị cụm chữ `HUST` trung tâm trên slide chào mừng (`hustwelcomeframe`). |
| `slogan` | `on`, `off`, `true`, `false`, `none` | `on` | Bật/tắt hiển thị dòng khẩu hiệu (`ONE LOVE. ONE FUTURE.`) ở chân trang bìa và slide chào mừng. |
| `slogantext` | Chuỗi văn bản | `ONE LOVE. ONE FUTURE.` | Tùy biến nội dung khẩu hiệu hiển thị ở chân trang bìa / slide chào mừng (đặt `slogantext={}` nếu muốn ẩn riêng trên trang bìa). |
| `toctitle` | Chuỗi văn bản | `Nội dung chính` | Tiêu đề mặc định của trang mục lục toàn cục (`\husttoctitle`). |
| `tocsubtitle` | Chuỗi văn bản / `Hidden` | Trống (`Hidden`) | Phụ đề mặc định của trang mục lục toàn cục (`\husttocsubtitle`). Khi để trống hoặc `Hidden`, tiêu đề chính tự động căn giữa dải màu. |
| `reftitle` | Chuỗi văn bản | `Tài liệu tham khảo` | Tiêu đề mặc định của các trang tài liệu tham khảo (`\hustreftitle`). |
| `refsubtitle` | Chuỗi văn bản / `Hidden` | Trống (`Hidden`) | Phụ đề mặc định của các trang tài liệu tham khảo (`\hustrefsubtitle`). |
| `numbering` | `fraction`, `plain`, `none` | `plain` | Định dạng số trang ở góc phải chân trang hoặc góc phải thanh tiêu đề (`fraction`: `2 / 10`; `plain`: `2`). |
| `headerright` | `off`, `pagenumber` (`number`), `logo` | `off` | Tùy chọn hiển thị phần tử ở góc phải của thanh tiêu đề (`frametitle`):<br>• `off` (`none`): Để trống góc phải thanh tiêu đề như mặc định.<br>• `pagenumber` (hoặc `headernumber=on`, `pagenumberpos=header`): Đưa bộ đếm số trang (`4/21`) lên góc phải thanh tiêu đề, căn giữa theo chiều dọc dải màu chính (cả chế độ `bar=thin` lẫn `bar=thick`), sử dụng cùng cỡ chữ/phông với `frametitle` và mang màu vàng phụ đề (`hustsubyellow` `#FFDE59`) trên cả hai bản Đỏ & Xanh. Khi bật chế độ này, số trang ở chân trang tự động ẩn và ngày tháng trong `footermeta` tự động dồn sát lề phải để mở rộng không gian cho Tác giả — Tiêu đề — Ngày tháng.<br>• `logo`: Hiển thị thêm một logo (ví dụ `fami-shield.png` hoặc `hust-shield.png`) ở góc phải thanh tiêu đề, tự động vẽ khung nền chữ nhật màu trắng kèm viền đệm trắng (`1.4pt`) bao quanh logo theo đúng quy chuẩn đặt logo trên nền màu đậm của Sổ tay thương hiệu, đồng thời chừa khoảng đệm trên/dưới/phải để màu thanh tiêu đề bao quanh. |
| `headernumber` / `pagenumberpos` | `on`, `off` / `header`, `footer` | `off` / `footer` | Phím tắt tiện lợi để bật/tắt việc chuyển số trang lên góc phải thanh tiêu đề (`headernumber=on` tương đương `headerright=pagenumber`). |
| `headerlogo` | Đường dẫn ảnh / `on` / `off` | Trống (`off`) | Đường dẫn file ảnh logo đặt tại góc phải thanh tiêu đề (ví dụ `headerlogo=fami-shield.png`). Khi truyền tên file ảnh, theme tự động kích hoạt `headerright=logo` và bọc khung nền trắng chuẩn Sổ tay thương hiệu. |
| `framebg` / `diagbg` / `texture` | `off`, `on` (`auto`, `diag`), `blue`, `red` | `off` | Bật/tắt họa tiết các hình thoi bo góc xếp chéo trích xuất vector từ **Trang 1 Sổ tay nhận diện thương hiệu** (đã khôi phục hoàn chỉnh hàng thoi đầu tiên bị cắt ở mép trên trong sổ tay) làm nền chìm bên phải cho toàn bộ các **frame nội dung** và **trang chuyển mục (`panel`)** (ngoại trừ màn hình chào mừng, trang bìa và trang kết thúc nền tối).<br>• `on` / `auto`: Tự động nạp phiên bản màu khớp với tông màu slide (`assets/bg-diag-blue.png` cho bản Xanh, `assets/bg-diag-red.png` cho bản Đỏ).<br>• `blue` / `red`: Chỉ định cứng phiên bản màu họa tiết thoi chéo. |
| `framebgopacity` | Số thực (`0.0` – `1.0`) | `0.08` | Độ đậm (opacity) của bộ lọc làm dịu họa tiết thoi chéo `framebg` trên nền slide và panel (mặc định `0.08` tức `8%` độ phủ màu đặc trên nền trắng, dịu hơn mức `15%` của bìa sổ tay để đảm bảo văn bản và công thức toán học nổi bên trên luôn sắc nét, dễ đọc tuyệt đối). |
| `coverlightopacity` | Số thực (`0.0` – `1.0`) | `0.18` | Độ đậm (opacity) của vòng chấm đồ họa trên trang bìa khi dùng `titlepage=light` / `coverbg=light` (mặc định `0.18` tức làm mờ 82% để tên tác giả/đơn vị trên tỉ lệ hẹp `4:3` dễ đọc hoàn toàn). |
| `progressbar` | `on`, `off` | `off` | Bật/tắt thanh tiến trình (*progress bar*) trên đỉnh slide với các ô chữ nhật chia đều theo section, đếm số subsection bằng các vạch chạy ngang, tự động hạ thấp header band để chừa khoảng trống hiển thị. Tự động ẩn trên trang mục lục toàn cục (*Nội dung chính*). Có thể tắt thủ công trên từng slide với `\begin{frame}[noprogressbar]`. |
| `footermeta` / `footerinfo` | `on`, `off` | `off` | Bật/tắt dải thông tin tích hợp chân trang: **Tác giả** (bên trái) — **Tiêu đề báo cáo** (ở giữa, tự ngắt dòng khi dài và neo đáy) — **Ngày rút gọn** (`DD/MM/YYYY`) — **Số trang** (giữ nguyên vị trí cố định bên phải).<br>• Khi tiêu đề dài thành nhiều dòng, thanh nhấn `hustaccent` sẽ tự động nhấc lên cao để nằm phía trên tiêu đề mà không cắt chữ.<br>• **Quy tắc ưu tiên**: Khi slide gọi bất kỳ lệnh trích dẫn `\cite` hoặc ghi chú chân trang `\note`, dải `footermeta` sẽ tự động ẩn để nhường toàn bộ không gian cho hộp trích dẫn. |
| `footerauthor` | Chuỗi văn bản | Trống | Tùy biến/ghi đè tên tác giả hiển thị tại `footermeta` (mặc định lấy `\insertshortauthor` hoặc `\insertauthor`). |
| `footertitle` | Chuỗi văn bản | Trống | Tùy biến/ghi đè tiêu đề hiển thị tại `footermeta` (mặc định lấy `\insertshorttitle` hoặc `\inserttitle`). |
| `footerdate` | Chuỗi văn bản | Trống | Tùy biến/ghi đè ngày tháng hiển thị tại `footermeta` (mặc định tự động tạo ngày ngắn `DD/MM/YYYY` từ `\today` hoặc từ tham số ngày của `\hustdate`). |
| `footertitlemax` | Số nguyên | `-1` (Không rút gọn) | Giới hạn số ký tự tối đa của tiêu đề báo cáo ở chân trang trước khi cắt ngắn bằng `...`. Đặt `-1` để giữ nguyên 100% tiêu đề đầy đủ (tự động cho phép ngắt dòng nếu dài). |
| `footerauthormax` | Số nguyên | `-1` (Không rút gọn) | Giới hạn số ký tự tối đa của tên tác giả ở chân trang trước khi cắt ngắn bằng `...`. Đặt `-1` để giữ nguyên toàn bộ tên tác giả. |
| `citemaxlines` | Số nguyên | `4` | Khóa cứng số dòng tối đa của hộp trích dẫn/chú thích chân trang (mặc định tối đa `4` dòng). |
| `citecolumns` | `auto`, `1`, `2` | `auto` | Chế độ cột của hộp trích dẫn chân trang: `auto` (1 cột khi $\le 4$ mục, tự động tách **2 cột** khi có $>4$ mục), `1` (luôn 1 cột), hoặc `2` (luôn chia 2 cột từ 2 mục trở lên). |
| `citetitlemax` | Số nguyên | `0` (Tự động) | Giới hạn số ký tự tối đa của tên bài báo trước khi cắt gọn bằng `...` (`0`: tự động co giãn vừa khít 1 dòng theo tỉ lệ `16:9` / `4:3`; `-1`: giữ nguyên tên bài báo đầy đủ không cắt ngắn). |
| `citejournalmax` | Số nguyên | `0` (Tự động) | Giới hạn số ký tự tối đa của tên tạp chí/hội nghị trước khi cắt gọn bằng `...` (`0`: tự động; `-1`: giữ nguyên đầy đủ không cắt ngắn). |
| `citemax` | Số nguyên | `8` | Số lượng mục trích dẫn/chú thích tối đa hiển thị trong hộp chân trang trên một slide (`-1`: không giới hạn số lượng mục). |
| `dateaddress` | `on`, `off`, `true`, `false`, `none` | `on` | Bật/tắt địa danh đứng trước ngày tháng trong `\today` (`Hà Nội, ngày ...` hoặc chỉ `ngày ...`). |
| `address` / `location` / `datecity` | Chuỗi văn bản / `none` | `Hà Nội` | Tùy biến tên địa danh hành chính đi kèm ngày tháng (ví dụ `address={Đà Nẵng}`, hoặc `address=none` để tắt địa danh). |
| `footer` | Chuỗi văn bản | Trống | Văn bản hiển thị chính giữa chân trang (ví dụ tên trường, tên hội nghị...). |
| `footerleft` | Chuỗi văn bản | Trống | Văn bản hiển thị bên cạnh logo chân trang (nếu có). |

---

## 6. Các Môi Trường Và Lệnh Đặc Biệt

### 6.1. Slide Chào Mừng (`\begin{hustwelcomeframe}`)

Tái hiện hoàn hảo màn hình mở đầu (Slide 1 trong bộ slide PPT gốc) tuân thủ quy chuẩn Hình 14 trong Sổ tay nhận diện thương hiệu (chiều rộng 2 dòng tiếng Việt và tiếng Anh khớp tuyệt đối với logo HUST):

1. **Màn hình chào mừng nền tối (`bg-dark`, mặc định)**:
   - Sử dụng `assets/footer-hust-white.png` (HUST trắng) và văn bản màu trắng.
   - Chân trang hiển thị khẩu hiệu **ONE LOVE. ONE FUTURE.** in đậm.
   ```latex
   \begin{hustwelcomeframe}
   \end{hustwelcomeframe}
   ```

2. **Màn hình chào mừng nền sáng (`bg-background`)**:
   - Sử dụng `assets/footer-hust.png` (HUST đỏ cờ chuẩn thương hiệu theo quy tắc không đổi màu logo trên nền sáng).
   - Văn bản tên trường hiển thị theo tông màu chủ đạo của slide (`hustmain`: xanh hoặc đỏ).
   - Chân trang hiển thị văn bản showcase (ví dụ **DEMO SHOWCASE**).
   ```latex
   \begin{hustwelcomeframe}[bg=background, footer={DEMO SHOWCASE}]
   \end{hustwelcomeframe}
   ```

3. **Cơ chế khóa cứng nhận diện (Lock-in Mechanism)**:
   - Toàn bộ phông chữ (`\hust@logofont` TeX Gyre Adventor) và sắc thái màu của logo HUST, huy hiệu, vạch ngăn cách được khóa cố định, không bị ảnh hưởng hay trôi màu/phông khi người dùng thay đổi phông chữ tài liệu (`font=times`, `font=cm`, `font=arial`) hoặc tỉ lệ màn hình (`16:9`, `4:3`).

### 6.2. Hướng Dẫn Kích Hoạt Tùy Chọn 1 Dòng & 2 Dòng Cho Logo (`1 line` / `2 lines`)

Trong thực tế thuyết trình tại ĐHBK Hà Nội, người dùng có nhu cầu lựa chọn linh hoạt giữa **Bố cục 1 dòng** (Tiêu chuẩn quốc gia gọn gàng, thanh thoát) và **Bố cục 2 dòng** (Tiêu chuẩn quốc tế trang trọng, cân đối). Bộ theme HUST cung cấp hai phương thức kích hoạt:

---

#### Cách 1: Thiết Lập Toàn Cục Trong Cấu Hình Theme (`\usetheme` hoặc `\hustsetup`)

Khi muốn thay đổi cách hiển thị cụm logo trên **Trang bìa (Title Page)** của bài thuyết trình:

```latex
%% =====================================================================
%% Trường hợp A: Logo HUST 1 dòng theo Tiêu chuẩn quốc gia (Hình 1 / Hình 7)
%% =====================================================================
\usetheme[
  logolayout=1,          % 1 (hoặc 1line): Bật bố cục 1 dòng quốc gia
]{HUST}

%% =====================================================================
%% Trường hợp B: Logo HUST 2 dòng theo Tiêu chuẩn quốc tế (Hình 2 / Hình 7b - Mặc định)
%% =====================================================================
\usetheme[
  logolayout=2,          % 2 (hoặc 2lines): Bật bố cục 2 dòng quốc tế
]{HUST}

%% =====================================================================
%% Trường hợp C: Kết hợp Đơn vị thành viên (Hình 9, Trường/Viện/Khoa)
%% =====================================================================
%% 1. Đơn vị 1 dòng:
\usetheme[
  unit={TRƯỜNG CƠ KHÍ}                                     % Tên trường 1 dòng + Đơn vị 1 dòng
]{HUST}

%% 2. Đơn vị 2 dòng – ĐHBKHN 1 dòng (Căn giữa trọng tâm huy hiệu - layout 4b):
\usetheme[
  logolayout=4b,
  unit={VIỆN CÔNG NGHỆ ĐIỀU KHIỂN\newline VÀ TỰ ĐỘNG HÓA}
]{HUST}

%% 3. Đơn vị 2 dòng – ĐHBKHN 2 dòng (Đối xứng - layout 4a):
\usetheme[
  logolayout=4a,
  unit={VIỆN CÔNG NGHỆ ĐIỀU KHIỂN\newline VÀ TỰ ĐỘNG HÓA}
]{HUST}

%% =====================================================================
%% Trường hợp D: Cấu hình Slot logo thứ 2 trên trang bìa (Khoa Toán - Tin / Đơn vị phối hợp)
%% =====================================================================
\usetheme[
  logo2image=fami-shield.png,                              % Ảnh huy hiệu đơn vị thành viên
  logo2vn={KHOA TOÁN - TIN},                               % Dòng tiếng Việt
  logo2en={Faculty of Mathematics and Informatics},         % Dòng tiếng Anh
  logo2color=famiblue,                                     % Khóa chuẩn màu nhận diện FaMI
  logo2layout=1                                            % 1: Bố cục 1 dòng | 2: Bố cục 2 dòng
]{HUST}
```

---

#### Cách 2: Gọi Trực Tiếp Trên Từng Slide Với Lệnh `\hustlogo[...]`

Lệnh `\hustlogo` vẽ cụm logo động bằng vector chuẩn xác tuyệt đối, hỗ trợ đầy đủ 6 bố cục như trong slide demo:

1. **Cụm chính thức Việt – Anh 1 dòng (Hình 7, `layout=1`)**:
   ```latex
   \hustlogo[height=0.85cm, layout=1]
   ```
   *Hiển thị 1 dòng tiếng Việt ("ĐẠI HỌC BÁCH KHOA HÀ NỘI") và 1 dòng tiếng Anh ("HANOI UNIVERSITY OF SCIENCE AND TECHNOLOGY") căn đều độ rộng tuyệt đối.*

2. **Bản 2 dòng Việt – Anh (Hình 7b, `layout=2`)**:
   ```latex
   \hustlogo[height=0.85cm, layout=2]
   ```
   *Hiển thị 2 dòng tiếng Việt ("ĐẠI HỌC \newline BÁCH KHOA HÀ NỘI") và 2 dòng tiếng Anh ("HANOI UNIVERSITY \newline OF SCIENCE AND TECHNOLOGY").*

3. **Đơn vị thành viên 1 dòng (Hình 9, `layout=3` hoặc truyền `unit={...}` 1 dòng)**:
   ```latex
   \hustlogo[height=0.85cm, layout=3, unit={TRƯỜNG CƠ KHÍ}]
   ```
   *Hiển thị 1 dòng tên trường + vạch ngăn cách màu xám + 1 dòng tên đơn vị thành viên in hoa màu đỏ cờ (khoảng cách an toàn $0.333 H$, tỉ lệ co chữ ngang `0.85` chuẩn quy chuẩn nhận diện).*

4. **Đơn vị 2 dòng – ĐHBKHN 2 dòng (Đối xứng, Hình 9 - `layout=4a`)**:
   ```latex
   \hustlogo[height=0.85cm, layout=4a, unit={VIỆN CÔNG NGHỆ ĐIỀU KHIỂN\newline VÀ TỰ ĐỘNG HÓA}]
   ```
   *Hiển thị 2 dòng tên trường + vạch ngăn cách ở giữa + 2 dòng tên đơn vị thành viên đối xứng.*

5. **Đơn vị 2 dòng – ĐHBKHN 1 dòng (Căn giữa trọng tâm, Hình 9 - `layout=4b`)**:
   ```latex
   \hustlogo[height=0.85cm, layout=4b, unit={VIỆN CÔNG NGHỆ ĐIỀU KHIỂN\newline VÀ TỰ ĐỘNG HÓA}]
   ```
   *Hiển thị 1 dòng tên trường + vạch ngăn cách + 2 dòng tên đơn vị thành viên, toàn bộ cụm được căn giữa theo trọng tâm của huy hiệu.*

6. **Cụm logo đơn vị thành viên / phối hợp (Khoa Toán - Tin FaMI, Hình 3)**:
   - **Tùy chọn 1 dòng (1 dòng VN, 1 dòng EN)**:
     ```latex
     \hustlogo[
       image=fami-shield.png,
       height=0.85cm,
       vn={KHOA TOÁN - TIN},
       en={Faculty of Mathematics and Informatics},
       color=famiblue,
       layout=1,
       equalwidth=false
     ]
     ```
   - **Tùy chọn 2 dòng (2 dòng VN, 2 dòng EN)**:
     ```latex
     \hustlogo[
       image=fami-shield.png,
       height=0.85cm,
       vn={KHOA\newline TOÁN - TIN},
       en={Faculty of\newline Mathematics and Informatics},
       color=famiblue,
       layout=2,
       equalwidth=false
     ]
     ```

8. **Cụm logo trên nền tối**: Thêm tùy chọn `dark`:
   ```latex
   \hustlogo[height=0.85cm, dark]
   ```

### 6.3. Slide Nền Tối Trang Trọng (`hustwordmarkframe` & `hustdarkframe`)

Dùng cho slide mở đầu đặc biệt hoặc slide kết thúc bài thuyết trình:

```latex
%% Slide nền tối với cụm chữ HUST và khẩu hiệu:
\begin{hustdarkframe}
  \centering
  \vspace*{0.2\paperheight}
  {\Huge\bfseries\color{white} CẢM ƠN QUÝ THẦY CÔ!\par}
\end{hustdarkframe}

%% Slide cảm ơn với vòng tròn chấm xoắn ốc trong suốt (bg-background):
\begin{hustbackgroundframe}
  \centering
  \vspace*{0.25\paperheight}
  {\Huge\bfseries\color{hustmain} XIN TRÂN TRỌNG CẢM ƠN!\par}
  \vspace{1.5em}
  {\large\color{hustblack!80} HUST Beamer Theme\par}
\end{hustbackgroundframe}
```

### 6.4. Trang Chuyển Mục Thủ Công (`\hustPanelFrame`)

Nếu bạn đặt `sectionpage=none` nhưng muốn chèn một slide chuyển mục tại một vị trí cụ thể:

```latex
\section{Phương Pháp Nghiên Cứu}
\hustPanelFrame
```

### 6.5. Khối Hộp Thông Tin (Blocks)

Theme đã được thiết kế sẵn 3 khối hộp tiêu chuẩn với góc bo tròn mềm mại và màu sắc nhận diện phân biệt rõ ràng giữa các phiên bản màu:

- **Phiên bản Xanh (`color=blue`)**:
  - `\begin{block}{Khối Tiêu Chuẩn}`: Màu xanh lam đậm (`hustmain` / `#003366`).
  - `\begin{alertblock}{Khối Cảnh Báo}`: Màu đỏ cờ thương hiệu HUST (`hustalert` / `#CE1628`).
  - `\begin{exampleblock}{Khối Ví Dụ}`: Màu cam nhận diện thương hiệu (`hustorange` / `#F57F20`), giúp phân biệt hoàn toàn với màu xanh tiêu chuẩn.

- **Phiên bản Đỏ (`color=red`)**:
  - `\begin{block}{Khối Tiêu Chuẩn}`: Màu đỏ thương hiệu HUST (`hustmain` / `#C02034`).
  - `\begin{alertblock}{Khối Cảnh Báo}`: Màu xanh lam đậm nhận diện HUST (`hustalert` / `#003366`).
  - `\begin{exampleblock}{Khối Ví Dụ}`: Màu cam nhận diện thương hiệu (`hustorange` / `#F57F20`).

### 6.6. Trích Dẫn Chân Trang, Chú Thích `\note` & Thanh Footer Động (Dynamic Footer Bar)

Theme hỗ trợ tích hợp sâu giữa trích dẫn học thuật **BibLaTeX / Biber** (`\cite{key}`) và lệnh chú thích ký tự **`\note{<từ>}{<nội dung chú thích>}`**:

1. **Lệnh chú thích `\note{<từ>}{<nội dung>}` (Phân biệt màu với `\cite`)**:
   - Hiển thị `<từ>` trong thân slide với ký hiệu chữ cái in thường đặt trên cao dạng superscript ($^{a}, ^{b}, ^{c}...$), ví dụ: `\note{phép toán hai ngôi}{Một ánh xạ từ $X^2 \to X$}` $\to$ `phép toán hai ngôi`$^{a}$.
   - **Phân biệt màu sắc trực quan với `\cite`**:
     - Trích dẫn `\cite{...}` ($^{1}, ^{2}...$) sử dụng màu chủ đạo **`hustmain`** (Xanh lam trên bản Xanh, Đỏ trên bản Đỏ).
     - Chú thích `\note{...}{...}` ($^{a}, ^{b}...$) sử dụng màu nhấn **`hustaccent`** (**Đỏ** trên bản Xanh, **Vàng hổ phách** trên bản Đỏ) ở cả chỉ số mũ trong văn bản lẫn nhãn trong hộp chân trang, giúp người xem phân biệt tức thì giữa tài liệu tham khảo và chú thích giải nghĩa.
   - Tự động kết xuất dòng chú thích `a Nội dung chú thích` vào hộp chân trang theo đúng định dạng superscript (bỏ dấu gạch ngang `-`), đồng bộ vị trí với trích dẫn `\cite{...}`.
   - Tự động reset bộ đếm `hustnotecnt` theo từng slide.
   - Khi sử dụng bảng biểu `tabularx` (có cơ chế tính toán độ rộng nhiều lượt làm rơi hộp chân trang), khuyến nghị đặt trích dẫn hoặc `\note` ở dòng giới thiệu trước bảng để bảo đảm tài liệu tham khảo luôn xuất hiện đầy đủ ở footer.

2. **Cơ chế thanh footer động thích ứng & Khóa cứng tối đa 4 dòng (4-Line Max Lock)**:
   - **Loại bỏ từ khóa `"In:"` dư thừa**: Trích dẫn ở cả chân trang và danh mục tài liệu tham khảo cuối bài đều loại bỏ hoàn toàn chữ `"In:"`, chỉ hiển thị sạch sẽ theo chuẩn: `Tác giả. "Tên bài báo". Tên tạp chí Tập (Năm).`
   - **Tự động rút gọn tác giả & tiêu đề thông minh (`...`)**:
     - Các bài báo có từ 2 tác giả trở lên (ví dụ 5–6 tác giả) tự động rút gọn ở chân trang thành `Tác giả đầu et al.` (trong khi trang Danh mục tài liệu tham khảo cuối bài vẫn hiển thị đầy đủ toàn bộ tác giả).
     - Tên bài báo và tên tạp chí dài được tự động cắt gọn theo ranh giới từ tiếng Việt/tiếng Anh Unicode kèm dấu `...` sao cho **mỗi mục trích dẫn luôn nằm gọn trên đúng 1 dòng duy nhất**.
   - **Khóa cứng hộp chân trang tối đa 4 dòng (`citemaxlines=4`) & Tự động tách 2 cột (`citecolumns=auto`)**:
     - **Chỉ có 1 mục (1 trích dẫn hoặc 1 note)**: Thanh viền footer giữ nguyên vị trí chuẩn (`footY`). Mục duy nhất được đặt gọn gàng **ngay dưới thanh footer**, nằm ngang hàng với logo chân trang và số trang bên phải mà không đẩy lùi bố cục slide.
     - **Từ 2 đến 4 mục**: Hiển thị dạng 1 cột (từ 2 đến 4 dòng đơn), toàn bộ hộp chú thích kéo sát xuống cạnh đáy (`numY`) và thanh viền footer tự động nâng lên ngay phía trên hộp chú thích.
     - **Từ 5 đến 8 mục trên cùng một slide**: Hộp chân trang **tự động chia thành 2 cột cân đối** (mỗi cột tối đa 4 dòng, định dạng siêu gọn `Tác giả et al. "Tên rút gọn..." (Năm).`), giúp hiển thị tới **8 trích dẫn/chú thích mà tổng chiều cao không bao giờ vượt quá 4 dòng**.
     - Tự động căn lề thụt vào bên phải logo chân trang (`footerlogo=mark/hust/full`), không bao giờ bị đè lên logo hay số trang bên phải.
     - Tự động tái sử dụng chỉ số trích dẫn nếu cùng một tài liệu được trích dẫn nhiều lần trên cùng một slide.

### 6.7. Bố Cục Chèn Hình Ảnh & Bọc Văn Bản (`wrapfig` trên Beamer)

Gói `wrapfig` được tích hợp sẵn trong `hust-setup.tex`, cho phép bọc văn bản xung quanh logo hoặc hình ảnh với số dòng cố định trên slide:

```latex
\begin{wrapfigure}[6]{r}{0.16\textwidth}
  \vspace{-1.2em}
  \centering
  \includegraphics[width=0.13\textwidth]{assets/hust-shield.png}
\end{wrapfigure}
Đoạn văn bản thuyết minh bọc xung quanh hình ảnh...
```
- Tùy chọn `[6]`: Quy định chính xác số dòng văn bản bọc quanh hình (ví dụ 6 dòng) trước khi trở về toàn độ rộng lề.
- `r` / `l`: Canh phải (`r`) hoặc canh trái (`l`).
- Khuyến nghị thu nhỏ khoảng cách đỉnh bằng `\vspace{-1.2em}` để hình ngang hàng với dòng văn bản đầu tiên.

### 6.8. Danh Mục Toàn Bộ Tài Liệu Cuối Bài & Tự Động Ẩn Progress Bar

- **Tiêu đề & phụ đề**:
  - Tiêu đề mặc định: `Tài liệu tham khảo`.
  - Phụ đề mặc định: Ẩn (`Hidden`). Khi không có phụ đề, tiêu đề tự động được căn giữa theo chiều dọc trong dải màu phía trên.
  - Tùy biến tiêu đề/phụ đề qua lệnh thiết lập:
    ```latex
    \hustsetup{reftitle={References}, refsubtitle={Overview main points}}
    ```
- **Tự động tắt thanh tiến trình**:
  - Tương tự như trang mục lục toàn cục (*Nội dung chính*), môi trường `hustreferencesframe` tự động kích hoạt `[noprogressbar]`, đẩy dải header band lên sát mép trên cùng và căn giữa tiêu đề theo chiều đứng.
- **Hiển thị và phân trang thủ công**:
  ```latex
  %% Hiển thị toàn bộ trong 1 slide:
  \begin{hustreferencesframe}
  \end{hustreferencesframe}

  %% Hoặc chia thành 2, 3, 4... slide thủ công (giữ nguyên tiêu đề "Tài liệu tham khảo", không sinh số La Mã I, II...):
  \begin{hustreferencesframe}[from=1, to=2]
  \end{hustreferencesframe}

  \begin{hustreferencesframe}[from=3, to=4]
  \end{hustreferencesframe}
  ```
  hoặc lệnh tắt:
  ```latex
  \hustprintreferences[from=1, to=2]
  ```
- Không gắn số trang trích dẫn ở cuối mục theo yêu cầu hiển thị học thuật sạch sẽ.

### 6.9. Mục Lục Toàn Cục & Tách 2 Cột (`\tableofcontents[split=N]`)

Mục lục toàn cục được thiết kế hiện đại theo chuẩn nhận diện HUST:
- **Tiêu đề & phụ đề**:
  - Tiêu đề mặc định: `Nội dung chính`.
  - Phụ đề mặc định: Ẩn (`Hidden`), tự động căn giữa theo chiều dọc trong dải màu.
  - Tùy biến qua `\hustsetup{toctitle={Table of Contents}, tocsubtitle={Overview}}` hoặc truyền trực tiếp vào `\begin{frame}{Table of Contents}{Overview}`.
- Đánh số đề mục dạng huy hiệu vuông màu chủ đạo (`hustmain`) với số màu trắng nổi bật, căn chỉnh tâm số hộp đồng trục với văn bản mục lục.
- **Tự động ẩn progress bar**: Thanh tiến trình được tắt hoàn toàn trên trang mục lục toàn cục.
- **Hỗ trợ tùy chọn `split=N`**: Tự động chia mục lục thành **2 cột song song cân đối**: Cột 1 gồm các section từ $1$ đến $N-1$, cột 2 gồm các section từ $N$ trở đi:
  ```latex
  \begin{frame}[noprogressbar]{\husttoctitle}{\husttocsubtitle}
    \tableofcontents[split=3,hideallsubsections]
  \end{frame}
  ```

### 6.10. Trang Chuyển Mục (Section Panel) & Màu Sắc Phụ Đề

Khi bật `sectionpage=panel`, mỗi khi bắt đầu một `\section`, theme tự động tạo một slide chuyển mục:
- Huy hiệu số mục lấy chuẩn từ mục lục toàn cục (`[1]`, `[2]`, ...).
- **Màu sắc đề mục con (subsections)**: Hiển thị bằng màu chuẩn **`HUSTBlack`** (`hustblack!80`) với dấu đầu dòng hình vuông nhỏ màu xám nhận diện `hustgrayline!80`, đảm bảo độ sắc nét cao nhất trên nền trắng.
- **Màu sắc phụ đề các slide (framesubtitle)**: Sử dụng màu vàng **`hustsubyellow`** (`#FFDE59`) được tinh chỉnh độ sáng tối ưu, đạt chuẩn tương phản cao trên cả nền xanh dương đậm (`#003366`, tương phản 11.5:1) và nền đỏ HUST (`#C02034`, tương phản 4.6:1).
- **Tùy chọn ẩn panel cho section cụ thể**: Nếu bạn không muốn hiển thị slide panel cho một phần nào đó (ví dụ phần Tùy biến hoặc phần Phụ lục):
  ```latex
  \hustsection[panel=false]{Tùy biến & linh hoạt}
  ```

### 6.11. Thanh Tiến Trình Thông Minh (`progressbar=on`)

Khi bật `progressbar=on` trong `\usetheme` hoặc `\hustsetup{progressbar=on}`:
- **Bố cục các ô chữ nhật**: Toàn bộ chiều rộng màn hình được chia thành các ô chữ nhật đều nhau tương ứng với số lượng `\section` trong bài trình chiếu.
- **Tên rút gọn / Alias cho Section trên Thanh Tiến Trình (`\section[alias]{full}`)**:
  - Khi bài trình chiếu có nhiều section hoặc tên section dài, các ô trên thanh tiến trình có chiều rộng thu hẹp lại.
  - Tương tự như cơ chế `\author[tên ngắn]{tên đầy đủ}` (dùng tên ngắn ở chân trang và tên đầy đủ ở trang bìa), người dùng có thể truyền tên rút gọn (alias) qua đối số tùy chọn `[...]`:
    ```latex
    \section[Quy chuẩn]{Giới thiệu \& quy chuẩn}
    \section[Giải thuật]{Các khối nội dung \& giải thuật}
    ```
    - **Mặc định**: Nếu không truyền `[...]` (ví dụ `\section{Nội dung chính}`), thanh tiến trình sẽ in toàn bộ tên section đầy đủ.
    - **Khi truyền `[...]`**: Tên alias trong `[...]` sẽ được in trên thanh tiến trình, trong khi trang chuyển mục (`section panel`) và mục lục (`\tableofcontents`) vẫn hiển thị đầy đủ tên dài nguyên bản.
  - **Hỗ trợ cú pháp `\hustsection[alias=...]` (hoặc `short=...`)**: Người dùng cũng có thể thiết lập alias qua key-value ngay trước `\section`:
    ```latex
    \hustsection[panel=false, alias=Tùy biến]
    \section{Tùy biến \& linh hoạt}
    ```
- **Tự động cắt ngắn bằng dấu ba chấm (`...`) theo độ rộng ô (Width-based Auto-truncation)**:
  - Nếu tên section hoặc alias dài hơn chiều rộng của ô chữ nhật trừ đi khoảng đệm an toàn hai bên (`\hust@sec@w - 4.5pt`), theme tự động đo đạc độ rộng phông chữ thực tế và cắt ngắn bằng dấu ba chấm `...` (ví dụ: `Trích dẫn tài liệu tham khảo khoa học...`).
  - Bảo đảm chữ trong ô thanh tiến trình **luôn nằm trên đúng 1 dòng duy nhất**, tuyệt đối không bị ngắt dòng làm tràn chiều cao thanh tiến trình hay đè lên các vạch tiến trình subsection bên dưới.
- **Màu sắc phần hiện tại**: Section đang trình chiếu có nền màu chủ đạo của slide (`hustmain`: xanh hoặc đỏ) và chữ trắng; các section khác có nền sáng với chữ màu `HUSTBlack`.
- **Vạch phân cách**: Giữa các ô chữ nhật có đường viền đứng mảnh tinh tế (`line width=0.4pt`).
- **Đếm đề mục con (Subsection bars)**:
  - Chỉ đếm các `\subsection` được gọi tường minh bằng lệnh, không tính theo frame hay frametitle.
  - Hiển thị dưới dạng các vạch chạy ngang chia đều ở đáy ô section tương ứng (hỗ trợ hiển thị ngay cả khi section chỉ có 1 `\subsection`).
  - **Màu sắc đề mục con**:
    - **Phiên bản Đỏ (Red variant)**:
      - Section khác (không phải section hiện tại): **`HUSTGray`** (`#A6A6A6`).
      - Trong section hiện tại, nhưng không thuộc subsection này: **`HUSTLightRed`** (`#F05C5D`).
      - Thuộc đúng subsection hiện tại: **`HUSTYellow`** (`#F3C108`).
    - **Phiên bản Xanh (Blue variant)**:
      - Section khác: **`HUSTGray`** (`#A6A6A6`).
      - Trong section hiện tại, nhưng không thuộc subsection này: **`HUSTLightBlue`** (`#5B9BD5`).
      - Thuộc đúng subsection hiện tại: **`HUSTYellow`** (`#F3C108`) (sử dụng sắc vàng nổi bật tương tự phiên bản đỏ).
    - **Khi slide nằm ngoài mọi subsection (`\c@subsection = 0`)**: Tất cả các vạch của section hiện tại tự động mang màu "trong section nhưng chưa vào subsection" (`HUSTLightRed` / `HUSTLightBlue`).
- **Tự động tắt trên trang mục lục và tài liệu tham khảo**: Thanh tiến trình tự động ẩn trên slide mục lục và slide tài liệu tham khảo.
- **Tùy chọn tắt thủ công trên từng frame (`[noprogressbar]`)**: Dùng cho các slide đồ thị toàn màn hình hoặc trang phụ lục đặc biệt:
  ```latex
  \begin{frame}[noprogressbar]{Tiêu Đề Slide}{Phụ đề nếu có}
    Nội dung slide không hiển thị thanh tiến trình...
  \end{frame}
  ```
- **Điều hướng siêu liên kết toàn diện (Full-surface Clickable Navigation)**:
  - **Click vào ô section (kể cả vùng trống ngoài chữ tiêu đề)**: Tự động chuyển tới slide panel của section đó (hoặc slide đầu tiên của section nếu panel đang tắt).
  - **Click vào từng vạch subsection bar**: Tự động chuyển trực tiếp đến slide đầu tiên trực thuộc subsection tương ứng.
- **Tự động đẩy dải tiêu đề xuống (Push-down)**: Khi bật `progressbar=on`, toàn bộ dải header band, vạch màu phụ, frametitle, framesubtitle và thân nội dung slide tự động dịch xuống một khoảng bằng chiều cao thanh tiến trình (`\hust@prog@h`), bảo đảm không bị đè chữ hay tràn lề.

### 6.12. Căn Chỉnh Tiêu Đề Và Phụ Đề Slide (Frametitle & Subtitle) & Thanh Header Dày (`bar=thick`)

- **Tự động cắt ngắn tiêu đề slide (`.title bar`) bằng dấu ba chấm (`...`) khi vượt quá khung viền**:
  - Khi tiêu đề slide (`\insertframetitle`) quá dài so với chiều rộng khả dụng của dải màu tiêu đề (`\hust@title@avail@w`, đã trừ khoảng đệm lề trái và hộp số trang/logo góc phải nếu có), theme sẽ tự động đo lường kích thước phông thực tế và cắt ngắn bằng dấu `...` (ví dụ: `Biểu diễn giải thuật tối ưu hóa đa mục tiêu với algorithm2e, listings và minted trong...`).
  - Giúp dải tiêu đề luôn duy trì bố cục chuẩn 1 dòng, không bị tràn ra ngoài khung chữ nhật hay va chạm với logo/số trang ở góc phải.

- **In đậm đồng bộ (Bold Typography)**: Cả `frametitle` và `framesubtitle` đều được thiết lập in đậm (`\bfseries`) bằng phông tiêu đề đồng bộ, giúp nâng cao độ sắc nét và khả năng nhận diện khi trình chiếu từ xa.
- **Tự động co hẹp khoảng cách từ (Word-spacing Optimization)**: Phụ đề `framesubtitle` được tinh chỉnh khoảng cách từ tự động (`\spaceskip=0.8\fontdimen2\font`), khắc phục hoàn toàn hiện tượng giãn từ quá rộng của một số phông chữ không chân.
- **Tùy chọn thanh nhấn dày (`bar=thick`)**:
  - Khi kích hoạt `bar=thick` (như trong `test_deck.tex`), thanh nhấn phụ bên dưới dải tiêu đề được mở rộng thành một dải màu phụ dày theo đúng quy chuẩn bài giảng PPT gốc của ĐHBK Hà Nội.
  - Khi slide có phụ đề `framesubtitle`, khối phụ đề sẽ **tự động chuyển xuống nằm trọn bên trong thanh nhấn dày** này với chữ màu trắng tinh (`HUSTWhite`), trong khi tiêu đề chính `frametitle` được căn giữa tuyệt đối trong dải màu chính phía trên.
- **Tùy chọn thanh mảnh (`bar=thin`) & Căn chỉnh đệm đối xứng chuẩn**:
  - Khi chọn `bar=thin` (như trong `test_variants.tex`), thanh nhấn bên dưới là một đường kẻ mảnh tinh tế.
  - Cả tiêu đề chính và phụ đề đều nằm chung bên trong dải màu chính, phụ đề mang màu vàng `hustsubyellow`.
  - **Khoảng cách đệm đối xứng hoàn hảo (Symmetric Vertical Padding)**: Khắc phục hoàn toàn hiện tượng chữ in hoa hoặc có dấu tiếng Việt (ví dụ: `Bảng dữ liệu...`, `Biểu diễn giải thuật...`) bị dính sát mép trên hoặc tràn sát vạch kẻ dưới. Theme áp dụng chiều cao dải chuyên dụng `bandThinB` (`10.80%` chiều cao khung hình trên `16:9`, `11.00%` trên `4:3`), kết hợp neo đỉnh `anchor=north west` tại tọa độ chuẩn `yshift=-\dimexpr\hust@cur@progh + 3.8pt\relax`. Kết quả đo lường pixel cho thấy khoảng cách từ đỉnh chữ đến thanh tiến trình và từ chân chữ đến vạch kẻ dưới đều đạt chính xác **6px đối xứng**, mang lại vẻ đẹp cân đối và đồng nhất trên mọi slide và tỉ lệ màn hình.
- **Căn giữa dải màu khi không có phụ đề**: Khi `framesubtitle` không có hoặc được thiết lập là `Hidden` / `hidden` / `none` (chẳng hạn ở slide mục lục *Nội dung chính* và *Tài liệu tham khảo*), tiêu đề chính `frametitle` được căn giữa tuyệt đối theo chiều đứng của dải màu header band.

### 6.13. Hệ Thống Khối Nội Dung & Môi Trường Toán Học Chuẩn Beamer

Theme HUST tích hợp và tùy biến toàn diện hệ thống khối nội dung (`blocks`) cùng các môi trường toán học chuẩn của Beamer, tự động đồng bộ theo hệ màu nhận diện thương hiệu:

1. **Các khối nội dung chuẩn Beamer (`blocks`)**:
   - `\begin{block}{Tiêu đề}`: Khối nội dung tiêu chuẩn mang màu chủ đạo `hustmain` (Xanh lam đậm trên bản Blue, Đỏ cờ trên bản Red). Nền thân hộp có sắc độ nhạt đồng bộ `hustmain!7`.
   - `\begin{alertblock}{Cảnh báo / Điểm then chốt}`: Khối cảnh báo hoặc nhấn mạnh đặc biệt với dải màu đỏ/xanh hoán đổi `hustalert` (Đỏ trên Blue, Xanh trên Red) và nền nhạt `hustalert!8`.
   - `\begin{exampleblock}{Ví dụ minh họa}`: Khối ví dụ, mã nguồn hoặc kết quả thực nghiệm với màu cam nhận diện `HUSTOrange` / `hustexample` (nền `hustexample!8`).

2. **Môi trường toán học chuẩn hóa tiếng Việt (`theorems`)**:
   - Được thiết lập đánh số tự động (`\setbeamertemplate{theorems}[numbered]`) và Việt hóa hoàn toàn qua gói `translator`:
     - `\begin{definition}[Tên khái niệm]`: Khối định nghĩa với tiêu đề **Định nghĩa <số> (<tên>)** trong màu `hustmain`.
     - `\begin{theorem}[Tên định lý]`: Khối định lý với tiêu đề **Định lý <số> (<tên>)** nổi bật.
     - `\begin{lemma}[Tên bổ đề]`: Khối bổ đề với tiêu đề **Bổ đề <số> (<tên>)**.
     - `\begin{corollary}[Tên hệ quả]`: Khối hệ quả với tiêu đề **Hệ quả <số> (<tên>)**.
     - `\begin{example}[Tên ví dụ]`: Khối ví dụ với tiêu đề **Ví dụ <số> (<tên>)** trong tông màu cam `hustexample`.
     - `\begin{proof}`: Môi trường chứng minh với tiêu đề **Chứng minh.** và tự động đặt ký hiệu kết thúc $\square$ ở cuối dòng.

3. **Tham chiếu chéo tự động với `cleveref`**:
   - Tích hợp liền mạch với `cleveref`: khi gán nhãn `\label{thm:pareto}` và gọi `\cref{thm:pareto}`, hệ thống tự động sinh tiền tố tiếng Việt chuẩn xác kèm liên kết màu thương hiệu (`định lý 1`, `định nghĩa 2`, `bổ đề 3`, `ví dụ 1`).

4. **Quy chuẩn bất biến logo Khoa Toán - Tin (FaMI)**:
   - Logo huy hiệu khiên tròn FaMI được **khóa cứng tuyệt đối** ở màu nhận diện chính thức **`famiblue`** (`#0062A5`). Tuyệt đối không tự ý chuyển logo sang màu vàng hay màu khác trên bất kỳ biến thể slide nào.

### 6.14. Tùy Biến Danh Sách Với `enumitem` & `tasks`

1. **Danh sách số ô vuông HUST (`hustsqlist`)**:
   - Tái hiện chính xác phong cách đánh số định nghĩa với huy hiệu số vuông màu thương hiệu (`hustmain` hoặc đỏ) và chữ số trắng in đậm:
   ```latex
   \begin{hustsqlist}
     \item $x^* \in C$ là \emph{nghiệm Pareto} nếu... \label{def:pareto}
     \item $\bar{x} \in C$ là \emph{nghiệm Pareto yếu}...
     \item Tập hợp tất cả các nghiệm Pareto...
   \end{hustsqlist}
   ```
   - Hỗ trợ gán nhãn `\label` và tham chiếu chéo bằng `\cref` an toàn mà không bị lỗi đệ quy mở rộng macro trong Beamer.

2. **Môi trường `tasks` mặc định & tùy biến huy hiệu ô vuông**:
   - **Mặc định**: Môi trường `tasks` kế thừa trọn vẹn dấu đầu dòng hình vuông đặc trưng màu xanh/đỏ (`hustmain`) của Beamer `itemize`:
     ```latex
     \begin{tasks}(2)
       \task Phương pháp gradient gần kề\cite{bellocruz2025}
       \task Thuật toán quán tính Hilbert\cite{alvarez2024}
       \task Chuẩn hóa nhận diện ĐHBK Hà Nội\cite{hust2026}
       \task Chiếu gradient đa mục tiêu
     \end{tasks}
     ```
   - **Tùy biến huy hiệu chữ cái ô vuông `[a]`, `[b]`, `[c]`, `[d]`**: Khi cần phân loại dạng bài tập hoặc danh mục trắc nghiệm, có thể kích hoạt huy hiệu chữ cái vuông thông qua tùy chọn linh hoạt:
     ```latex
     \begin{tasks}[label=\hustitemsq{\alph*}, label-width=1.5em, item-indent=1.9em, label-format={\bfseries\color{white}}](2)
       \task Bài toán lồi đa mục tiêu
       \task Bài toán không lồi với gradient
       \task Điều kiện tối ưu Karush-Kuhn-Tucker
       \task Thuật toán chiếu điểm gần kề
     \end{tasks}
     ```

3. **Phân cấp danh sách lồng nhau (Itemize & Enumerate Cấp 1, 2, 3)**:
   - **`itemize` (Danh sách không đánh số)**:
     - Cấp 1: Ô vuông lớn 0.8ex đặc trưng màu `hustmain`.
     - Cấp 2: Ô vuông nhỏ 0.6ex màu nhấn `hustaccent`.
     - Cấp 3: Dấu chấm tròn `\bullet` màu `hustaccent` (tự động kế thừa định dạng Beamer).
   - **`enumerate` (Danh sách có đánh số)**:
     - Cấp 1: Số Ả Rập `1.`, `2.`, ...
     - Cấp 2: Chữ cái thường `a.`, `b.`, ...
     - Cấp 3: Chữ số La Mã `i)`, `ii)`, `iii)` (tự động tăng đúng chỉ số).
   > [!IMPORTANT]
   > Trong LaTeX với gói `enumitem`, môi trường `itemize` là danh sách không đánh số (bullet list) và không có bộ đếm nội tại. Do đó, nếu truyền `[label=\roman*)]` vào `\begin{itemize}`, LaTeX sẽ không thể tăng số đếm (dẫn đến hiển thị lặp `iii)` trên mọi mục). Khi cần danh sách đánh số La Mã tăng dần, hãy sử dụng `\begin{enumerate}[label=\roman*)]` (hoặc `\begin{enumerate}` lồng ở cấp 3).

### 6.15. Toán Học Chuyên Sâu, Vi Phân, Tích Phân Đường Kín & TikZ

`hust-setup.tex` tích hợp đầy đủ hệ thống ký hiệu toán học nâng cao:
- **Ký hiệu vector & ma trận**: `\bm{w} \in \mathbb{C}^n` (tự động tương thích cả `unicode-math` lẫn `bm`), `\vv{AB}`, `\vs{v}`.
- **Đạo hàm khoa học (`derivative`)**: Đạo hàm thường `\odv{f}{z}`, đạo hàm riêng `\pdv{u}{x} = \pdv{v}{y}`.
- **Tích phân đường cong kín & mặt kín**: Tích phân Cauchy ngược chiều kim đồng hồ `\ointctrclockwise_{C} \frac{f(z)}{z - z_0}\,\mathrm{d}z = 2\pi i f(z_0)`, tích phân mặt kín `\oiint_{\mathcal{S}} \bm{F}\cdot\mathrm{d}\bm{S}`.
- **Dấu ngoặc co giãn thông minh (Paired Delimiters)**:
  - Chuẩn: `\norm{z}` hoặc `\norm*{z}`
  - Trị tuyệt đối: `\abs{z}`
  - Tích vô hướng: `\innerp{u}{v}`
  - Phần làm tròn: `\ceil{x}`, `\floor{x}`
- **Toán tử tối ưu**: `\argmin_{d}`, `\argmax_{x}`, `\Real`, `\Image`.
- **Biểu đồ hình học TikZ**: Tích hợp mũi tên `Stealth`, bộ trang trí mũi tên dọc đường cong `decorations.markings` cho mặt phẳng phức và quỹ đạo tối ưu.

### 6.16. Động Cơ Chú Thích Vạn Năng & Tham Chiếu Chéo (`\hustcaption`, `cleveref`, `\cref`, `\eqref`, `\href`)

Theme cung cấp giải pháp chú thích và tham chiếu chéo toàn diện, đồng bộ màu sắc nhận diện thương hiệu `hustmain` cho toàn bộ các siêu liên kết (`\cref`, `\eqref`, `\href`), khắc phục triệt để các hạn chế của môi trường Beamer:

1. **Động cơ chú thích vạn năng `\hustcaption[<tên>][<số>]{<caption>}\label{...}`**:
   - Sử dụng cho **mọi đối tượng khoa học** trong bài thuyết trình: hình vẽ TikZ, bảng biểu `tabularx`, mã nguồn `listings`, mã `minted`, thuật toán mã giả `algorithm2e`, hình ảnh `wrapfigure`... mà không phụ thuộc vào môi trường trôi nổi `figure`/`table`.
   - **Tùy biến tên gọi linh hoạt (Custom Prefix Name)**:
     - Tự do truyền tên tiếng Việt hoặc tiếng Anh: `\hustcaption[Hình]{...}`, `\hustcaption[Bảng]{...}`, `\hustcaption[Figure]{...}`, `\hustcaption[Table]{...}`, `\hustcaption[Image]{...}`, `\hustcaption[Listing]{...}`, `\hustcaption[Thuật toán]{...}`.
     - Khi không truyền tham số `[<tên>]`, mặc định sử dụng `\hustfigurename` ("Hình").
   - **Linh hoạt giữa Đánh số tự động (Auto-increment) và Đánh số thủ công (Manual Numbering)**:
     - **Tự động tăng số**: Khi không truyền `[<số>]` (ví dụ `\hustcaption[Hình]{Miền giải tích C}\label{fig:cauchy}`), bộ đếm sẽ tự động tăng dần: `Hình 1`, `Hình 2`...
     - **Đánh số thủ công tùy biến**: Khi cần đánh số theo chương hoặc số thứ tự bài báo (ví dụ `\hustcaption[Bảng][2.5]{So sánh hiệu năng}\label{tab:exp}` hoặc `\hustcaption[Hình][6]{Sơ đồ khối}\label{fig:block}`), hệ thống sẽ hiển thị chính xác con số bạn chỉ định (`Bảng 2.5`, `Hình 6`).
   - **Tích hợp Cleveref (`\cref` / `\Cref`) nhấp được 100%**:
     - Gán nhãn `\label{key}` ngay sau `\hustcaption`.
     - Khi gọi `\cref{key}` hoặc `\Cref{key}`, LaTeX tự động kết xuất cả cụm tên và số chuẩn xác (ví dụ: **Hình 1**, **Bảng 2.5**, **Listing 1**) thành một khối liên kết siêu văn bản duy nhất mang màu sắc nhận diện `hustmain`, nhấp chuột nhảy ngay đến slide đích:
       ```latex
       %% Định nghĩa hình vẽ TikZ kèm chú thích tự động:
       \begin{tikzpicture}...\end{tikzpicture}
       \hustcaption[Hình]{Miền giải tích liên thông $C$}\label{fig:cauchy}

       %% Định nghĩa bảng dữ liệu kèm số thủ công:
       \begin{tabularx}{\textwidth}{...}...\end{tabularx}
       \hustcaption[Bảng][2.5]{So sánh hiệu năng thực nghiệm}\label{tab:exp}

       %% Đoạn mã nguồn:
       \hustcaption[Listing][1]{Cài đặt hàm mục tiêu bằng Python}\label{lst:python}

       %% Tham chiếu chéo trong văn bản:
       Như quan sát trên \cref{fig:cauchy}, kết quả tại \cref{tab:exp} và mã nguồn \cref{lst:python}...
       ```
   - **Lệnh thay đổi tên mặc định toàn cục**:
     ```latex
     \hustsetfigurename{Figure}   % Đổi tên hình sang tiếng Anh
     \hustsettablename{Table}     % Đổi tên bảng sang tiếng Anh
     ```

2. **Khai thác `\captionof` truyền thống & Thứ tự nạp gói an toàn**:
   - `cleveref` được nạp trước `listings` trong `hust-setup.tex` để tránh xung đột lặp vô hạn với bộ phân tích verbatim `.vrb` của Beamer.
   - Bạn vẫn có thể dùng `\captionof{figure}{...}\label{...}` hoặc `\captionof{table}{...}\label{...}` theo thói quen cũ.

3. **Hệ thống liên kết nhấp được 100% trong Beamer**:
   - `\Cref{eq:mop}` $\to$ **Phương trình 2**: Nhấp chuột nhảy ngay đến công thức tối ưu hóa đa mục tiêu.
   - `\eqref{eq:cauchy}` $\to$ **(1)**: Định nghĩa lại thông qua `\hyperref[#1]{...}` giúp biểu thức toán học trở thành liên kết tương tác nhấp được trong Beamer.
   - `\cref{def:pareto}` $\to$ **mục 1**: Nhảy trực tiếp đến điều kiện nghiệm Pareto trong danh sách `hustsqlist`.
   - `\cref{fig:cauchy}`, `\cref{tab:exp}`, `\cref{lst:python}`: Nhảy chính xác đến từng hình ảnh, bảng dữ liệu, thuật toán và đoạn mã.
   - `\href{https://hust.edu.vn}{\underline{Trang chủ ĐHBK Hà Nội}}`: Liên kết ngoài trực tiếp mang màu `hustmain` (xanh trên Blue, đỏ trên Red).

### 6.17. Bảng Dữ Liệu Khoa Học & Trình Bày Giải Thuật

1. **Bảng khoa học (`tabularx` + `booktabs` + `multirow`)**:
   - Kẻ bảng chuẩn quốc tế với `\toprule`, `\midrule`, `\bottomrule`.
   - Cột co giãn linh hoạt `X`, căn giữa dọc theo chiều cao ô `\tabularxcolumn{m{#1}}`.
   - Nổi bật dòng phương pháp đề xuất với `\rowcolor{hustmain!10}`.

2. **Cấu trúc thuật toán (`algorithm2e`)**:
   - Đánh số dòng tự động, đóng khung và kẻ chỉ số vòng lặp `[linesnumbered,ruled,vlined]`.
   - **Căn lề số dòng chuẩn trong khối (`\IncMargin{1.2em}`)**: Số thứ tự dòng (`1, 2, 3...`) được thụt vào nằm gọn bên trong đường kẻ ngang của khối thuật toán, không bị tràn ra ngoài lề trái.
   - Đầu vào/đầu ra rõ ràng qua `\KwIn{...}`, `\KwOut{...}`, vòng lặp `\For{...}{...}`, rẽ nhánh `\If{...}{...}`.

3. **Khối mã nguồn (`listings` & `minted`)**:
   - **Với `listings` (phong cách `hustcode`)**:
     - Tô màu cú pháp Python/C++/MATLAB với số dòng nằm gọn **bên trong** khung viền (`xleftmargin=1.6em, framexleftmargin=1.4em`).
     - **Nền mờ biến đổi theo theme (`hustcodebg = hustmain!5!white`)**: Trên bản Xanh sử dụng nền xanh phấn nhạt, trên bản Đỏ tự động chuyển sang nền ửng hồng phấn nhạt.
   - **Với `minted` (tô màu cú pháp nâng cao qua Pygments)**:
     - Tự động bọc trong hộp `hustmintedbox` đồng bộ màu nền `hustmain!5!white`, viền `hustmain!30` và giữ số thứ tự dòng nằm trọn bên trong khung viền.
     - Hỗ trợ gán nhãn và tham chiếu chéo qua `\captionof{listing}{...}\label{lst:cpp}` và `\cref{lst:cpp}`.
     - **Lưu ý cài đặt khi dùng `minted`**: Cần cài đặt **Python** (kèm gói `pygments` / `latexminted`) và bật cờ **`-shell-escape`** cho trình biên dịch (`lualatex -shell-escape`).

### 6.18. Module Cấu Hình Mở Rộng `hust-setup.tex`

Toàn bộ các gói thư viện mở rộng, định nghĩa hộp, danh sách, toán học và tham chiếu chéo được đóng gói độc lập trong file **`hust-setup.tex`**. Nhờ đó:
- File trình chiếu chính (`presentation.tex`) luôn sạch sẽ và tinh gọn tối đa:
  ```latex
  \documentclass[aspectratio=169,10pt]{beamer}
  \usetheme[color=blue, font=lato]{HUST}
  \input{hust-setup}
  \begin{document}
    ...
  \end{document}
  ```
- Dễ dàng bảo trì, chia sẻ giữa các đồ án, bài giảng hoặc luận văn mà không làm xáo trộn nhân theme `HUST`.

### 6.19. Tùy Chọn Nền Trang Bìa (`cover` / `light` / `solid` / `dark`), Màu Sắc & Định Dạng Ngày Tháng (`\today` & `\hustdate`)

- **4 chế độ nền Trang Bìa (Title Page Background Modes) cho mọi tỉ lệ (`16:9` & `4:3`)**:
  - **`titlepage=cover` (hoặc `coverbg=cover`, mặc định cho `16:9`)**: Nền trắng chính thức kèm vòng chấm tròn đậm nguyên bản bên phải (`bg-cover-*`).
  - **`titlepage=light` (hoặc `coverbg=light`, khuyến nghị cho tỉ lệ hẹp `4:3`)**: Áp dụng lớp phủ làm sáng `+20%` lightness / `40%` tint lên vòng chấm tròn (tương tự sắc độ chấm trên nền tối), giúp vùng chấm trở thành hoa văn pastel dịu mắt và giữ cho các dòng tên tác giả, GVHD, tên trường/viện dài trên khung hình `4:3` luôn sắc nét tuyệt đối khi đi qua vùng đồ họa.
  - **`titlepage=solid` (hoặc `coverbg=solid`)**: Nền màu đặc thương hiệu (`hustmain`: Xanh lam đậm hoặc Đỏ HUST) hoàn toàn không có vòng chấm đồ họa; tự động chuyển cụm logo HUST sang phiên bản trắng âm bản (`dark`) và chữ tiêu đề/tác giả sang tông trắng – vàng tương phản cao.
  - **`titlepage=dark`**: Nền tối kèm vòng chấm tròn đồng tâm (`bg-dark-*`), toàn bộ khối tiêu đề được căn giữa màn hình.
- **Màu sắc khối thông tin trang bìa (trên nền sáng `cover` & `light`)**:
  - **Tiêu đề chính (`title`)**: Màu thương hiệu chủ đạo `hustcover` (Xanh lam đậm `#003366` hoặc Đỏ HUST `#C02034`), phông **Avant Garde** (`TeX Gyre Adventor`) in hoa đậm.
  - **Phụ đề (`subtitle`) & Đơn vị (`institute`)**: Màu đen nhận diện sắc nét **`HUSTBlack`** (`#231F20`).
  - **Tác giả (`author`)**: Sử dụng màu nhấn thương hiệu của slide (**`hustaccent`** $\to$ Đỏ cờ `#CE1628` trên bản Xanh, Hổ phách `#E59C0A` trên bản Đỏ).
- **Quy tắc chính tả chuẩn Sổ tay thương hiệu (Trang 79–80)**:
  - Tên trường đầy đủ: `Đại học Bách khoa Hà Nội` (không viết hoa chữ `khoa`), viết tắt: `ĐHBK Hà Nội` (không viết tắt `ĐHBKHN`).
  - Tên đơn vị trực thuộc: Viết hoa chữ cái đầu sau danh từ chung và từ ghép (ví dụ: `Trường Công nghệ Thông tin và Truyền thông, Đại học Bách khoa Hà Nội`).
  - Học hàm, học vị: Có khoảng trắng sau dấu chấm (ví dụ: `GS. TS.`, `PGS. TS.`).
- **Định dạng ngày tháng tiếng Việt chuẩn hành chính**:
  - Lệnh `\today` được định nghĩa lại tự động theo chuẩn tiếng Việt có địa danh: `Hà Nội, ngày ... tháng ... năm ...`.
  - **Tùy chọn bật/tắt địa danh**: Sử dụng `dateaddress = on | off` trong `\usetheme` hoặc `\hustsetup{dateaddress=off}` (khi tắt sẽ hiển thị `ngày ... tháng ... năm ...`).
  - **Tùy chọn thay đổi địa danh**: Sử dụng `address={...}` hoặc `location={...}` (ví dụ: `address={Đà Nẵng}` $\to$ `Đà Nẵng, ngày ... tháng ... năm ...`).
  - **Lệnh ngày cố định tùy biến `\hustdate`** (đồng thời tự động cập nhật ngày ngắn `DD/MM/YYYY` cho `footermeta`):
    ```latex
    \date{\hustdate{8}{7}{2025}}                  % "Hà Nội, ngày 8 tháng 7 năm 2025" (footermeta: 08/07/2025)
    \date{\hustdate[none]{8}{7}{2025}}            % "ngày 8 tháng 7 năm 2025"
    \date{\hustdate[TP. Hồ Chí Minh]{8}{7}{2025}} % "TP. Hồ Chí Minh, ngày 8 tháng 7 năm 2025"
    ```

### 6.20. Dải Thông Tin Tích Hợp Chân Trang (`footermeta=on`)

Khi bật `footermeta=on` (hoặc `footerinfo=on`) trong `\usetheme` hoặc `\hustsetup`:
- **Bố cục 4 thành phần trên cùng một dải chân trang**:
  1. **Tác giả (`\insertshortauthor`)**: Căn trái ngay sau logo chân trang.
  2. **Tiêu đề báo cáo (`\insertshorttitle`)**: Đặt ở khoảng giữa tác giả và ngày tháng. Nếu tiêu đề dài, hệ thống tự động ngắt thành nhiều dòng (`\parbox[b]`) neo đáy ngang hàng với tác giả và ngày tháng, đồng thời **tự động nâng đường kẻ ngang `hustaccent` lên cao** để nằm phía trên tiêu đề mà không bao giờ cắt ngang chữ.
  3. **Ngày tháng rút gọn (`DD/MM/YYYY`)**: Tự động trích xuất từ `\today` hoặc từ `\hustdate{D}{M}{Y}`, đặt ngay bên trái số trang.
  4. **Số trang (`n/N` hoặc `n`)**: Giữ nguyên vị trí neo cố định ở góc phải dưới (`numR`, `numY`).
- **Tự động nhường chỗ cho `\cite` và `\note`**: Bất kỳ slide nào có gọi `\cite{...}`, `\footnote{...}` hoặc `\note{...}{...}` sẽ tự động tắt dải `footermeta` trên đúng slide đó để nhường toàn bộ không gian chân trang cho hộp trích dẫn/chú thích (tối đa 4 dòng).
- **Lệnh ghi đè tùy chọn & Chế độ giữ nguyên không cắt ngắn (`-1`)**:
  - Tùy biến nội dung: `footerauthor={...}`, `footertitle={...}`, `footerdate={...}`.
  - Tùy chọn giới hạn độ dài: `footertitlemax={N}` và `footerauthormax={N}`. Mặc định là `-1` (**không bao giờ cắt ngắn**, giữ nguyên toàn bộ văn bản và cho phép tiêu đề tự ngắt dòng xuống phía dưới nếu dài, đường kẻ trên tự động nâng lên bảo vệ chữ). Khi muốn ép buộc cắt ngắn bằng `...`, bạn có thể đặt số nguyên dương $N > 0$ (ví dụ: `footertitlemax=40`).

### 6.21. Danh Mục Khung Hình Chuyên Dụng & Lệnh Toàn Cục (Frame Types & Commands)

Bảng tổng hợp toàn bộ các môi trường khung hình và lệnh chuyên biệt của gói theme HUST (như minh họa tại Slide 4.2):

| Tên Môi Trường / Lệnh | Tùy Chọn & Đối Số | Mục Đích Sử Dụng & Đặc Tính |
| :--- | :--- | :--- |
| `frame` | `[t\|c\|b]`, `[plain]`, `[fragile]`, `[noframenumbering]`, `[noprogressbar]` | Khung trình chiếu nội dung tiêu chuẩn. Hỗ trợ tắt thanh tiến trình với `[noprogressbar]` trên các slide cần tập trung cao độ (TOC, References). |
| `hustwelcomeframe` | `[bg=dark\|background]`, `[footer={...}]`, `[slogan={...}]` | Slide chào mừng mở màn (Hình 14: cụm logo chữ `HUST` + 2 dòng tên trường Việt – Anh khớp độ rộng tuyệt đối và cách nhau $\frac{1}{3}x$). |
| `husttocframe` / `\hustprinttoc` | `[split=N]`, `[title={...}]`, `[subtitle={...}]` | Khung mục lục toàn cục tự động ẩn thanh tiến trình, hỗ trợ tách 2 cột từ mục `N`. |
| `hustdarkframe` | Tùy chọn Beamer bất kỳ | Slide nền đậm toàn màn hình với nhận diện thương hiệu HUST (dùng cho slide Kết luận, Cảm ơn, Q&A). |
| `hustbackgroundframe` | Tùy chọn Beamer bất kỳ | Slide với nền hoa văn chìm vòng chấm tròn HUST toàn trang (`bg-background-*`). |
| `hustreferencesframe` / `\hustprintreferences` | `[from=N, to=M]`, `[title={...}]`, `[subtitle={...}]` | Khung hiển thị tài liệu tham khảo phân trang thủ công từ mục `N` đến `M`, giữ nguyên tiêu đề thống nhất và tự động ẩn thanh tiến trình. |
| `\hustsection` / `\hustpanel` | `[panel=true\|false]`, `[true\|false]`, `[on\|off]`, `[none]` | Đặt ngay trước lệnh `\section{...}` tiêu chuẩn để điều khiển bật/tắt slide chuyển mục (*Section Transition Panel*) cho mục đó mà không làm lệch cây cấu trúc (*Structure pane*) của TeXstudio. |
| `\hustPanelFrame` | Không có đối số | Chèn thủ công một slide chuyển mục tại vị trí bất kỳ ngay cả khi `sectionpage=none`. |
| `\hustcaption[tên][số]{nội dung}\label{key}` | `[tên=Hình\|Bảng\|...]`, `[số]`, `{nội dung}` | Động cơ chú thích vạn năng cho hình vẽ TikZ, bảng biểu, mã nguồn, thuật toán. Hỗ trợ tự động tăng số hoặc gán số thủ công tùy biến (`Bảng 2.5`, `Hình 6`), tích hợp `\cref` nhấp được 100%. |
| `\hustlogo[...]` | `height`, `layout=1\|2\|3\|4a\|4b`, `unit`, `vn`, `en`, `image`, `color`, `unitcolor`, `linecolor`, `equalwidth`, `dark` | Vẽ cụm logo vector động chuẩn Sổ tay thương hiệu (Hình 7, Hình 9, Hình 17a) với khoảng cách an toàn $\frac{1}{3}x$ (`0.333 H`). |
| `\hustwordmarklockup[...]` | `height`, `image`, `color` | Vẽ cụm logo viết tắt `HUST` kèm 2 dòng tên trường tiếng Việt & tiếng Anh theo đúng quy chuẩn Hình 14. |
| `\note{text}{content}` | `{từ khóa}{nội dung giải thích}` | Ghi chú chân trang chữ cái ($a, b, \dots$) mang màu nhấn `hustaccent` (phân biệt với `\cite` mang màu `hustmain`), đồng bộ trong hộp chân trang khóa tối đa 4 dòng. |
| `\hustsetup{...}` | Danh sách `key=value` bất kỳ | Thay đổi linh hoạt mọi tùy chọn của theme ở bất kỳ đâu trong preamble hoặc giữa các slide. |

### 6.22. Hệ Màu Quy Chuẩn & Định Danh Màu Sẵn Có (Color Definitions)

Theme nạp sẵn toàn bộ các hằng số màu thương hiệu vào không gian tên LaTeX/xcolor, cho phép sử dụng trực tiếp trong tài liệu với các lệnh `\textcolor{<màu>}{...}`, `\colorbox{<màu>}{...}`, `\rowcolor{<màu>}` hoặc trong tùy chọn TikZ/Beamer blocks:

| Tên Màu Trực Tiếp | Mã Hex | Sắc Thái Nhận Diện Thương Hiệu HUST |
| :--- | :--- | :--- |
| `HUSTNavy` / `HUSTBlue` | `#003366` | Xanh lam đậm chủ đạo của trường (HUST Blue) |
| `HUSTRed` / `HUSTCrimson` | `#CE1628` | Đỏ cờ thương hiệu HUST (HUST Red) |
| `HUSTYellow` | `#F3C108` | Vàng sao nhận diện thương hiệu |
| `HUSTOrange` | `#F57F20` | Cam phụ trợ thể hiện nhiệt huyết, năng động |
| `HUSTBlack` | `#231F20` | Đen tuyền nhận diện tiêu chuẩn (thay cho đen `#000000`) |
| `HUSTLightBlue` | `#5B9BD5` | Xanh dương nhạt dùng cho thanh tiến trình / biểu đồ |
| `HUSTLightRed` | `#F05C5D` | Đỏ nhạt dùng cho thanh tiến trình / cảnh báo nhẹ |
| `HUSTPink` | `#FAD2D2` | Hồng nhạt nền khối / cảnh báo |
| `HUSTGrey` / `HUSTGray` | `#A6A6A6` | Xám phân cách và đường viền phụ |
| `famiblue` | `#0062A5` | Xanh lam chuẩn huy hiệu Khoa Toán - Tin (FaMI) |

**Gợi ý sử dụng màu tương đối (Relative Tints)**:
- Nền bảng biểu xen kẽ: `\rowcolor{hustmain!6}` hoặc `\rowcolor{hustmain!8}`.
- Viền nhấn khối thông tin: `draw=hustmain!80` hoặc `draw=hustalert!70`.
- Khối cảnh báo hoặc ví dụ: `hustalert!8` (Đỏ nhạt) và `hustexample!8` (Cam nhạt).

### 6.23. Gợi Ý Lựa Chọn Tỉ Lệ Khung Hình & Phông Chữ (Aspect Ratios & Fonts)

#### Tỉ Lệ Màn Hình Hỗ Trợ:
Bộ theme hỗ trợ hệ thống tính toán tọa độ vector thích ứng (`\hust@fW`, `\hust@fH`) tương thích toàn diện với tất cả các tỉ lệ của Beamer:
- **`aspectratio=169` (16:9, 160mm $\times$ 90mm)**: Khung hình rộng hiện đại, chuẩn trình chiếu màn hình LED, tivi thông minh, máy chiếu HD/4K tại các giảng đường và hội trường mới.
- **`aspectratio=43` (4:3, 128mm $\times$ 96mm)**: Khung hình truyền thống, tối ưu cho các máy chiếu phòng học đời cũ hoặc hội đồng bảo vệ chuyên môn.
- **`aspectratio=1610` (16:10, 160mm $\times$ 100mm)**: Tỉ lệ màn hình máy tính xách tay hiện đại (MacBook Pro, Dell XPS).
- **`aspectratio=149` (14:9, 140mm $\times$ 90mm)**: Tỉ lệ trung gian cân đối.
- **`aspectratio=54` (5:4, 125mm $\times$ 100mm)**: Tỉ lệ gần vuông cho màn hình giám sát hoặc hiển thị đứng.
- **`aspectratio=32` (3:2, 135mm $\times$ 90mm)**: Tương thích màn hình Microsoft Surface và tablet.
- **`aspectratio=141` (1.41:1, 141.4mm $\times$ 100mm)**: Khung hình tương đương khổ giấy A4 xoay ngang, thuận tiện in ấn tài liệu thuyết trình.

#### Khuyến Nghị Lựa Chọn Phông Chữ (`font=...`):
- **`font=lato` (Được dùng trong `test_deck.tex`)**: Phông chữ không chân hình học (geometric sans-serif) thanh thoát, độ cao x-height lớn, tính thẩm mỹ hiện đại, hỗ trợ tiếng Việt mượt mà. Rất phù hợp cho các bài báo cáo công nghệ, hội thảo quốc tế, bài giảng trực quan.
- **`font=cm` (Được dùng trong `test_variants.tex`)**: Bộ phông Computer Modern / Latin Modern kinh điển của Donald Knuth. Thể hiện công thức toán học, biểu thức vi phân giải tích, ký hiệu giải thuật với độ hoàn mỹ cao nhất.
- **`font=times`**: Phông chữ có chân Times New Roman chuẩn mực, trang trọng. Phù hợp cho bảo vệ đồ án tốt nghiệp, luận án tiến sĩ, báo cáo khoa học theo format truyền thống.
- **`font=arial`**: Phông không chân thông dụng, nét chữ dày và rõ, dễ đọc từ khoảng cách xa trong các hội trường lớn.

### 6.24. Tùy Biến Góc Phải Thanh Tiêu Đề (`headerright`, `headernumber`, `headerlogo`)

Phần bên phải của thanh tiêu đề (`frametitle`) mặc định để trống (`headerright=off`), nhưng có thể bật một trong hai chế độ hiển thị chuyên biệt:

1. **Chuyển Số Trang Lên Góc Phải Thanh Tiêu Đề (`headerright=pagenumber` hoặc `headernumber=on`)**:
   - Số trang (`4/21`) được đặt ở góc phải thanh tiêu đề, căn giữa hoàn hảo theo chiều dọc của dải màu chính trong mọi chế độ (`bar=thin` hoặc `bar=thick`, có hoặc không có `framesubtitle` và `progressbar`).
   - Sử dụng cùng kiểu chữ đậm của `frametitle` với màu vàng phụ đề (`hustsubyellow` `#FFDE59`) nổi bật trên cả phiên bản Đỏ và Xanh.
   - Tự động tắt số trang ở góc phải dưới chân trang và dồn ngày tháng (`footerdate`) sát lề phải của thanh chân trang, mở rộng không gian cho Tác giả — Tiêu đề — Ngày tháng:
   ```latex
   \usetheme[
     color=red,
     numbering=fraction,
     headerright=pagenumber,   % Hoặc headernumber=on
     footermeta=on
   ]{HUST}
   ```

2. **Hiển Thị Logo Phụ Có Viền Trắng Bảo Toàn Ở Góc Phải Thanh Tiêu Đề (`headerlogo=<file>`)**:
   - Theo quy chuẩn Sổ tay nhận diện thương hiệu ĐHBK Hà Nội (mục *Logo trên nền tối / nền màu*), khi đặt logo trên nền màu xanh đậm hoặc đỏ cờ, bắt buộc phải có đường viền trắng bao quanh; đồng thời logo đơn vị như `fami-shield.png` có nền trong suốt.
   - Theme giải quyết triệt để cả hai bài toán bằng cách vẽ một khối chữ nhật màu trắng (`\colorbox{white}`) có kích thước cộng sẵn phần đệm viền trắng (`1.4pt`), đặt logo nằm chính giữa bên trên khối trắng đó, và chừa khoảng đệm trên/dưới/phải để màu của thanh tiêu đề chảy bao quanh:
   ```latex
   \usetheme[
     color=blue,
     headerlogo=fami-shield.png % Tự động bật headerright=logo kèm khung đệm trắng
   ]{HUST}
   ```

### 6.25. Họa Tiết Thoi Chéo Nền Slide & Panel Từ Trang 1 Sổ Tay Thương Hiệu (`framebg`)

Trên Trang 1 của *Sổ tay hướng dẫn nhận diện thương hiệu ĐHBK Hà Nội*, góc phải dải băng đỏ sử dụng họa tiết 21 hình thoi bo góc xếp chéo $45^\circ$ (với bộ lọc mask độ mờ `15%` trên nền đỏ `#CE1628`). Bộ công cụ `tools/generate_diag_bg.ps1` đã trích xuất chính xác đường cong vector Bézier từ Sổ tay, khôi phục trọn vẹn hàng thoi đầu tiên bị cắt ở mép trên, và kết xuất thành 2 tài nguyên màu đặc sắc nét `assets/bg-diag-red.png` (`#CE1628`) và `assets/bg-diag-blue.png` (`#003366`).

- Khi bật `framebg=on` (hoặc `diagbg=on`, `texture=on`), họa tiết được áp lên toàn bộ các **frame nội dung** và **trang chuyển mục (`panel`)** (tự động loại trừ màn hình chào mừng, trang bìa và màn hình kết thúc nền tối).
- **Vị trí và tỉ lệ góc dưới phải (Bottom-Right Corner)**: Đúng tinh thần thiết kế chuẩn của Sổ tay thương hiệu ĐHBK Hà Nội, họa tiết được thu gọn thành điểm nhấn tinh tế ở **góc dưới cùng bên phải**:
  - Trên **frame nội dung**: Căn sát mép phải (`anchor=south east`), đặt ngay phía trên đường kẻ chỉ chân trang (`footY`), chiếm khoảng $24\%\text{--}26\%$ chiều cao slide (`0.26\paperheight` ở 16:9, `0.24\paperheight` ở 4:3) và chỉ chiếm khoảng $13\%\text{--}16\%$ chiều rộng lề phải, để lại toàn bộ không gian chính giữa và phía trên hoàn toàn thanh thoát, không bao giờ đè hay làm rối nội dung văn bản, bảng biểu hay công thức.
  - Trên **trang chuyển mục (`panel`)**: Căn sát góc dưới phải tuyệt đối (`current page.south east`) với chiều cao gọn gàng `0.28\paperheight` (16:9) hoặc `0.26\paperheight` (4:3), nằm phía dưới và cách xa danh mục mục lục bên phải.
- **Tùy chỉnh chiều cao và độ mờ**:
  - `framebgopacity=<giá_trị>` (mặc định `0.08` tức 8%): Tùy chỉnh độ mờ của họa tiết nền.
  - `framebgheight=<độ_dài>` (mặc định `auto`): Cho phép người dùng truyền kích thước chiều cao tùy ý (ví dụ `2.5cm`, `0.25\paperheight`) nếu muốn điều chỉnh độ lớn họa tiết.
  - Tự động đồng bộ màu theo chủ đề: `color=blue` nạp `bg-diag-blue.png`, `color=red` nạp `bg-diag-red.png` (hoặc ép màu qua `framebg=blue` / `framebg=red`).

```latex
\usetheme[
  color=blue,
  framebg=on,             % Bật họa tiết thoi chéo góc dưới phải
  framebgopacity=0.08,    % Độ mờ tinh tế (mặc định 0.08)
  framebgheight=auto      % Tự động tỉ lệ chuẩn (hoặc truyền số đo tùy ý như 2.4cm)
]{HUST}
```

---

## 7. Mở Rộng Và Tùy Biến Trong Tương Lai

Bộ theme được thiết kế theo tư duy mã nguồn mở, tách biệt rõ ràng giữa logic tọa độ, màu sắc và kiểu chữ:

- Muốn bổ sung màu sắc mới: Khai báo thêm trong `hust-core.sty` và `beamercolorthemeHUST.sty`.
- Muốn bổ sung layout mới: Bạn có thể sao chép cách viết các khối TikZ overlay từ `beamerinnerthemeHUST.sty` và `beamerouterthemeHUST.sty`.
- Tọa độ hình học tỉ lệ màn hình đều được tính toán theo tỷ lệ phần trăm chuẩn (`\hust@fW`, `\hust@fH`) trong `hust-core.sty`.
