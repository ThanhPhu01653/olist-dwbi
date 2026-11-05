"""ONE-TIME bootstrap of the LaTeX report skeleton in report/ (main.tex, preamble, chapters/*.tex, refs.bib).

    python scripts/bootstrap_report.py [--force]
Chapter 3 is filled with the draft paragraphs of handoff/*.md and huong-dan/*.md converted to LaTeX; the team then edits report/chapters/*.tex by hand.
The script REFUSES to run when report/chapters/ already exists unless --force (that would overwrite the team's text). Data tables are NOT written here: they come
from scripts/export_latex.py (report/tables/), which can be re-run at any time.
"""
from __future__ import annotations

import re
import shutil
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
REP = ROOT / "report"
CH = REP / "chapters"


def esc(s: str) -> str:
    for a, b in [("\\", r"\textbackslash{}"), ("&", r"\&"), ("%", r"\%"), ("$", r"\$"), ("#", r"\#"), ("_", r"\_"), ("{", r"\{"), ("}", r"\}"), ("~", r"\textasciitilde{}"), ("^", r"\textasciicircum{}")]:
        s = s.replace(a, b)
    return s


def md2tex(s: str) -> str:
    """Small markdown -> LaTeX converter for the draft paragraphs (code, bold, italic, links, arrows)."""
    parts = re.split(r"(`[^`]+`)", s)
    out = []
    for p in parts:
        if p.startswith("`") and p.endswith("`") and len(p) > 2:
            out.append(r"\code{" + esc(p[1:-1]).replace(r"\_", r"\_\allowbreak{}") + "}")
        else:
            t = esc(p)
            t = re.sub(r"\*\*(.+?)\*\*", r"\\textbf{\1}", t)
            t = re.sub(r"(?<![\w*])\*(?!\s)(.+?)(?<!\s)\*(?![\w*])", r"\\emph{\1}", t)
            t = re.sub(r"\[([^\]]+)\]\((?:https?://[^)]+)\)", r"\1", t)
            t = t.replace("→", r"$\rightarrow$").replace("≤", r"$\leq$").replace("≥", r"$\geq$").replace("×", r"$\times$").replace("≈", r"$\approx$").replace("−", "-").replace("Σ", r"$\Sigma$")
            out.append(t)
    return "".join(out)


def draft(fname: str, heading: str) -> str:
    """Paragraph(s) under the '## <heading...>' of a handoff file."""
    txt = (ROOT / fname).read_text(encoding="utf-8")
    m = re.search(r"^## " + re.escape(heading) + r".*?\n(.*?)(?=^## |\Z)", txt, re.S | re.M)
    if not m:
        raise SystemExit(f"draft not found: {fname} / {heading}")
    return "\n\n".join(md2tex(p.strip()) for p in m.group(1).strip().split("\n\n") if p.strip())


def section(fname: str, num: str) -> str:
    """Body of '## <num>. ...' in huong-dan/dashboards/Dx.md."""
    txt = (ROOT / fname).read_text(encoding="utf-8")
    m = re.search(r"^## " + re.escape(num) + r"\. .*?\n(.*?)(?=^## |\Z)", txt, re.S | re.M)
    return m.group(1).strip() if m else ""


def itemize(items: list[str], todo: str = "") -> str:
    body = "\\begin{itemize}\n" + "\n".join(f"  \\item {md2tex(i)}" for i in items) + "\n\\end{itemize}"
    return body + (f"\n\\todo{{{todo}}}" if todo else "")


def fig(file: str, cap: str, label: str, w: str = "0.9") -> str:
    return f"\\hinh{{{file}}}{{{cap}}}{{{label}}}{{{w}}}"


MAIN = r"""% Báo cáo bài tập lớn - Kho dữ liệu và Kinh doanh thông minh (MI4214). Biên dịch: XeLaTeX (latexmk -xelatex main.tex)
\documentclass[12pt,a4paper]{report}
\input{preamble}
\begin{document}
\pagenumbering{roman}
\input{chapters/00-bia}
\input{chapters/00-loi-mo-dau}
\input{chapters/00-danh-gia-thanh-vien}
\input{chapters/00-tu-danh-gia}
\tableofcontents
\listoffigures
\listoftables
\input{chapters/00-viet-tat}
\cleardoublepage
\pagenumbering{arabic}
\setcounter{page}{1}

\chapter{Tổng quan về kho dữ liệu}
\input{chapters/01-tong-quan-dw}
\chapter{Tổng quan về kinh doanh thông minh}
\input{chapters/02-tong-quan-bi}

\chapter{Ứng dụng kho dữ liệu và BI vào bài toán quản lý đơn hàng Olist}
\section{Giới thiệu bài toán}
\input{chapters/3-1-gioi-thieu}
\section{Khảo sát nghiệp vụ và dữ liệu}
\input{chapters/3-2-1-quy-trinh}
\input{chapters/3-2-2-yeu-cau}
\input{chapters/3-2-3-he-thong-du-lieu}
\input{chapters/3-2-4-erd-oltp}
\section{Phân tích và thiết kế}
\input{chapters/3-3-1-kham-pha}
\input{chapters/3-3-2-kien-truc}
\input{chapters/3-3-3-ods}
\input{chapters/3-3-4-thiet-ke-kho}
\input{chapters/3-3-5-kpi}
\section{Xây dựng hệ thống}
\input{chapters/3-4-1-moi-truong}
\input{chapters/3-4-2-staging-ods}
\input{chapters/3-4-3-doi-soat-tang-dan}
\input{chapters/3-4-4-mart-olap}
\input{chapters/3-4-5-dashboard}
\section{Các nội dung mở rộng}
\input{chapters/3-5-1-hieu-nang}
\input{chapters/3-5-2-dia-ly}

\chapter{Kết luận và bài học kinh nghiệm}
\input{chapters/04-ket-luan}

\bibliographystyle{plain}
\renewcommand{\bibname}{Tài liệu tham khảo}
\bibliography{refs}
\addcontentsline{toc}{chapter}{Tài liệu tham khảo}

\appendix
\chapter{Thư viện measure DAX}
\input{chapters/phu-luc-dax}
\chapter{SQL tiêu biểu}
\input{chapters/phu-luc-sql}
\chapter{Ánh xạ ODS sang kho dữ liệu}
\input{tables/mapping}
% \listoftodos   % bỏ dấu % để xem danh sách việc còn lại (todonotes)
\end{document}
"""

PREAMBLE = r"""% Gói và cấu hình chung. Font Times New Roman (nếu máy không có thì dùng TeX Gyre Termes, có sẵn trên Overleaf).
\usepackage{fontspec}
\IfFontExistsTF{Times New Roman}{\setmainfont{Times New Roman}}{\setmainfont{TeX Gyre Termes}}
\IfFontExistsTF{Courier New}{\setmonofont{Courier New}[Scale=0.88]}{\setmonofont{TeX Gyre Cursor}[Scale=0.95]}
\usepackage[vietnamese]{babel}
\usepackage[a4paper,left=3cm,right=2cm,top=2.5cm,bottom=2.5cm]{geometry}
\usepackage{setspace}
\setstretch{1.3}
\usepackage{graphicx,booktabs,longtable,array,tabularx,float,caption,xcolor,amssymb,enumitem,fancyhdr,titlesec,listings}
\usepackage[colorinlistoftodos,textsize=small]{todonotes}
\presetkeys{todonotes}{inline}{}   % mọi \todo hiện ngay trong dòng văn bản (khung vàng), dễ thấy khi soát
\usepackage[hidelinks]{hyperref}
\captionsetup{font=small,labelfont=bf,labelsep=period}
\setlist{itemsep=2pt,topsep=3pt}
\emergencystretch=3em
\setlength{\parindent}{1.0cm}
\setlength{\parskip}{3pt}
\pagestyle{plain}
\newcommand{\code}[1]{\texttt{#1}}
\newcommand{\hinh}[4]{\begin{figure}[htbp]\centering\includegraphics[width=#4\textwidth,keepaspectratio]{figures/#1}\caption{#2}\label{#3}\end{figure}}
\newcommand{\khunganh}[2]{\begin{figure}[htbp]\centering\fbox{\parbox[c][5.5cm][c]{0.9\textwidth}{\centering\textit{#1}}}\caption{#2}\end{figure}}
\lstset{basicstyle=\ttfamily\footnotesize,breaklines=true,breakatwhitespace=false,columns=fullflexible,frame=single,framesep=3pt,numbers=none,keepspaces=true,showstringspaces=false,
  upquote=false,xleftmargin=0pt,literate={→}{{$\rightarrow$}}1 {≤}{{$\leq$}}1 {≥}{{$\geq$}}1}
\lstdefinelanguage{SQLvi}{morekeywords={SELECT,FROM,WHERE,GROUP,BY,ORDER,JOIN,LEFT,ON,AND,OR,NOT,NULL,CASE,WHEN,THEN,ELSE,END,AS,WITH,INSERT,INTO,UPDATE,SET,DELETE,CREATE,OR,REPLACE,PROCEDURE,FUNCTION,LANGUAGE,BEGIN,DECLARE,RETURNS,DISTINCT,ROLLUP,CUBE,GROUPING,SETS,FILTER,COUNT,SUM,AVG,OVER,PARTITION,UNION,ALL,EXISTS,IN,IS,CONFLICT,DO,NOTHING,USING,INOUT,CALL,RETURNING,HAVING,LIMIT},sensitive=false,morecomment=[l]{--},morestring=[b]'}
"""

