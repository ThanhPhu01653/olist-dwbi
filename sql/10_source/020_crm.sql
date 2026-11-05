-- setup: required
-- Source system 2: CRM / marketing (Kaggle olistbr/marketing-funnel-olist).
-- Column names are kept exactly as in the CSV files.

CREATE TABLE IF NOT EXISTS crm.mql (
    mql_id              char(32) PRIMARY KEY,
    first_contact_date  date NOT NULL,
    landing_page_id     char(32),
    origin              text                      -- NULL for some leads (source defect)
);

-- closed_deals.seller_id is deliberately NOT a foreign key to oltp.sellers:
-- CRM and sales are two independent systems and cannot enforce referential integrity across each other.
-- Only part of the sellers won in the CRM ever appear in the sales system; the link is made in the DW
-- through the conformed dimension dw.dim_seller.
-- seller_id is UNIQUE inside the CRM (one deal per seller), mql_id is the 1-to-0..1 link to mql.
CREATE TABLE IF NOT EXISTS crm.closed_deals (
    mql_id                         char(32) PRIMARY KEY REFERENCES crm.mql (mql_id),
    seller_id                      char(32) NOT NULL UNIQUE,
    sdr_id                         char(32),
    sr_id                          char(32),
    won_date                       timestamp NOT NULL,
    business_segment               text,
    lead_type                      text,
    lead_behaviour_profile         text,
    has_company                    boolean,
    has_gtin                       boolean,
    average_stock                  text,
    business_type                  text,
    declared_product_catalog_size  numeric(12,1),
    declared_monthly_revenue       numeric(14,2)
);

COMMENT ON SCHEMA crm IS 'Simulated CRM / marketing system (Olist Marketing Funnel)';
COMMENT ON COLUMN crm.closed_deals.seller_id IS 'Joins to oltp.sellers.seller_id logically only; no FK across systems';
