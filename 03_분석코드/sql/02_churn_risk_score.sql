-- 목적: 이탈 위험 상품 식별 (CAS 낮고 좋아요수 높은 상품)

-- CAS 하위 50% 이면서 좋아요수 상위 50% → 이탈 위험 상품
WITH thresholds AS (
    SELECT
        AVG(CAS_score)  AS avg_cas,
        AVG(좋아요수)    AS avg_like
    FROM products
)

SELECT
    p.상품명,
    p.브랜드,
    p.CAS_score,
    p.좋아요수,
    p.리뷰수,
    p.가격,
    p.segment,
    -- Churn Risk Score: CAS 낮을수록, 
    -- 좋아요수 높을수록 위험
    ROUND(
        (1.0 - p.CAS_score / 100.0) * 0.6
        + (CAST(p.좋아요수 AS FLOAT) / (SELECT MAX(좋아요수) FROM products)) * 0.4
    , 3) AS churn_risk_score,
    CASE
        WHEN (1.0 - p.CAS_score / 100.0) * 0.6
           + (CAST(p.좋아요수 AS FLOAT) / (SELECT MAX(좋아요수) FROM products)) * 0.4 >= 0.7
        THEN 'HIGH_RISK'
        WHEN (1.0 - p.CAS_score / 100.0) * 0.6
           + (CAST(p.좋아요수 AS FLOAT) / (SELECT MAX(좋아요수) FROM products)) * 0.4 >= 0.4
        THEN 'MID_RISK'
        ELSE 'LOW_RISK'
    END AS risk_level
FROM products p
ORDER BY churn_risk_score DESC
LIMIT 20;