COVER = (ROOT / "scripts" / "report_cover.tex").read_text(encoding="utf-8")

FOREWORD = r"""\chapter*{Lời mở đầu}
\addcontentsline{toc}{chapter}{Lời mở đầu}
\todo{Viết lời mở đầu (nửa trang đến một trang): bối cảnh (thương mại điện tử, nhu cầu phân tích dữ liệu), mục tiêu của bài tập lớn, phạm vi (hai bộ dữ liệu Olist, PostgreSQL, Power BI), bố cục báo cáo ba chương và kết luận, lời cảm ơn giảng viên.}
\begin{itemize}
  \item Bối cảnh: thương mại điện tử Brazil và vai trò của dữ liệu đơn hàng (gợi ý số liệu: 99.441 đơn, 3.095 seller, 8.000 khách tiềm năng).
  \item Mục tiêu: xây kho dữ liệu chủ đề Order Management, tích hợp funnel thu hút seller, và 7 dashboard Power BI.
  \item Bố cục: Chương 1 kho dữ liệu, Chương 2 kinh doanh thông minh, Chương 3 ứng dụng, kết luận.
\end{itemize}
"""

RATING = r"""\chapter*{Bảng đánh giá thành viên}
\addcontentsline{toc}{chapter}{Bảng đánh giá thành viên}
\noindent\textbf{Môn học:} Kho dữ liệu và Kinh doanh thông minh (MI4214)\qquad\textbf{Lớp:} \dotfill\qquad\textbf{Nhóm:} \dotfill\\[4pt]
\noindent\textbf{Người đánh giá (trưởng nhóm):} \dotfill

\medskip
\begin{center}
\small
\renewcommand{\arraystretch}{1.6}
\begin{tabularx}{\textwidth}{|c|>{\raggedright\arraybackslash}p{2.8cm}|>{\centering\arraybackslash}X|>{\centering\arraybackslash}X|>{\centering\arraybackslash}X|>{\centering\arraybackslash}X|>{\centering\arraybackslash}X|c|}
\hline
\textbf{STT} & \textbf{Tên thành viên} & \textbf{Làm tốt phần việc được giao} & \textbf{Liên hệ được khi cần} & \textbf{Khả năng đóng góp sáng kiến, ý kiến cho hoạt động nhóm} & \textbf{Sẵn sàng giúp đỡ} & \textbf{Đóng góp chung vào kết quả của nhóm} & \textbf{Tổng điểm}\\
\hline
1 & & & & & & & \\ \hline
2 & & & & & & & \\ \hline
3 & & & & & & & \\ \hline
4 & & & & & & & \\ \hline
5 & & & & & & & \\ \hline
6 & & & & & & & \\ \hline
\end{tabularx}
\end{center}

\noindent\textbf{Chú ý:}
\begin{itemize}
  \item Điểm mỗi tiêu chí từ 1 đến 5 (cao nhất là 5, thấp nhất là 1); tổng điểm tối đa là 25.
  \item Điểm đánh giá của mỗi thành viên trong nhóm phải có \textbf{tối thiểu 4 bậc điểm} (không cho mọi thành viên cùng một điểm).
  \item Bảng đánh giá này do \textbf{trưởng nhóm} lập; tất cả thành viên cần \textbf{ký} (ghi rõ họ tên).
\end{itemize}
\todo{Trưởng nhóm điền điểm sau khi cả nhóm thống nhất; in ra và ký. Mẫu theo bảng đánh giá thành viên của môn học (5 tiêu chí).}

\bigskip
\noindent\textbf{Chữ ký các thành viên:}\\[1.2cm]
\begin{tabular}{p{2.8cm}p{2.8cm}p{2.8cm}p{2.8cm}p{2.8cm}}
1. \dotfill & 2. \dotfill & 3. \dotfill & 4. \dotfill & 5. \dotfill
\end{tabular}
"""

SELFEVAL = r"""\chapter*{Tự đánh giá báo cáo}
\addcontentsline{toc}{chapter}{Tự đánh giá báo cáo}
Nhóm tự đối chiếu báo cáo với yêu cầu nội dung và trình bày của môn học (đánh dấu \checkmark{} khi đạt, ghi chú nếu chưa).

\begin{center}\small\renewcommand{\arraystretch}{1.3}
\begin{tabularx}{\textwidth}{|>{\raggedright\arraybackslash}X|c|>{\raggedright\arraybackslash}p{4cm}|}
\hline
\textbf{Yêu cầu} & \textbf{Đạt} & \textbf{Vị trí / ghi chú}\\ \hline
Phần I: Tổng quan về kho dữ liệu & & Chương 1\\ \hline
Phần II: Tổng quan về BI & & Chương 2\\ \hline
Phần III: Ứng dụng vào bài toán: giới thiệu bài toán (requirement) & & Mục 3.1, 3.2.1--3.2.2\\ \hline
Giới thiệu về ODS & & Mục 3.3.3, 3.4.2\\ \hline
Kiến trúc kho dữ liệu (có logo công nghệ ở mỗi phần) & & Mục 3.3.2\\ \hline
Tiền xử lý dữ liệu (có before--after) & & Mục 3.3.1, 3.4.2--3.4.3\\ \hline
Mô hình dữ liệu OLTP (gạch chân trường dùng sang OLAP, ghi mapping) & & Mục 3.2.4, Phụ lục C\\ \hline
Mô hình dữ liệu OLAP (data model logic, vật lý; fact/dimension khác màu) & & Mục 3.3.4\\ \hline
Các mẫu dashboard (đa dạng biểu đồ, slicer, định dạng có điều kiện) & & Mục 3.4.5\\ \hline
Có mục lục, kết luận, tài liệu tham khảo, có số trang & & \\ \hline
Font Times New Roman 12, căn lề hai bên & & \\ \hline
Không sai chính tả & & \\ \hline
\end{tabularx}
\end{center}
\todo{Nhóm điền cột "Đạt" và ghi chú khi hoàn thiện báo cáo.}
"""

ABBR = r"""\chapter*{Danh mục từ viết tắt}
\addcontentsline{toc}{chapter}{Danh mục từ viết tắt}
\begin{longtable}{p{3cm}p{12cm}}
\toprule \textbf{Từ viết tắt} & \textbf{Ý nghĩa}\\ \midrule
BI & Business Intelligence -- kinh doanh thông minh\\
BPMN & Business Process Model and Notation\\
CSV & Comma-Separated Values\\
DAX & Data Analysis Expressions\\
DW & Data Warehouse -- kho dữ liệu\\
ERD & Entity Relationship Diagram -- sơ đồ thực thể quan hệ\\
ETL & Extract -- Transform -- Load\\
GMV & Gross Merchandise Value -- tổng giá trị hàng bán\\
HOLAP & Hybrid OLAP\\
KPI & Key Performance Indicator -- chỉ số hiệu suất chính\\
MOLAP & Multidimensional OLAP\\
MQL & Marketing Qualified Lead -- khách tiềm năng đã qua sàng lọc marketing\\
ODS & Operational Data Store\\
OLAP & Online Analytical Processing\\
OLTP & Online Transaction Processing\\
RFM & Recency -- Frequency -- Monetary\\
ROLAP & Relational OLAP\\
SCD & Slowly Changing Dimension\\
SDR / SR & Sales Development Representative / Sales Representative\\
SQL & Structured Query Language\\
\bottomrule
\end{longtable}
\todo{Bổ sung các từ viết tắt khác xuất hiện trong báo cáo.}
"""

