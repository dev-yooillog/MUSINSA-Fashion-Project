import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from scipy import stats
import warnings
warnings.filterwarnings("ignore")

plt.rcParams["font.family"] = "Malgun Gothic"  
plt.rcParams["axes.unicode_minus"] = False

df = pd.read_csv("../../data/musinsa_processed.csv")
print(f"데이터 로드: {df.shape[0]}행 x {df.shape[1]}열\n")

# CAS vs 좋아요수 상관관계 (Spearman)
df_corr = df[["CAS_score", "좋아요수", "리뷰수", "평점"]].dropna()
corr_like, p_like = stats.spearmanr(df_corr["CAS_score"], df_corr["좋아요수"])
corr_review, p_review = stats.spearmanr(df_corr["CAS_score"], df_corr["리뷰수"])

print("[1] CAS 상관분석 결과")
print(f"    CAS vs 좋아요수 : r = {corr_like:.3f}, p = {p_like:.4f}")
print(f"    CAS vs 리뷰수   : r = {corr_review:.3f}, p = {p_review:.4f}")
print()

# 세그먼트별 차이 검정 (Kruskal-Wallis)
for col in ["좋아요수", "리뷰수", "평점"]:
    groups = [
        df[df["segment"] == s][col].dropna().values
        for s in df["segment"].unique()
    ]
    groups = [g for g in groups if len(g) > 0]
    if len(groups) >= 2:
        H, p_kw = stats.kruskal(*groups)
        print(f"[2] {col} Kruskal-Wallis : H = {H:.2f}, p = {p_kw:.4f}", end="  ")
        print("-> 유의미한 차이" if p_kw < 0.05 else "-> 유의미하지 않음")
print()

# 세그먼트별 기술통계
summary = df.groupby("segment").agg(
    상품수=("상품명", "count"),
    평균_CAS=("CAS_score", "mean"),
    평균_좋아요수=("좋아요수", "mean"),
    평균_리뷰수=("리뷰수", "mean"),
    평균_평점=("평점", "mean"),
    평균_가격=("가격", "mean"),
).round(1)
summary = summary.sort_values("평균_좋아요수", ascending=False)
print(summary.to_string())
print()

COLORS = {
    "Super Fan Product": "#1E4D8C",
    "Community Only":    "#2E75B6",
    "Purchase Only":     "#70AD47",
    "Dormant":           "#BFBFBF",
}
order = ["Super Fan Product", "Purchase Only", "Community Only", "Dormant"]
order = [s for s in order if s in df["segment"].unique()]

fig, axes = plt.subplots(1, 3, figsize=(16, 5))
fig.suptitle("패션 커머스 커뮤니티 활동 분석", fontsize=14, fontweight="bold")

# 4-1. 세그먼트별 좋아요수 박스플롯
bp_data = [df[df["segment"] == s]["좋아요수"].dropna() for s in order]
bp = axes[0].boxplot(bp_data, labels=order, patch_artist=True)
for patch, seg in zip(bp["boxes"], order):
    patch.set_facecolor(COLORS.get(seg, "#CCCCCC"))
    patch.set_alpha(0.7)
axes[0].set_title("세그먼트별 좋아요수 분포")
axes[0].set_ylabel("좋아요수")
axes[0].tick_params(axis="x", rotation=15)

# 4-2. CAS vs 좋아요수 산점도
for seg, color in COLORS.items():
    if seg not in df["segment"].unique():
        continue
    sub = df[df["segment"] == seg].dropna(subset=["CAS_score", "좋아요수"])
    axes[1].scatter(sub["CAS_score"], sub["좋아요수"],
                    c=color, alpha=0.5, s=20, label=seg)
axes[1].set_title(f"CAS vs 좋아요수 (r={corr_like:.2f})")
axes[1].set_xlabel("CAS_score")
axes[1].set_ylabel("좋아요수")
axes[1].legend(fontsize=8)

# 4-3. 세그먼트별 평균 좋아요수 바차트
seg_means = df.groupby("segment")["좋아요수"].mean().reindex(order)
bars = axes[2].bar(
    range(len(order)),
    seg_means.values,
    color=[COLORS.get(s, "#CCCCCC") for s in order],
    alpha=0.8
)
axes[2].set_title("세그먼트별 평균 좋아요수")
axes[2].set_xticks(range(len(order)))
axes[2].set_xticklabels(order, rotation=15)
axes[2].set_ylabel("평균 좋아요수")
for bar, val in zip(bars, seg_means.values):
    if not np.isnan(val):
        axes[2].text(
            bar.get_x() + bar.get_width() / 2,
            bar.get_height() + 1000,
            f"{int(val):,}",
            ha="center", va="bottom", fontsize=9
        )

plt.tight_layout()
plt.savefig("../../04_시각화/ltv_distribution.png", dpi=150, bbox_inches="tight")
print("[4] 시각화 저장 완료 -> 04_시각화/ltv_distribution.png")
plt.show()

# 요약
print()
print("[결론 및 액션 아이템]")
print(f"1. CAS vs 좋아요수 Spearman r = {corr_like:.2f}")
print(f"   -> 커뮤니티 활동과 참여도 {'상관관계 확인' if corr_like > 0.3 else '상관관계 미확인'}")
print(f"2. CAS vs 리뷰수 Spearman r = {corr_review:.2f}")
community_like = df[df["segment"] == "Community Only"]["좋아요수"].mean()
superfan_like = df[df["segment"] == "Super Fan Product"]["좋아요수"].mean()
print(f"3. Super Fan 평균 좋아요수    : {superfan_like:,.0f}")
print(f"   Community Only 평균 좋아요수: {community_like:,.0f}")
print(f"   -> Community Only 구매 전환이 핵심 성장 레버")