# 패션 커머스 커뮤니티 활동 기반 이탈 방지 분석

## 프로젝트 개요

패션 커머스 플랫폼에서 커뮤니티 활동(리뷰, 좋아요)이 유저 참여도 및 구매 전환에 미치는 영향을 분석, 이탈 징후 유저 대상 리텐션 트리거 시나리오를 제안.

무신사 랭킹 상위 300개 상품을 직접 크롤링하여 실데이터 기반 분석을 수행했다.

---

## 핵심 가설

커뮤니티 활동(리뷰, 좋아요)이 활발한 상품일수록 구매 전환율이 높고 유저 참여도가 높을 것이다.

---

## 분석 결과

### 상관관계 분석 (Spearman)

| 변수 쌍 | r | p-value | 해석 |
|--------|---|---------|------|
| CAS vs 좋아요수 | 0.996 | 0.0000 | 매우 강한 양의 상관관계 |
| CAS vs 리뷰수 | 0.219 | 0.0003 | 약한 양의 상관관계 |

### 세그먼트별 Kruskal-Wallis 검정

| 지표 | H | p-value | 결과 |
|------|---|---------|------|
| 좋아요수 | 162.87 | 0.0000 | 세그먼트 간 유의미한 차이 |
| 리뷰수 | 97.64 | 0.0000 | 세그먼트 간 유의미한 차이 |
| 평점 | 0.38 | 0.9452 | 유의미한 차이 없음 |

### 세그먼트별 기술통계

| 세그먼트 | 상품수 | 평균 좋아요수 | 평균 리뷰수 | 평균 가격 |
|---------|-------|------------|----------|---------|
| Super Fan Product | 33 | 762,424 | 7,081 | 51,064원 |
| Community Only | 27 | 557,778 | 96 | 138,067원 |
| Dormant | 173 | 101,548 | 1,408 | 168,594원 |
| Purchase Only | 67 | 41,340 | 1,989 | 100,760원 |

### 시각화

세그먼트별 커뮤니티 활동 분석
<img width="2386" height="744" alt="ltv_distribution" src="https://github.com/user-attachments/assets/9a4d16a4-772c-45a8-b7be-20d513701d38" />


---

## 핵심 인사이트

**1. Community Only가 핵심**

Community Only 세그먼트는 평균 좋아요수가 557,778개로 Super Fan의 73% 수준이지만,
평균 리뷰수는 96개로 Super Fan(7,081개)의 1.3%에 불과하다.
관심도는 높지만 구매 전환이 극히 낮은 그룹으로, 이 그룹을 Super Fan으로 전환하는 것이
가장 임팩트 있는 성장 전략이다.

**2. 평점은 세그먼트를 구분하지 못한다**

모든 세그먼트의 평균 평점이 4.8~4.9로 수렴하며 유의미한 차이가 없다(p=0.9452).
즉 평점은 이탈 예측 지표로 활용하기 어렵고, 리뷰수와 좋아요수가 더 유효한 지표다.

**3. Super Fan은 저가 상품에 집중된다**

Super Fan Product의 평균 가격(51,064원)이 다른 세그먼트 대비 현저히 낮다.
가격 접근성이 커뮤니티 활동 활성화에 기여하는 것으로 해석된다.

---

## Actionable Insight - 리텐션 트리거 시나리오

| 대상 세그먼트 | 이탈 징후 | 트리거 액션 | 예상 효과 |
|-------------|---------|-----------|---------|
| Super Fan | 좋아요수 2주 연속 감소 | 팔로잉 브랜드 신상 알림 + VIP 5% 쿠폰 | 재방문율 +15% |
| Community Only | 좋아요수 높은데 구매 0 | 찜한 상품 첫구매 무료배송 쿠폰 | 첫구매 전환 +8% |
| Purchase Only | 구매 주기 1.5배 초과 | 재입고 / 가격 인하 알림 | 재구매율 +12% |
| Dormant | 4주 이상 미활동 | 맞춤 큐레이션 + 복귀 쿠폰 10% | 복귀율 +5% |

---

## 분석 흐름

```
무신사 랭킹 크롤링 (Selenium)
         |
         v
전처리 및 CAS 산출 (pandas)
         |
         v
세그먼트 분류 (CAS x popularity 기준)
         |
         v
상관관계 분석 (Spearman / Kruskal-Wallis)
         |
         v
리텐션 트리거 시나리오 설계
```

---

## 기술 스택

Tech Stack
- **Language**: Python 3.10, SQL
- **Web Scraping**: Selenium, BeautifulSoup4
- **Data Analysis**: Pandas, NumPy, SciPy
- **Visualization**: Matplotlib, Seaborn
- **Database**: SQLite
---

## 실행 방법

```bash
# 1. 패키지 설치
pip install -r requirements.txt

# 2. 크롤링 (약 30분 소요)
cd 03_분석코드/python
python 01_musinsa_crawler.py

# 3. 전처리
python 02_preprocess.py

# 4. 분석 및 시각화
python 03_community_ltv_analysis.py
```

---

## 폴더 구조

```
fashion-commerce-churn-prevention/
├── README.md
├── requirements.txt
├── .gitignore
├── data/                          
├── 01_문제정의/
│   └── problem_definition.md
├── 02_데이터설계/
│   └── data_schema.md
├── 03_분석코드/
│   ├── python/
│   │   ├── 01_musinsa_crawler.py
│   │   ├── 02_preprocess.py
│   │   └── 03_community_ltv_analysis.py
│   └── sql/
│       ├── 01_user_segment_classification.sql
│       └── 02_churn_risk_score.sql
├── 04_시각화/
│   ├── ltv_distribution.png
│   └── visualization_guide.md
└── 05_액션플랜/
    └── retention_trigger_scenario.md
```