CH1 = r"""\todo{Chương 1 chỉ có khung: nhóm tự viết văn bản từ các ý chính bên dưới, trích dẫn nguồn đã đọc. Các trích dẫn dưới đây là gợi ý trong refs.bib; kiểm tra lại trang/phiên bản trước khi dùng. Tham chiếu nội dung môn học: giáo trình và slide chương 1, 2, 5, 6.}

\section{Giới thiệu về kho dữ liệu}
\begin{itemize}
  \item Khái niệm kho dữ liệu; định nghĩa của Inmon: hướng chủ đề, tích hợp, biến thiên theo thời gian, không biến động \cite{inmon2005}; cách nhìn của Kimball \cite{kimball2013}.
  \item Vì sao doanh nghiệp cần kho dữ liệu: hệ thống nguồn rời rạc, dữ liệu không nhất quán, nhu cầu phân tích lịch sử.
  \item Đặc tính của kho dữ liệu và lợi ích (một nguồn sự thật, định nghĩa KPI thống nhất).
\end{itemize}

\section{OLTP và OLAP}
\begin{itemize}
  \item So sánh hệ thống giao dịch (OLTP) và hệ thống phân tích (OLAP): mục đích, mô hình dữ liệu (chuẩn hóa so với chiều), kiểu truy vấn, khối lượng, người dùng \cite{chaudhuri1997}.
  \item Ví dụ minh họa lấy từ dự án: 9 bảng chuẩn hóa của hệ thống bán hàng so với 1 fact và các chiều (liên hệ Chương 3).
\end{itemize}

\section{Kiến trúc kho dữ liệu}
\begin{itemize}
  \item Kiến trúc Kimball: bus matrix, conformed dimension, data mart theo quy trình nghiệp vụ \cite{kimball2013}.
  \item Kiến trúc Inmon: kho dữ liệu doanh nghiệp (3NF) và data mart phụ thuộc \cite{inmon2005}.
  \item Kiến trúc lai, vai trò của staging và ODS; so sánh ưu nhược điểm.
  \item Các lớp dữ liệu: nguồn, staging, ODS, kho, data mart, BI (liên hệ kiến trúc nhóm chọn ở mục 3.3.2).
\end{itemize}

\section{Mô hình dữ liệu đa chiều}
\begin{itemize}
  \item Fact, dimension, measure, grain; lược đồ sao, bông tuyết, chòm sao (constellation).
  \item Ba loại bảng fact: transaction, periodic snapshot, accumulating snapshot \cite{kimball2013}.
  \item Khóa thay thế, dòng Unknown, degenerate dimension, conformed dimension, junk dimension, role-playing dimension.
  \item Slowly changing dimension: loại 1, 2, 3 và khi nào dùng.
  \item Phân cấp (hierarchy) và cách dùng trong roll-up / drill-down.
\end{itemize}

\section{Quy trình ETL}
\begin{itemize}
  \item Extract, Transform, Load; nạp đầy đủ và nạp tăng dần (incremental), watermark, upsert.
  \item Làm sạch dữ liệu, kiểm soát chất lượng, ghi nhận dòng lỗi.
  \item Công cụ ETL phổ biến và lựa chọn của nhóm (Python điều phối, biến đổi bằng SQL procedure).
\end{itemize}

\section{OLAP: MOLAP, ROLAP, HOLAP}
\begin{itemize}
  \item Các thao tác OLAP: roll-up, drill-down, slice, dice, pivot \cite{chaudhuri1997,codd1993}.
  \item \textbf{So sánh MOLAP / ROLAP / HOLAP} (lưu trữ, tốc độ truy vấn, khả năng mở rộng, chi phí xử lý khối, độ tươi của dữ liệu, công cụ điển hình): nhóm lập bảng so sánh và trích nguồn.
  \item \textbf{Vì sao nhóm chọn ROLAP}: dùng PostgreSQL (không có khối đa chiều như SSAS), dữ liệu cỡ vài trăm nghìn dòng fact nên SQL trên lược đồ sao trả lời trong vòng một giây, kho luôn cập nhật sau mỗi lần nạp tăng dần mà không phải xử lý lại khối, Power BI đóng vai trò lớp ngữ nghĩa; đổi lại cần materialized view cho truy vấn nặng (liên hệ mục 3.4.4 và 3.5.1).
\end{itemize}

\section{Data mart và kho dữ liệu trong kinh doanh}
\begin{itemize}
  \item Khái niệm data mart, độc lập và phụ thuộc; tổng hợp sẵn bằng view / materialized view.
  \item Ứng dụng kho dữ liệu trong bán lẻ, thương mại điện tử, quản lý đơn hàng (giáo trình chương 7).
\end{itemize}
"""

CH2 = r"""\todo{Chương 2 chỉ có khung: nhóm tự viết văn bản từ các ý chính bên dưới và trích nguồn đã đọc; các mục tương ứng nội dung môn học (chương 6, 8).}

\section{Tổng quan về kinh doanh thông minh}
\begin{itemize}
  \item Khái niệm BI, vòng đời từ dữ liệu đến quyết định; BI và DW bổ trợ nhau \cite{kimball2013}.
  \item Các cấp phân tích: mô tả, chẩn đoán, dự đoán, đề xuất; phạm vi bài tập (mô tả và chẩn đoán).
\end{itemize}

\section{Kiến trúc và công cụ BI}
\begin{itemize}
  \item Các thành phần: nguồn dữ liệu, kho / data mart, mô hình ngữ nghĩa, báo cáo và dashboard, phân phối.
  \item So sánh các công cụ phổ biến (Power BI, Tableau, Qlik) và lý do chọn Power BI \cite{powerbi_docs}.
  \item Chế độ Import so với DirectQuery; Publish to web và các lưu ý về chia sẻ dữ liệu.
\end{itemize}

\section{KPI và đo lường hiệu quả}
\begin{itemize}
  \item KPI, chỉ số dẫn dắt và chỉ số kết quả; tiêu chí SMART; cây KPI.
  \item Liên hệ KPI của bài toán: GMV, AOV, tỷ lệ giao đúng hạn, điểm review, tỷ lệ chuyển đổi MQL sang seller (mục 3.3.5).
\end{itemize}

\section{Trực quan hóa dữ liệu và thiết kế dashboard}
\begin{itemize}
  \item Nguyên tắc chọn biểu đồ theo mục đích (so sánh, xu hướng, cấu thành, phân bố, quan hệ, bản đồ).
  \item Nguyên tắc bố cục, màu sắc, định dạng có điều kiện, slicer và drill-down; các loại dashboard (theo thời gian, OLAP, vận hành, thống kê).
\end{itemize}

\section{Mô hình ngữ nghĩa và ngôn ngữ DAX}
\begin{itemize}
  \item Bảng, quan hệ, cardinality, role-playing date và \code{USERELATIONSHIP}; ngữ cảnh bộ lọc và ngữ cảnh hàng \cite{dax_docs}.
  \item Measure so với cột tính toán; time intelligence (MoM, YoY).
\end{itemize}

\section{Xu hướng}
\begin{itemize}
  \item BI tự phục vụ, BI nhúng, tích hợp AI; dữ liệu lớn (giáo trình chương 8).
\end{itemize}
"""


