-- Q1. 각 세그먼트에서 좋아요수가 가장 높은 상품을 1개씩 조회하시오.
--      (상품명, 브랜드, 세그먼트, 좋아요수 출력)
SELECT 상품명, 브랜드, segment, 좋아요수
FROM products
WHERE (segment, 좋아요수) IN (
    SELECT segment, MAX(좋아요수)
    FROM products
    GROUP BY segment
)
ORDER BY 좋아요수 DESC;


-- Q2. 전체 평균 CAS_score보다 높은 세그먼트만 조회하고,
--      해당 세그먼트의 평균 좋아요수를 구하시오.
SELECT
    segment,
    ROUND(AVG(CAS_score), 2) AS 평균_CAS,
    ROUND(AVG(좋아요수), 0) AS 평균_좋아요수
FROM products
GROUP BY segment
HAVING AVG(CAS_score) > (SELECT AVG(CAS_score) FROM products)
ORDER BY 평균_CAS DESC;


-- Q3. 브랜드별 상품 수가 3개 이상인 브랜드 중
--      평균 CAS_score 상위 5개 브랜드를 조회하시오.
SELECT
    브랜드,
    COUNT(*) AS 상품수,
    ROUND(AVG(CAS_score), 2) AS 평균_CAS,
    ROUND(AVG(좋아요수), 0) AS 평균_좋아요수
FROM products
GROUP BY 브랜드
HAVING COUNT(*) >= 3
ORDER BY 평균_CAS DESC
LIMIT 5;


-- Q4. CAS_score를 기준으로 상위 20% / 중간 60% / 하위 20% 구간으로
--      나누고 각 구간의 평균 리뷰수를 구하시오.
WITH ranked AS (
    SELECT
        상품명,
        CAS_score,
        리뷰수,
        NTILE(5) OVER (ORDER BY CAS_score DESC) AS tile
    FROM products
)
SELECT
    CASE
        WHEN tile = 1 THEN '상위 20%'
        WHEN tile IN (2, 3, 4) THEN '중간 60%'
        ELSE '하위 20%'
    END AS CAS_구간,
    COUNT(*) AS 상품수,
    ROUND(AVG(리뷰수), 0) AS 평균_리뷰수,
    ROUND(AVG(CAS_score), 2) AS 평균_CAS
FROM ranked
GROUP BY CAS_구간
ORDER BY 평균_CAS DESC;


-- Q5. 좋아요수 대비 리뷰수 비율(리뷰 전환율)을 계산하고
--      비율이 높은 상품 상위 10개를 조회하시오.
--      (좋아요수가 0인 상품 제외)
SELECT
    상품명,
    브랜드,
    좋아요수,
    리뷰수,
    ROUND(CAST(리뷰수 AS FLOAT) / 좋아요수 * 100, 2) AS 리뷰전환율_pct,
    segment
FROM products
WHERE 좋아요수 > 0 AND 리뷰수 IS NOT NULL
ORDER BY 리뷰전환율_pct DESC
LIMIT 10;


-- Q6. 세그먼트별로 가격 구간(5만원 미만 / 5~10만원 / 10~20만원 / 20만원 이상)을
--      나누고 각 조합의 상품 수를 피벗 형태로 조회하시오.
SELECT
    segment,
    COUNT(CASE WHEN 가격 < 50000 THEN 1 END) AS '5만원_미만',
    COUNT(CASE WHEN 가격 >= 50000 AND 가격 < 100000 THEN 1 END) AS '5~10만원',
    COUNT(CASE WHEN 가격 >= 100000 AND 가격 < 200000 THEN 1 END) AS '10~20만원',
    COUNT(CASE WHEN 가격 >= 200000 THEN 1 END) AS '20만원_이상'
FROM products
GROUP BY segment
ORDER BY segment;


