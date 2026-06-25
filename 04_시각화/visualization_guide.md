# 시각화 가이드

## 생성되는 차트 목록 (community_ltv_analysis.py 실행 시)

### 1. 세그먼트별 구매수 분포 (박스플롯)
- x축: 세그먼트 4종
- y축: 구매수
- 목적: 세그먼트 간 구매 행동 차이 시각화

### 2. CAS vs 구매수 산점도
- x축: CAS_score
- y축: 구매수
- 색상: 세그먼트별
- 목적: 상관관계 및 Spearman r 값 표시

### 3. 세그먼트별 평균 구매수 바차트
- x축: 세그먼트
- y축: 평균 구매수
- 목적: 세그먼트 간 LTV 차이 한눈에 비교

## 실행 방법
cd 03_분석코드/python
python community_ltv_analysis.py
→ 결과 이미지: 04_시각화/ltv_distribution.png 자동 저장