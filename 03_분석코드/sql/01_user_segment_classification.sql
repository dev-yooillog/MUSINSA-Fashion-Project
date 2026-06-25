-- 목적: CAS 기반 상품 세그먼트 분류

-- 세그먼트별 기술통계
SELECT
    segment,
    COUNT(*) AS 상품수,
    ROUND(AVG(CAS_score), 2) AS 평균_CAS,
    ROUND(AVG(좋아요수), 0) AS 평균_좋아요수,
    ROUND(AVG(리뷰수), 0) AS 평균_리뷰수,
    ROUND(AVG(가격), 0) AS 평균_가격,
    ROUND(AVG(평점), 2) AS 평균_평점
FROM products
GROUP BY segment
ORDER BY 평균_좋아요수 DESC