-- Q7. 각 상품의 CAS_score가 자신이 속한 브랜드 평균 CAS_score보다
--      높은지 낮은지 여부와 그 차이를 구하시오. (상위 20개 출력)
WITH brand_avg AS (
    SELECT
        브랜드,
        AVG(CAS_score) AS 브랜드_평균_CAS
    FROM products
    GROUP BY 브랜드
)
SELECT
    p.상품명,
    p.브랜드,
    ROUND(p.CAS_score, 2) AS 상품_CAS,
    ROUND(b.브랜드_평균_CAS, 2) AS 브랜드_평균_CAS,
    ROUND(p.CAS_score - b.브랜드_평균_CAS, 2) AS CAS_차이,
    CASE
        WHEN p.CAS_score >= b.브랜드_평균_CAS THEN '평균_이상'
        ELSE '평균_미만'
    END AS 브랜드내_위치
FROM products p
JOIN brand_avg b ON p.브랜드 = b.브랜드
ORDER BY ABS(p.CAS_score - b.브랜드_평균_CAS) DESC
LIMIT 20;


-- Q8. 이탈 위험 상품을 정의하고 세그먼트별 이탈 위험 비율을 구하시오.
--      이탈 위험 정의: CAS_score 하위 50% AND 좋아요수 상위 50%
--      (관심은 높은데 커뮤니티 참여가 낮은 상품)
WITH thresholds AS (
    SELECT
        (SELECT AVG(CAS_score) FROM products) AS avg_cas,
        (SELECT AVG(좋아요수)  FROM products) AS avg_like
)
SELECT
    segment,
    COUNT(*) AS 전체_상품수,
    COUNT(CASE
        WHEN p.CAS_score < t.avg_cas AND p.좋아요수 >= t.avg_like THEN 1
    END) AS 이탈위험_상품수,
    ROUND(
        COUNT(CASE WHEN p.CAS_score < t.avg_cas AND p.좋아요수 >= t.avg_like THEN 1 END)
        * 100.0 / COUNT(*), 1
    ) AS 이탈위험_비율_pct
FROM products p, thresholds t
GROUP BY segment
ORDER BY 이탈위험_비율_pct DESC;


-- Q9. 누적 좋아요수 기준으로 상위 50%에 해당하는 브랜드 목록과
--      해당 브랜드들의 전체 좋아요수 합계를 구하시오.
WITH brand_total AS (
    SELECT
        브랜드,
        SUM(좋아요수) AS 브랜드_총_좋아요수,
        SUM(SUM(좋아요수)) OVER () AS 전체_총_좋아요수
    FROM products
    GROUP BY 브랜드
),
brand_ranked AS (
    SELECT
        브랜드,
        브랜드_총_좋아요수,
        전체_총_좋아요수,
        SUM(브랜드_총_좋아요수) OVER (ORDER BY 브랜드_총_좋아요수 DESC) AS 누적_좋아요수
    FROM brand_total
)
SELECT
    브랜드,
    브랜드_총_좋아요수,
    ROUND(브랜드_총_좋아요수 * 100.0 / 전체_총_좋아요수, 1) AS 점유율_pct,
    누적_좋아요수
FROM brand_ranked
WHERE 누적_좋아요수 <= 전체_총_좋아요수 * 0.5
ORDER BY 브랜드_총_좋아요수 DESC;


-- Q10. 각 세그먼트의 CAS_score 분포를 요약하시오.
--      (최솟값, 1사분위, 중앙값, 3사분위, 최댓값)
--      SQLite는 PERCENTILE 미지원 → NTILE로 근사치 계산
WITH ranked AS (
    SELECT
        segment,
        CAS_score,
        NTILE(4) OVER (PARTITION BY segment ORDER BY CAS_score) AS quartile
    FROM products
)
SELECT
    segment,
    ROUND(MIN(CAS_score), 2) AS 최솟값,
    ROUND(AVG(CASE WHEN quartile = 1 THEN CAS_score END), 2) AS Q1_근사,
    ROUND(AVG(CASE WHEN quartile IN (2,3) THEN CAS_score END), 2) AS 중앙값_근사,
    ROUND(AVG(CASE WHEN quartile = 4 THEN CAS_score END), 2) AS Q3_근사,
    ROUND(MAX(CAS_score), 2) AS 최댓값
FROM ranked
GROUP BY segment
ORDER BY 최댓값 DESC;