-- Q01. 전체 상품 수를 구하시오.
SELECT COUNT(*) AS 전체_상품수
FROM products;


-- Q02. 브랜드별 상품 수를 구하고, 상품 수가 많은 순으로 정렬하시오.
SELECT
    브랜드,
    COUNT(*) AS 상품수
FROM products
GROUP BY 브랜드
ORDER BY 상품수 DESC;


-- Q03. 가격이 50,000원 이하인 상품의 상품명, 브랜드, 가격을 조회하시오.
SELECT 상품명, 브랜드, 가격
FROM products
WHERE 가격 <= 50000
ORDER BY 가격 ASC;


-- Q04. 평점이 4.9 이상인 상품의 수를 구하시오.
SELECT COUNT(*) AS 고평점_상품수
FROM products
WHERE 평점 >= 4.9;


-- Q05. 상품 가격의 최솟값, 최댓값, 평균값을 구하시오.
SELECT
    MIN(가격) AS 최저가,
    MAX(가격) AS 최고가,
    ROUND(AVG(가격), 0) AS 평균가
FROM products;


-- Q06. 세그먼트별 상품 수와 평균 가격을 구하시오.
SELECT
    segment,
    COUNT(*) AS 상품수,
    ROUND(AVG(가격), 0) AS 평균_가격
FROM products
GROUP BY segment
ORDER BY 평균_가격 DESC;


-- Q07. 좋아요수 상위 10개 상품의 상품명, 브랜드, 좋아요수를 조회하시오.
SELECT 상품명, 브랜드, 좋아요수
FROM products
ORDER BY 좋아요수 DESC
LIMIT 10;


-- Q08. 리뷰수가 1000개 이상인 브랜드를 조회하고,
--      해당 브랜드의 평균 리뷰수를 구하시오.
SELECT
    브랜드,
    COUNT(*) AS 상품수,
    ROUND(AVG(리뷰수), 0) AS 평균_리뷰수
FROM products
WHERE 리뷰수 >= 1000
GROUP BY 브랜드
ORDER BY 평균_리뷰수 DESC;


-- Q09. CAS_score가 NULL이 아닌 상품 중
--      CAS_score 평균보다 높은 상품의 수를 구하시오.
SELECT COUNT(*) AS 평균_초과_상품수
FROM products
WHERE CAS_score > (SELECT AVG(CAS_score) FROM products);


-- Q10. 브랜드명에 '단독'이 포함된 상품의 수와 평균 CAS_score를 구하시오.
SELECT
    COUNT(*) AS 단독상품수,
    ROUND(AVG(CAS_score), 2) AS 평균_CAS
FROM products
WHERE 브랜드 LIKE '%단독%';