def build_chapters() -> dict[str, str]:
    d: dict[str, str] = {}
    d["00-bia"], d["00-loi-mo-dau"], d["00-danh-gia-thanh-vien"], d["00-tu-danh-gia"], d["00-viet-tat"] = COVER, FOREWORD, RATING, SELFEVAL, ABBR
    d["01-tong-quan-dw"], d["02-tong-quan-bi"] = CH1, CH2

    d["3-1-gioi-thieu"] = f"""Olist là doanh nghiệp kết nối người bán nhỏ với các sàn thương mại điện tử lớn ở Brazil. Bài tập lớn xây dựng kho dữ liệu cho chủ đề \\textbf{{quản lý đơn hàng}} (Order Management) trên bộ dữ liệu công khai Brazilian E-Commerce \\cite{{olist_ecommerce}}, tích hợp thêm bộ Marketing Funnel \\cite{{olist_marketing}} để phân tích cả quá trình thu hút người bán. Hai bộ dữ liệu được nối qua mã người bán (\\code{{seller\\_id}}), nên kho trả lời được câu hỏi xuyên quy trình: \\emph{{người bán đến từ kênh marketing nào thì bán được nhiều và giao đúng hạn hơn}}.

\\todo{{Viết 2--3 câu về mục tiêu và phạm vi bài toán theo cách của nhóm; thêm 1 đoạn giới thiệu Olist từ nguồn công khai (trích dẫn nguồn đã đọc).}}

\\paragraph{{Các nhóm câu hỏi phân tích chính.}}
\\begin{{itemize}}
  \\item \\textbf{{Bán hàng}}: doanh thu (GMV), số đơn, giá trị đơn trung bình theo thời gian, danh mục, vùng; tăng trưởng và quy luật 80/20.
  \\item \\textbf{{Xử lý đơn}}: mỗi chặng (duyệt, bàn giao vận chuyển, giao) mất bao lâu, tỷ lệ giao trễ và hủy, vùng nào chậm.
  \\item \\textbf{{Thanh toán}}: cơ cấu hình thức thanh toán, số kỳ trả góp.
  \\item \\textbf{{Trải nghiệm khách}}: giao trễ ảnh hưởng điểm đánh giá thế nào, khách có quay lại không.
  \\item \\textbf{{Người bán}}: seller nào doanh thu cao nhưng hay trễ.
  \\item \\textbf{{Thu hút người bán}}: tỷ lệ chuyển đổi từ khách tiềm năng (MQL) sang seller theo kênh, thời gian chốt deal, thời gian đến đơn đầu tiên.
\\end{{itemize}}

\\paragraph{{Mô hình kinh doanh (bản nháp).}} Hình \\ref{{fig:bmc}} tóm tắt mô hình kinh doanh của Olist theo 9 ô của Business Model Canvas, suy luận từ dữ liệu và mô tả công khai.
{fig("3-2-3_business_model_canvas.png", "Business Model Canvas của Olist (bản nháp)", "fig:bmc", "0.98")}
\\todo{{Nhóm kiểm tra và sửa Business Model Canvas, đặc biệt ô \\emph{{dòng doanh thu}} và \\emph{{đối tác chính}}: chỉ có suy luận, cần dẫn chứng từ nguồn công khai về Olist (dữ liệu chỉ có giá hàng và phí vận chuyển, không có doanh thu của Olist). Vẽ lại bằng draw.io nếu muốn.}}
"""

    d["3-2-1-quy-trinh"] = f"""\\subsection{{Quy trình nghiệp vụ}}
Chu trình xử lý đơn hàng gồm các bước: khách đặt hàng và thanh toán, sàn duyệt thanh toán, người bán chuẩn bị và bàn giao cho đơn vị vận chuyển, vận chuyển giao hàng, khách nhận hàng và đánh giá; đơn có thể bị hủy hoặc không khả dụng. Mỗi mốc là một cột thời gian trong dữ liệu nguồn (Hình \\ref{{fig:bpmn-don}}); các ô vàng đánh dấu nơi \\textbf{{kho dữ liệu thu thập}} để phân tích.
{fig("3-2-1_bpmn_don_hang.png", "Quy trình xử lý đơn hàng và các điểm thu thập dữ liệu của kho (bản nháp)", "fig:bpmn-don", "1.0")}
Quy trình thu hút người bán đi từ khách tiềm năng (MQL) để lại thông tin trên trang đích, đội sales (SDR, SR) tư vấn và chốt thương vụ, người bán ký hợp đồng và nhận đơn đầu tiên (Hình \\ref{{fig:bpmn-seller}}). Trong dữ liệu: 8.000 MQL, 842 thương vụ được chốt (10,5\\%), trong đó 380 seller có đơn (45,1\\% số đã chốt).
{fig("3-2-2_bpmn_thu_hut_seller.png", "Quy trình thu hút người bán và các điểm thu thập dữ liệu của kho (bản nháp)", "fig:bpmn-seller", "1.0")}
Các hoạt động của doanh nghiệp được tổ chức thành cây nghiệp vụ ở Hình \\ref{{fig:cay-nghiep-vu}}.
{fig("3-2-5_cay_nghiep_vu.png", "Cây nghiệp vụ của Olist (bản nháp)", "fig:cay-nghiep-vu", "0.8")}
\\todo{{Nhóm đọc, sửa cho đúng cách hiểu nghiệp vụ và vẽ lại BPMN bằng draw.io (đúng ký hiệu BPMN), giữ nguyên các điểm thu thập dữ liệu. Nguồn nháp: huong-dan/05-nghiep-vu-nhap.md.}}

\\begin{{table}}[htbp]\\centering\\small\\caption{{Các mốc của quy trình đơn hàng và nơi kho lưu}}\\label{{tab:moc-don}}
\\begin{{tabular}}{{p{{3.2cm}}p{{4.6cm}}p{{3.4cm}}p{{3.6cm}}}}\\toprule
\\textbf{{Bước}} & \\textbf{{Cột nguồn}} & \\textbf{{Nơi kho lưu}} & \\textbf{{Phân tích được}}\\\\\\midrule
Đặt hàng, thanh toán & \\code{{order\\_purchase\\_timestamp}}, \\code{{payment\\_type}} & \\code{{purchase\\_ts}}, \\code{{fact\\_payment}} & số đơn, cơ cấu thanh toán\\\\
Duyệt & \\code{{order\\_approved\\_at}} & \\code{{approval\\_hours}} & tốc độ duyệt\\\\
Bàn giao vận chuyển & \\code{{order\\_delivered\\_carrier\\_date}} & \\code{{handling\\_days}} & seller xử lý nhanh hay chậm\\\\
Giao khách & \\code{{order\\_delivered\\_customer\\_date}} & \\code{{transit\\_days}}, \\code{{lead\\_days}}, \\code{{delay\\_days}} & vận chuyển, đúng hạn\\\\
Đánh giá & \\code{{review\\_score}} & \\code{{fact\\_review}} & điểm trung bình, ảnh hưởng của trễ\\\\\\bottomrule
\\end{{tabular}}\\end{{table}}
"""

    d["3-2-2-yeu-cau"] = f"""\\subsection{{Yêu cầu phân tích}}
Các yêu cầu phân tích được tổ chức theo chủ điểm (bán hàng, xử lý đơn, thanh toán, trải nghiệm khách, seller, thu hút seller) và theo các khía cạnh cần quan tâm (thời gian, địa lý, sản phẩm, kênh thu hút); Hình \\ref{{fig:cay-yeu-cau}} là cây yêu cầu phân tích.
{fig("3-2-6_cay_yeu_cau_phan_tich.png", "Cây yêu cầu phân tích (bản nháp)", "fig:cay-yeu-cau", "0.85")}
\\begin{{table}}[htbp]\\centering\\small\\caption{{Chủ điểm phân tích và câu hỏi chính}}\\label{{tab:chu-diem}}
\\begin{{tabular}}{{p{{2.8cm}}p{{8cm}}p{{3.6cm}}}}\\toprule
\\textbf{{Chủ điểm}} & \\textbf{{Câu hỏi}} & \\textbf{{Khía cạnh}}\\\\\\midrule
Bán hàng & GMV, số đơn, AOV theo thời gian / danh mục / vùng; tăng trưởng MoM, YoY; quy luật 80/20 & thời gian, sản phẩm, địa lý\\\\
Xử lý đơn & Mỗi chặng mất bao lâu; tỷ lệ trễ, hủy; vùng nào chậm; ngày hứa giao so với thực tế & thời gian, địa lý, trạng thái\\\\
Thanh toán & Cơ cấu hình thức thanh toán, số kỳ trả góp & thời gian, hình thức\\\\
Trải nghiệm khách & Giao trễ ảnh hưởng điểm review thế nào; khách có quay lại không & mức trễ, khách\\\\
Seller & Seller nào doanh thu cao nhưng hay trễ & seller, thời gian\\\\
Thu hút seller & Tỷ lệ chuyển đổi MQL sang seller theo kênh; thời gian chốt; GMV theo kênh & kênh, thời gian, phân khúc\\\\\\bottomrule
\\end{{tabular}}\\end{{table}}
\\todo{{Nhóm bổ sung hoặc điều chỉnh yêu cầu phân tích theo cách trình bày trên lớp (theo chủ điểm, khía cạnh, dạng cây).}}
"""

    d["3-2-3-he-thong-du-lieu"] = f"""\\subsection{{Hệ thống dữ liệu}}
{draft("handoff/2026-11-05-P0.md", "Đoạn nháp cho báo cáo (mục 3.2.3")}

\\input{{tables/src_tables}}
Hai hệ thống nguồn được mô phỏng thành hai schema riêng (\\code{{oltp}} và \\code{{crm}}) trong PostgreSQL; sau khi nạp đủ, kho có số dòng từng lớp như Bảng \\ref{{tab:layers}}.
\\input{{tables/layers}}
\\paragraph{{Tần suất và khối lượng cập nhật.}} Dữ liệu Kaggle là ảnh chụp tĩnh nên nhóm mô phỏng cập nhật theo tháng: nạp ban đầu đến 31/12/2017 (45.430 đơn) rồi 11 đợt hằng tháng (01--11/2018), tổng 286.144 bản ghi mới (xem mục 3.4.3).
\\todo{{Nhóm nêu rõ tần suất cập nhật giả định của hệ thống thực (ví dụ đơn hàng cập nhật liên tục, kho cập nhật hằng ngày) và dung lượng mỗi lần cập nhật.}}
"""

    d["3-2-4-erd-oltp"] = f"""\\subsection{{ERD hệ thống OLTP và luồng dữ liệu}}
{draft("handoff/2026-11-05-P0.md", "Đoạn nháp cho báo cáo (mục 3.2.4")}

{fig("3-2-4_erd_oltp.png", "ERD hai hệ thống nguồn: bán hàng (oltp) và marketing (crm)", "fig:erd-oltp", "1.0")}
\\todo{{Yêu cầu của môn: trên ERD OLTP \\textbf{{gạch chân các trường dữ liệu sẽ dùng sang OLAP}} và ghi chú \\textbf{{mapping}} tương ứng. Vẽ lại ERD bằng draw.io từ hình nháp, gạch chân các cột dùng và ghi chú (bảng mapping đầy đủ ở Phụ lục C, nguồn docs/mapping\\_oltp\\_olap.md). Thêm sơ đồ luồng dữ liệu (data flow) từ nguồn đến kho.}}
"""

    d["3-3-1-kham-pha"] = f"""\\subsection{{Khám phá dữ liệu}}
{draft("handoff/2026-11-05-P1.md", "Đoạn nháp cho báo cáo (mục 3.3.1")}

{fig("3-3-1_data_quality.png", "Các lỗi dữ liệu đo được, xếp theo tỷ lệ", "fig:dq", "0.95")}
{fig("3-3-1_null_heatmap.png", "Tỷ lệ ô rỗng của các cột", "fig:null", "0.95")}
{fig("3-3-1_distributions_numeric.png", "Phân bố các biến số (giá, phí vận chuyển, thanh toán, lead time, số ngày trễ)", "fig:dist", "0.95")}
{fig("3-3-1_pareto_category.png", "Quy luật 80/20 theo danh mục sản phẩm (Pareto)", "fig:pareto-cat", "0.85")}
{fig("3-3-1_pareto_seller.png", "Quy luật 80/20 theo seller (Pareto)", "fig:pareto-seller", "0.85")}
{fig("3-3-1_orders_per_month.png", "Số đơn theo tháng (2016 thưa, 09--10/2018 gần như trống)", "fig:orders-month", "0.85")}
{fig("3-3-1_delay_vs_review.png", "Điểm đánh giá theo mức trễ giao hàng", "fig:delay-review", "0.85")}
{fig("3-3-1_lead_time_by_region.png", "Lead time theo vùng", "fig:lead-region", "0.85")}
{fig("3-3-1_late_rate_by_state.png", "Tỷ lệ giao trễ theo bang", "fig:late-state", "0.85")}
{fig("3-3-1_correlation_matrix.png", "Ma trận tương quan Spearman giữa các biến số", "fig:corr", "0.85")}
{fig("3-3-1_funnel_seller_overlap.png", "Seller của funnel có và không có đơn hàng", "fig:funnel-overlap", "0.8")}
{fig("3-3-1_funnel_win_rate_by_origin.png", "Tỷ lệ chốt deal theo kênh (origin)", "fig:funnel-origin", "0.85")}
\\input{{tables/review_delay}}
\\input{{tables/funnel_channel}}
\\todo{{Chọn các hình cần đưa vào thân báo cáo (các hình còn lại chuyển sang phụ lục); thêm hình \\texttt{{3-3-1\\_funnel\\_*}} khác nếu cần. Bổ sung kết quả Excel Data Analysis ToolPak (thống kê mô tả, tương quan) theo hướng dẫn handoff/excel-toolpak-guide.md.}}
"""

    d["3-3-2-kien-truc"] = f"""\\subsection{{Kiến trúc kho dữ liệu}}
Kiến trúc gồm sáu lớp (Hình \\ref{{fig:pipeline}}): hai hệ thống nguồn, staging, ODS, kho dữ liệu hình sao, các data mart theo chủ đề và Power BI; lớp giám sát \\code{{etl\\_log}} ghi lại mỗi lần chạy, dòng bị loại và kết quả kiểm thử. Python điều phối pipeline, mọi biến đổi chính viết bằng SQL procedure trên PostgreSQL. Vai trò từng lớp: staging giữ bản sao thô để nạp tăng dần và đối soát; ODS làm sạch và chuẩn hóa mà không xóa dữ liệu; kho tổ chức theo mô hình chiều với khóa thay thế và SCD; data mart tổng hợp sẵn cho từng nhóm dashboard.
{fig("3-4-1_pipeline.png", "Kiến trúc các lớp và pipeline ETL (bản nháp tự động)", "fig:pipeline", "1.0")}
Số bảng và số dòng của từng lớp ở trạng thái cuối được thống kê ở Bảng \\ref{{tab:layers}} (mục 3.2.3).
\\todo{{Yêu cầu của môn: sơ đồ kiến trúc \\textbf{{có logo công nghệ ở mỗi phần}} (PostgreSQL, Python, Power BI, GitHub...), nêu các hoạt động ETL, dimension, fact và tên các dashboard. Vẽ lại bằng draw.io từ các file docs/diagrams/kien-truc-cac-lop.drawio và pipeline-etl.drawio, xuất PNG vào report/figures/.}}
"""

    d["3-3-3-ods"] = f"""\\subsection{{ODS và phân tích dữ liệu nguồn}}
{draft("handoff/2026-11-05-P2.md", "Đoạn nháp cho báo cáo (mục 3.3.3")}

\\input{{tables/dq_errors}}
\\todo{{Nhóm bổ sung phần ``Giới thiệu về ODS'' theo giáo trình (khái niệm, vị trí giữa nguồn và kho, khác biệt với kho) và liên hệ với Chương 1.}}
"""

    d["3-3-4-thiet-ke-kho"] = f"""\\subsection{{Thiết kế kho dữ liệu}}
\\subsubsection*{{Bảng chiều (dimension)}}
{draft("handoff/2026-11-05-P3.md", "Đoạn nháp cho báo cáo (mục 3.3.4")}

\\input{{tables/dims}}
\\subsubsection*{{Bảng fact và mô hình vật lý}}
{draft("handoff/2026-11-05-P4.md", "Đoạn nháp cho báo cáo (mục 3.3.4")}

\\input{{tables/facts}}
{fig("3-3-4_erd_dw.png", "Mô hình dữ liệu của kho (data model; bản nháp tự động)", "fig:erd-dw", "1.0")}
{fig("3-3-4_constellation.png", "Mô hình constellation theo data mart: fact (cam), dimension (xanh) (bản nháp tự động)", "fig:constellation", "0.9")}
\\todo{{Yêu cầu của môn: \\textbf{{data model logic và vật lý}} của staging / data mart / kho, dùng màu phân biệt fact (cam) và dimension (xanh), nhóm các vùng liên quan bằng khung. Vẽ lại bằng draw.io từ docs/diagrams/data-model-theo-mart.drawio. Thêm: hệ thống chiều khái niệm (phân cấp từng dimension), thống kê số bản ghi từng dimension (đã có Bảng \\ref{{tab:dims}}), phân nhóm các dimension.}}
\\todo{{Thêm bus matrix (docs/DW\\_DESIGN.md mục 4) và sơ đồ phân cấp: ngày, địa lý, sản phẩm, seller, khách (SCD2).}}
"""

    d["3-3-5-kpi"] = f"""\\subsection{{KPI và cây phân tích}}
Bảng \\ref{{tab:kpi}} liệt kê các KPI chính; mỗi KPI được định nghĩa một lần bằng công thức DAX (Phụ lục A) và đối chiếu với giá trị tính bằng SQL trên kho. \\textbf{{GMV}} chỉ tính đơn không thuộc nhóm Failed (hủy hoặc không khả dụng), vì vậy nhỏ hơn tổng giá hàng của mọi đơn (13,49 triệu so với 13,59 triệu BRL). KPI \\emph{{ngày hứa giao so với ngày giao thực tế}} so sánh số ngày Olist hứa với số ngày giao thực tế: ngày dự kiến rất rộng rãi (trung bình 24,4 ngày) trong khi giao thực tế trung bình 12,6 ngày, nên tỷ lệ ``đúng hạn'' cao (93,2\\%) chưa phản ánh trải nghiệm.
\\input{{tables/kpi}}
Mỗi dashboard có một cây phân tích đi từ mục tiêu đến câu hỏi, chỉ số và chiều (Hình \\ref{{fig:cay-d1}} đến \\ref{{fig:cay-d7}}).
{fig("3-2-7_cay_phan_tich_D1.png", "Cây phân tích dashboard D1 -- Executive Overview", "fig:cay-d1", "0.75")}
{fig("3-2-7_cay_phan_tich_D2.png", "Cây phân tích dashboard D2 -- Sales và Product", "fig:cay-d2", "0.75")}
{fig("3-2-7_cay_phan_tich_D3.png", "Cây phân tích dashboard D3 -- Order Fulfillment", "fig:cay-d3", "0.75")}
{fig("3-2-7_cay_phan_tich_D4.png", "Cây phân tích dashboard D4 -- Geography và Freight", "fig:cay-d4", "0.75")}
{fig("3-2-7_cay_phan_tich_D5.png", "Cây phân tích dashboard D5 -- Customer Experience", "fig:cay-d5", "0.75")}
{fig("3-2-7_cay_phan_tich_D6.png", "Cây phân tích dashboard D6 -- Seller Acquisition", "fig:cay-d6", "0.75")}
{fig("3-2-7_cay_phan_tich_D7.png", "Cây phân tích dashboard D7 -- Data Quality và ETL Monitor", "fig:cay-d7", "0.75")}
\\todo{{Nhóm vẽ lại các cây phân tích bằng draw.io nếu muốn thống nhất kiểu trình bày; thêm bảng KPI đầy đủ theo định nghĩa trong docs/DW\\_DESIGN.md mục 9 (công thức, nguồn, đơn vị).}}
"""

    d["3-4-1-moi-truong"] = f"""\\subsection{{Môi trường và mã nguồn}}
Hệ thống chạy trên PostgreSQL 18 (cài trực tiếp, không dùng Docker và không dùng PostGIS), Python 3.11 (pandas, SQLAlchemy, psycopg2) cho điều phối và nạp dữ liệu, SQL procedure (PL/pgSQL) cho biến đổi, Power BI Desktop cho dashboard và Git/GitHub để quản lý mã nguồn (nhánh theo từng phase, nhánh \\code{{main}} luôn chạy được). Cấu trúc thư mục: \\code{{sql/}} (DDL, procedure, view, kiểm thử), \\code{{etl/}} (gói Python), \\code{{scripts/}} (xuất dữ liệu, báo cáo), \\code{{powerbi/}} (đặc tả mô hình và DAX), \\code{{handoff/}} và \\code{{huong-dan/}} (tài liệu). Toàn bộ dự án dựng lại từ đầu bằng một lệnh \\code{{python scripts/rebuild\\_all.py --drop}} và cho kết quả giống hệt lần trước (Bảng \\ref{{tab:rebuild}}).
\\input{{tables/rebuild}}
\\todo{{Thêm bảng công nghệ (logo, phiên bản, vai trò), hình cấu trúc thư mục repo, và hướng dẫn cài đặt rút gọn (README.md). Nêu quy ước đặt tên và quy trình làm việc nhóm với Git.}}
"""

    d["3-4-2-staging-ods"] = f"""\\subsection{{Staging và ODS: làm sạch dữ liệu}}
{draft("handoff/2026-11-05-P2.md", "Đoạn nháp cho báo cáo (mục 3.3.3")}

Các quy tắc làm sạch và số dòng bị ảnh hưởng được tổng hợp ở Bảng \\ref{{tab:dq-errors}} (mục 3.3.3). Mỗi dòng bị loại được ghi vào \\code{{etl\\_log.rejected\\_rows}} cùng lý do; không có dòng nào bị bỏ âm thầm.
\\todo{{Thêm sơ đồ luồng staging $\\rightarrow$ ODS (các job ETL) và bảng ``nguồn $\\rightarrow$ đích $\\rightarrow$ phép biến đổi'' (Phụ lục C).}}
"""

    d["3-4-3-doi-soat-tang-dan"] = f"""\\subsection{{Đối soát trước và sau ETL, nạp tăng dần}}
Mẫu dữ liệu trước và sau làm sạch được đối chiếu ở các hình dưới đây (nguồn: handoff/before-after-samples.md).
{fig("3-4-3_before_after_orders.png", "Trước và sau ETL: bảng đơn hàng", "fig:ba-orders", "0.95")}
{fig("3-4-3_before_after_products.png", "Trước và sau ETL: bảng sản phẩm", "fig:ba-products", "0.95")}
{fig("3-4-3_before_after_sellers.png", "Trước và sau ETL: bảng seller", "fig:ba-sellers", "0.95")}
{fig("3-4-3_before_after_geolocation.png", "Trước và sau ETL: bảng toạ độ địa lý", "fig:ba-geo", "0.95")}
{fig("3-4-3_before_after_mql.png", "Trước và sau ETL: bảng MQL", "fig:ba-mql", "0.95")}
{fig("3-4-3_before_after_closed_deals.png", "Trước và sau ETL: bảng deal đã chốt", "fig:ba-deals", "0.95")}
\\paragraph{{Nạp tăng dần.}}
{draft("handoff/2026-11-05-P5.md", "Đoạn nháp cho báo cáo (mục 3.4")}

\\input{{tables/increments}}
\\paragraph{{Thử lại dòng mồ côi.}} Dòng con bị loại vì chưa có dòng cha (ví dụ deal đến trước MQL) được thử lại ở các đợt sau và biến mất khỏi danh sách loại khi đã nạp. \\textbf{{Lưu ý trung thực}}: cơ chế này mới được chứng minh bằng kịch bản kiểm thử; trong 11 đợt thật không có dòng mồ côi nào xảy ra vì nguồn luôn nạp dòng cha trước.
\\todo{{Thêm sơ đồ data pipeline hoặc ETL jobs (có logo công nghệ); ví dụ trước/sau cho thêm bảng nếu giảng viên yêu cầu; kết quả so sánh incremental với full: 16/16 bảng khớp (handoff/2026-11-05-P5.md).}}
"""

    d["3-4-4-mart-olap"] = f"""\\subsection{{Data mart và các thao tác OLAP}}
{draft("handoff/2026-11-05-P6.md", "Đoạn nháp cho báo cáo (mục 3.4.4")}

\\input{{tables/marts}}
\\paragraph{{Roll-up và pivot trên dữ liệu thật.}} Bảng \\ref{{tab:olap-rollup}} là kết quả roll-up bằng \\code{{ROLLUP}} (SQL ở Phụ lục B); Bảng \\ref{{tab:olap-pivot}} là pivot GMV theo vùng và năm bằng tổng có điều kiện \\code{{FILTER}}.
\\input{{tables/olap_rollup}}
\\input{{tables/olap_pivot}}
\\todo{{Chọn thêm các truy vấn drill-down, slice, dice từ handoff/olap-examples.md; viết đoạn so sánh ROLAP và MOLAP trong bối cảnh bài toán (liên hệ mục 1.6).}}
"""

    # 3.4.5 dashboards
    dash = ["\\subsection{Dashboard}", "Hệ thống có 7 dashboard Power BI dựng trên cùng một mô hình ngữ nghĩa (32 quan hệ, role-playing date, phân cấp thời gian, địa lý, sản phẩm, seller): ba dashboard theo dòng thời gian và phân tích (D1, D2, D6), hai dashboard OLAP/địa lý (D2, D4), hai dashboard vận hành và thống kê (D3, D5) và một dashboard vận hành hệ thống (D7). Cách dựng từng bước: powerbi/model.md.", "\\todo{Thống kê số dashboard theo loại (theo dòng thời gian, OLAP, vận hành, thống kê/dự án) và liệt kê các loại biểu đồ đã dùng (yêu cầu của môn: đa dạng biểu đồ, slicer, định dạng có điều kiện, DAX tăng trưởng và cảnh báo).}"]
    for k in ["D1", "D2", "D3", "D4", "D5", "D6", "D7"]:
        f = f"huong-dan/dashboards/{k}.md"
        title = re.search(r"^# (.+)", (ROOT / f).read_text(encoding="utf-8"), re.M).group(1)
        goal = section(f, "1")
        qs = [re.sub(r"^- ", "", l) for l in section(f, "2").splitlines() if l.startswith("- ")]
        ins = [re.sub(r"^\d+\. ", "", l) for l in section(f, "10").splitlines() if re.match(r"^\d+\. ", l)]
        dash += [f"\\subsubsection*{{{md2tex(title)}}}", md2tex(goal), "\\paragraph{Câu hỏi dashboard trả lời.}", itemize(qs),
                 f"\\khunganh{{[Ảnh chụp dashboard {k} sau khi dựng trên Power BI]}}{{Dashboard {k}}}",
                 f"\\todo{{Chèn ảnh chụp dashboard {k} (xuất PNG từ Power BI) thay cho khung trống; mô tả bố cục, slicer, định dạng có điều kiện đã dùng (xem huong-dan/dashboards/{k}.md mục 4--8).}}",
                 "\\paragraph{Nhận xét (gợi ý từ số liệu kho; \\textbf{nhóm xác nhận lại sau khi dựng và đối chiếu số}).}", itemize(ins, f"Nhóm kiểm tra các nhận xét của {k} trên dashboard thực tế rồi viết lại bằng lời của nhóm.")]
    d["3-4-5-dashboard"] = "\n\n".join(dash) + "\n"

    d["3-5-1-hieu-nang"] = f"""\\subsection{{Hiệu năng truy vấn}}
{draft("handoff/2026-11-05-P7-perf.md", "Đoạn nháp cho báo cáo (mục 3.5.1")}

\\input{{tables/benchmark}}
{fig("3-5-1_benchmark.png", "Thời gian thực thi trung bình: oltp so với dw, có và không có index khóa ngoại, view thường so với materialized view (thang logarit)", "fig:benchmark", "1.0")}
\\paragraph{{Nhận xét.}} Trên dữ liệu khoảng 100 nghìn đơn, lược đồ hình sao chỉ nhanh hơn lược đồ chuẩn hóa của hệ thống nguồn từ 1,0 đến 1,6 lần ở các truy vấn quét toàn bộ, và scorecard seller không nhanh hơn; lợi ích chính của mô hình chiều là \\textbf{{truy vấn đơn giản và số liệu nhất quán}} (một định nghĩa cho mỗi KPI). Tốc độ đến chủ yếu từ hai kỹ thuật: \\textbf{{materialized view}} (đọc dưới 1 ms thay vì 150--750 ms) và \\textbf{{chỉ mục}} trên khóa ngoại (truy vấn chọn lọc một seller nhanh gấp khoảng 9 lần). Cần lưu ý đo trên một máy, một người dùng, dữ liệu còn nhỏ.
\\todo{{Nhóm xác nhận số đo trên máy của mình nếu chạy lại (python scripts/benchmark.py); thêm giải thích kế hoạch thực thi (EXPLAIN) cho một truy vấn nếu muốn.}}
"""

    d["3-5-2-dia-ly"] = f"""\\subsection{{Cơ sở dữ liệu địa lý}}
{draft("handoff/2026-11-05-P7-geo.md", "Đoạn nháp cho báo cáo (mục 3.5.2")}

\\input{{tables/distance}}
{fig("3-5-2_distance_vs_freight.png", "Khoảng cách seller -- khách và phí vận chuyển", "fig:dist-freight", "1.0")}
{fig("3-5-2_distance_vs_leadtime.png", "Khoảng cách seller -- khách, lead time và tỷ lệ trễ", "fig:dist-lead", "1.0")}
\\begin{{table}}[htbp]\\centering\\small\\caption{{So sánh haversine bằng SQL thuần và PostGIS}}\\label{{tab:haversine-postgis}}
\\begin{{tabular}}{{p{{2.6cm}}p{{6cm}}p{{6cm}}}}\\toprule
 & \\textbf{{Haversine SQL thuần}} & \\textbf{{PostGIS}}\\\\\\midrule
Dữ liệu & hai cột vĩ độ, kinh độ kiểu số thực & kiểu \\code{{geometry}} hoặc \\code{{geography}}\\\\
Khoảng cách & công thức cầu, sai số tối đa khoảng 0,5\\% & có tính trên ellipsoid chính xác hơn\\\\
Chỉ mục & chỉ B-tree, không hỗ trợ truy vấn bán kính hay láng giềng gần nhất & chỉ mục không gian GiST (cây R)\\\\
Phép toán & khoảng cách điểm--điểm & đa giác, giao cắt, diện tích, hệ toạ độ\\\\
Chi phí & không cần cài thêm & cần cài extension\\\\\\bottomrule
\\end{{tabular}}\\end{{table}}
\\todo{{Nhóm bổ sung phần lý thuyết cơ sở dữ liệu địa lý (mô hình vector/raster, kiểu dữ liệu không gian, chỉ mục không gian) từ tài liệu PostGIS \\cite{{postgis_docs}} và công thức haversine \\cite{{sinnott1984}}; thêm bản đồ bong bóng từ dashboard D4 khi dựng xong. Hàm dw.haversine\\_km: Phụ lục B.}}
"""

    d["04-ket-luan"] = r"""\section{Kết quả đạt được}
\todo{Viết lại bằng lời của nhóm. Gợi ý các ý đã có số liệu: kho dữ liệu hình sao với 10 bảng chiều và 6 bảng fact thuộc cả ba loại; hai hệ thống nguồn và 1,56 triệu dòng; pipeline chạy lại từ đầu bằng một lệnh trong khoảng 7 phút, kết quả nạp tăng dần trùng khớp nạp đầy đủ (16/16 bảng); 133 phép kiểm thử đạt; 4 data mart, 17 view; 7 dashboard; các phát hiện chính (giao trễ làm điểm review giảm từ 4,29 xuống 1,70; funnel chỉ nối được 45,1\% deal với seller có đơn; khoảng cách seller--khách làm phí vận chuyển và lead time tăng).}

\section{Bài học kinh nghiệm}
\begin{itemize}
  \item Làm sạch không đồng nghĩa với xóa: gắn cờ lỗi và ghi dòng bị loại giúp kiểm toán được dữ liệu.
  \item Chọn grain trước khi thiết kế fact; accumulating snapshot hợp với quy trình có nhiều mốc.
  \item Định nghĩa KPI một lần (GMV loại đơn Failed) và đối chiếu bằng SQL để tránh số lệch giữa các dashboard.
  \item Mô hình chiều không phải lúc nào cũng nhanh hơn trên dữ liệu nhỏ; giá trị nằm ở sự nhất quán, còn tốc độ đến từ materialized view và chỉ mục.
  \item Kiểm thử tái lập (dựng lại toàn bộ từ đầu) phát hiện sớm sự phụ thuộc ngầm giữa các bước.
\end{itemize}
\todo{Nhóm bổ sung bài học về làm việc nhóm, phân công, công cụ (Git, Power BI) và khó khăn thực tế.}

\section{Hạn chế và hướng phát triển}
\begin{itemize}
  \item Nạp tăng dần chỉ mô phỏng bản ghi mới với trạng thái cuối, chưa có đơn đổi trạng thái giữa chừng; cơ chế thử lại dòng mồ côi mới được chứng minh bằng kịch bản kiểm thử, chưa phát sinh từ dữ liệu thật.
  \item Toạ độ theo mã bưu chính (không phải địa chỉ); haversine là khoảng cách đường chim bay.
  \item Dữ liệu 2016 và cuối 2018 rất thưa; chỉ 45,1\% deal đã chốt có đơn nên so sánh theo kênh có cỡ mẫu nhỏ.
  \item Hướng phát triển: CDC thật với trạng thái trung gian, lịch chạy tự động, PostGIS cho truy vấn không gian, phân vùng bảng fact, đo hiệu năng nhiều người dùng.
\end{itemize}
\todo{Chỉnh danh sách hạn chế theo thực tế sau khi dựng dashboard.}
"""

    d["phu-luc-dax"] = "Thư viện measure DAX của mô hình (nguồn: powerbi/measures.md; sinh bằng scripts/export\\_latex.py). Dán lần lượt vào bảng \\code{\_Measures} trong Power BI.\n\\input{tables/dax}\n"
    d["phu-luc-sql"] = r"""\section*{SQL tiêu biểu}
Các đoạn mã dưới đây được cắt từ thư mục \code{sql/} của dự án (sinh bằng scripts/export\_latex.py).

\subsection*{ODS: nạp deal đã chốt và thử lại dòng mồ côi}
\lstinputlisting[language=SQLvi]{code/ods_take_orphans.sql}
\lstinputlisting[language=SQLvi]{code/ods_load_closed_deals.sql}

\subsection*{SCD loại 2: dim\_customer}
\lstinputlisting[language=SQLvi]{code/scd2_dim_customer.sql}

\subsection*{Accumulating snapshot: fact\_order\_fulfillment (rút gọn)}
\lstinputlisting[language=SQLvi]{code/fact_order_fulfillment.sql}

\subsection*{OLAP: roll-up và pivot}
\lstinputlisting[language=SQLvi]{code/olap_rollup.sql}
\lstinputlisting[language=SQLvi]{code/olap_pivot.sql}

\subsection*{Địa lý: hàm haversine}
\lstinputlisting[language=SQLvi]{code/haversine.sql}
"""
    return d


