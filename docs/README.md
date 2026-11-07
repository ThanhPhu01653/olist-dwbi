# docs/ – đặc tả, sơ đồ và mapping

| File | Công dụng |
| --- | --- |
| [`DW_DESIGN.md`](DW_DESIGN.md) | Đặc tả schema đầy đủ của kho (nguồn sự thật duy nhất): bảng, cột, bus matrix, KPI, kiểm thử; kèm nhật ký quyết định thiết kế theo ngày |
| [`mapping.csv`](mapping.csv) | Bảng ánh xạ nguồn → đích → phép biến đổi (dạng CSV, dùng làm phụ lục báo cáo); sinh bằng `scripts/gen_mapping.py` |
| [`mapping_oltp_olap.md`](mapping_oltp_olap.md) | Cùng nội dung với `mapping.csv` nhưng đọc được trên GitHub, nhóm theo từng dimension và fact; sinh tự động |
| [`erd_oltp.mmd`](erd_oltp.mmd) | Sơ đồ Mermaid ERD hai hệ thống nguồn (`oltp`, `crm`) |
| [`erd_dw.mmd`](erd_dw.mmd) | Sơ đồ Mermaid ERD kho dữ liệu (dim và fact, có cột) |
| [`erd_dw_marts.mmd`](erd_dw_marts.mmd) | Sơ đồ Mermaid constellation: fact và dim theo từng data mart |
| [`pipeline.mmd`](pipeline.mmd) | Sơ đồ Mermaid pipeline ETL (nguồn → staging → ODS → kho → mart → Power BI) |
| [`category_group_draft.csv`](category_group_draft.csv) | Bản nháp ánh xạ danh mục sản phẩm → nhóm ngành hàng (bản chốt nằm ở `seeds/category_group.csv`) |
| [`diagrams/`](diagrams/) | Ba sơ đồ draw.io chỉnh được: `kien-truc-cac-lop`, `data-model-theo-mart`, `pipeline-etl` |

Các file `.mmd` dán vào <https://mermaid.live> để ra hình; hình đã render nằm ở [`../figures/`](../figures/).
Tài liệu môn học cục bộ (PDF, XLSX trong thư mục này) không được commit.
