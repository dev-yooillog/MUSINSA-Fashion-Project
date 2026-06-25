import pandas as pd
import numpy as np
import re

df = pd.read_csv("../../data/musinsa_raw.csv")
print(f"원본 데이터: {df.shape[0]}행 x {df.shape[1]}열")
print(f"컬럼 목록: {list(df.columns)}\n")

# 숫자형 변환 
def clean_number(x):
    """'37만' -> 370000 / '3.2천' -> 3200 / '1,234' -> 1234"""
    if pd.isna(x):
        return np.nan
    x = str(x).strip()
    if "만" in x:
        num = re.sub(r"[^0-9.]", "", x.replace("만", ""))
        return int(float(num) * 10000) if num else np.nan
    if "천" in x:
        num = re.sub(r"[^0-9.]", "", x.replace("천", ""))
        return int(float(num) * 1000) if num else np.nan
    # 일반 숫자
    cleaned = re.sub(r"[^0-9]", "", x)
    return int(cleaned) if cleaned else np.nan

for col in ["리뷰수", "좋아요수"]:
    if col in df.columns:
        df[col] = df[col].apply(clean_number)

# 가격: 첫번째 숫자만 (할인 전 가격 제거)
if "가격" in df.columns:
    df["가격"] = df["가격"].apply(
        lambda x: clean_number(str(x).split("\n")[0]) if pd.notna(x) else np.nan
    )

# 평점
if "평점" in df.columns:
    df["평점"] = df["평점"].apply(
        lambda x: float(re.sub(r"[^0-9.]", "", str(x).split("\n")[0]))
        if pd.notna(x) and re.sub(r"[^0-9.]", "", str(x)) else np.nan
    )

print("[1] 숫자형 변환 완료")
print(df[["리뷰수", "좋아요수", "가격", "평점"]].describe())
print()

# 결측치 확인
print("[2] 결측치 현황")
print(df[["리뷰수", "좋아요수", "가격", "평점"]].isnull().sum())
print()

# Community Activity Score (CAS) 산출 
"""
CAS 구성 (조회수/구매수 없으므로 리뷰수 + 좋아요수 기준):
  리뷰수   x 4  (구매 후 참여, 가중치 최대)
  좋아요수  x 2  (관심 표현)
-> Min-Max 정규화 (0~100)
"""
df["CAS_raw"] = (
    df["리뷰수"].fillna(0) * 4 +
    df["좋아요수"].fillna(0) * 2
)

cas_min, cas_max = df["CAS_raw"].min(), df["CAS_raw"].max()
df["CAS_score"] = ((df["CAS_raw"] - cas_min) / (cas_max - cas_min) * 100).round(2)

print("[3] CAS_score 분포")
print(df["CAS_score"].describe())
print()

# 인기도 점수 (Popularity Score) 산출
"""
구매수/조회수 없으므로 리뷰수 + 평점 기준
"""
df["popularity_raw"] = (
    df["리뷰수"].fillna(0) * 3 +
    df["평점"].fillna(0) * 1000
)

p_min, p_max = df["popularity_raw"].min(), df["popularity_raw"].max()
df["popularity_score"] = ((df["popularity_raw"] - p_min) / (p_max - p_min) * 100).round(2)

print("[4] popularity_score 분포")
print(df["popularity_score"].describe())
print()

# 세그먼트 분류
cas_p80 = df["CAS_score"].quantile(0.8)
cas_p50 = df["CAS_score"].quantile(0.5)
pop_p50 = df["popularity_score"].quantile(0.5)

print(f"[5] 세그먼트 기준값")
print(f"    CAS 80percentile : {cas_p80:.2f}")
print(f"    CAS 50percentile : {cas_p50:.2f}")
print(f"    POP 50percentile : {pop_p50:.2f}\n")

def classify_segment(row):
    cas = row["CAS_score"]
    pop = row["popularity_score"]
    if cas >= cas_p80 and pop >= pop_p50:
        return "Super Fan Product"
    elif cas >= cas_p80 and pop < pop_p50:
        return "Community Only"
    elif cas < cas_p50 and pop >= pop_p50:
        return "Purchase Only"
    else:
        return "Dormant"

df["segment"] = df.apply(classify_segment, axis=1)

print("[5] 세그먼트 분포")
print(df["segment"].value_counts())
print()

# 리뷰 텍스트 합치기
review_cols = [f"리뷰{i}" for i in range(1, 11) if f"리뷰{i}" in df.columns]
df["리뷰_전체"] = df[review_cols].fillna("").apply(
    lambda row: " ".join([r for r in row if r]), axis=1
)
df["리뷰_개수_실제"] = df[review_cols].notna().sum(axis=1)

analysis_cols = [
    "링크", "상품ID", "상품명", "브랜드", "가격",
    "평점", "리뷰수", "좋아요수",
    "CAS_score", "popularity_score", "segment",
    "리뷰_전체", "리뷰_개수_실제"
]

df_out = df[[c for c in analysis_cols if c in df.columns]]
df_out.to_csv("../../data/musinsa_processed.csv", index=False, encoding="utf-8-sig")

print(f"전처리 -> data/musinsa_processed.csv")
print(f"최종 데이터: {df_out.shape[0]}행 x {df_out.shape[1]}열")
print()
print(df_out[["상품명", "브랜드", "가격", "리뷰수", "좋아요수", "CAS_score", "segment"]].head())