BIB = r"""% Tài liệu tham khảo. Mọi mục là nguồn có thật. Mục đánh dấu [GỢI Ý] chưa được nhóm dùng trực tiếp: nhóm đọc và kiểm tra thông tin (nhà xuất bản, trang) trước khi trích dẫn.

@book{kimball2013,
  author    = {Kimball, Ralph and Ross, Margy},
  title     = {The Data Warehouse Toolkit: The Definitive Guide to Dimensional Modeling},
  edition   = {3},
  publisher = {John Wiley \& Sons},
  year      = {2013}
}

@book{inmon2005,
  author    = {Inmon, William H.},
  title     = {Building the Data Warehouse},
  edition   = {4},
  publisher = {John Wiley \& Sons},
  year      = {2005},
  note      = {[GỢI Ý] đọc và kiểm tra trước khi trích}
}

@article{chaudhuri1997,
  author  = {Chaudhuri, Surajit and Dayal, Umeshwar},
  title   = {An Overview of Data Warehousing and {OLAP} Technology},
  journal = {ACM SIGMOD Record},
  volume  = {26},
  number  = {1},
  pages   = {65--74},
  year    = {1997},
  note    = {[GỢI Ý] đọc và kiểm tra trước khi trích}
}

@techreport{codd1993,
  author      = {Codd, E. F. and Codd, S. B. and Salley, C. T.},
  title       = {Providing {OLAP} (On-line Analytical Processing) to User-Analysts: An {IT} Mandate},
  institution = {E. F. Codd \& Associates},
  year        = {1993},
  note        = {[GỢI Ý] đọc và kiểm tra trước khi trích}
}

@misc{olist_ecommerce,
  author       = {{Olist}},
  title        = {Brazilian E-Commerce Public Dataset by Olist},
  howpublished = {Kaggle},
  url          = {https://www.kaggle.com/datasets/olistbr/brazilian-ecommerce},
  note         = {Truy cập 2026}
}

@misc{olist_marketing,
  author       = {{Olist}},
  title        = {Marketing Funnel by Olist},
  howpublished = {Kaggle},
  url          = {https://www.kaggle.com/datasets/olistbr/marketing-funnel-olist},
  note         = {Truy cập 2026}
}

@manual{postgresql_docs,
  author       = {{PostgreSQL Global Development Group}},
  title        = {PostgreSQL 18 Documentation},
  url          = {https://www.postgresql.org/docs/18/},
  note         = {Materialized views, GROUPING SETS / ROLLUP / CUBE, PL/pgSQL, unaccent}
}

@manual{powerbi_docs,
  author       = {{Microsoft}},
  title        = {Power BI documentation},
  url          = {https://learn.microsoft.com/power-bi/},
  note         = {Truy cập 2026}
}

@manual{dax_docs,
  author       = {{Microsoft}},
  title        = {Data Analysis Expressions (DAX) reference},
  url          = {https://learn.microsoft.com/dax/},
  note         = {Truy cập 2026}
}

@manual{postgis_docs,
  author       = {{PostGIS Project Steering Committee}},
  title        = {PostGIS documentation},
  url          = {https://postgis.net/documentation/},
  note         = {Dùng để so sánh với haversine bằng SQL thuần}
}

@article{sinnott1984,
  author  = {Sinnott, Roger W.},
  title   = {Virtues of the Haversine},
  journal = {Sky and Telescope},
  volume  = {68},
  number  = {2},
  pages   = {159},
  year    = {1984}
}

@inproceedings{mckinney2010,
  author    = {McKinney, Wes},
  title     = {Data Structures for Statistical Computing in Python},
  booktitle = {Proceedings of the 9th Python in Science Conference},
  pages     = {56--61},
  year      = {2010}
}

@article{hunter2007,
  author  = {Hunter, John D.},
  title   = {Matplotlib: A 2D Graphics Environment},
  journal = {Computing in Science \& Engineering},
  volume  = {9},
  number  = {3},
  pages   = {90--95},
  year    = {2007}
}

@book{kimball2008,
  author    = {Kimball, Ralph and Ross, Margy and Thornthwaite, Warren and Mundy, Joy and Becker, Bob},
  title     = {The Data Warehouse Lifecycle Toolkit},
  edition   = {2},
  publisher = {John Wiley \& Sons},
  year      = {2008},
  note      = {[GỢI Ý] đọc và kiểm tra trước khi trích}
}
"""


def main() -> None:
    force = "--force" in sys.argv
    if CH.exists() and not force:
        raise SystemExit("report/chapters/ already exists: refusing to overwrite the team's text (use --force to regenerate the skeleton).")
    CH.mkdir(parents=True, exist_ok=True)
    (REP / "figures").mkdir(exist_ok=True)
    (REP / "main.tex").write_text(MAIN, encoding="utf-8")
    (REP / "preamble.tex").write_text(PREAMBLE, encoding="utf-8")
    (REP / "refs.bib").write_text(BIB, encoding="utf-8")
    for name, body in build_chapters().items():
        (CH / f"{name}.tex").write_text(body, encoding="utf-8")
    for p in (ROOT / "figures").glob("*.png"):
        shutil.copy2(p, REP / "figures" / p.name)
    print(f"written main.tex, preamble.tex, refs.bib, {len(list(CH.glob('*.tex')))} chapter files, {len(list((REP / 'figures').glob('*.png')))} figures")


if __name__ == "__main__":
    main()
