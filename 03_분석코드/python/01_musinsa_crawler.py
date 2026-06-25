import time
import pandas as pd
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from tqdm import trange
import warnings
warnings.filterwarnings("ignore")

# 설정 
TARGET_COUNT = 300
SLEEP = 2.0
OUTPUT_PATH = "../../data/musinsa_raw.csv"

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/120.0.0.0 Safari/537.36"
    )
}

RANKING_URL = "https://www.musinsa.com/main/musinsa/ranking?skip_bf=Y"


#상품 링크 수집 (Selenium 스크롤)
def get_product_links(driver, target_count: int) -> list[str]:
    print(f"[STEP 1] 상품 링크 수집 시작 (목표: {target_count}개)")
    driver.get(RANKING_URL)
    time.sleep(3)

    links = []
    scroll_count = 0

    while len(links) < target_count:
        soup = BeautifulSoup(driver.page_source, "html.parser")
        items = soup.select("a[href*='/products/']")

        for item in items:
            href = item.get("href", "")
            if "/products/" in href:
                full_url = href if href.startswith("http") else f"https://www.musinsa.com{href}"
                if full_url not in links:
                    links.append(full_url)

        print(f"  스크롤 {scroll_count + 1}회 (누적: {len(links)}개)")

        if len(links) >= target_count:
            break

        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        time.sleep(2)
        scroll_count += 1

        if scroll_count > 50:
            print("  스크롤 한계 도달")
            break

    links = list(dict.fromkeys(links))[:target_count]
    print(f"  링크 수집 완료: {len(links)}개\n")
    return links


#상품 상세 데이터 수집 
def parse_product(driver, url: str) -> dict:
    driver.get(url)
    time.sleep(SLEEP)

    soup = BeautifulSoup(driver.page_source, "html.parser")
    product_id = url.rstrip("/").split("/products/")[-1].split("?")[0]
    data = {"링크": url, "상품ID": product_id}

    def safe_select(selector):
        el = soup.select_one(selector)
        return el.get_text(strip=True) if el else None

    def safe_find(css_selector):
        try:
            return driver.find_element(By.CSS_SELECTOR, css_selector).text.strip()
        except:
            return None

    # 상품명
    data["상품명"] = safe_select('[class*="GoodsName"]')

    # 브랜드
    data["브랜드"] = safe_select('[class*="BrandName"]')

    # 가격 (할인가 우선, 없으면 정가)
    price_raw = safe_select('[class*="Price__DiscountWrap"]') or safe_select('[class*="Price"]')
    data["가격"] = price_raw

    # 좋아요수
    data["좋아요수"] = safe_select('[class*="Like"]')

    # 평점
    data["평점"] = safe_select('[class*="ReviewStarScore"]')

    # 리뷰수 (ContentsTab__Count 첫번째 값)
    try:
        counts = soup.select('[class*="ContentsTab__Count"]')
        data["리뷰수"] = counts[0].get_text(strip=True) if counts else None
    except:
        data["리뷰수"] = None

    # 리뷰 텍스트 (최대 10개)
    try:
        reviews = soup.select('[class*="ReviewImageContentSection"]')
        for j in range(10):
            data[f"리뷰{j + 1}"] = reviews[j].get_text(strip=True) if j < len(reviews) else None
    except:
        for j in range(10):
            data[f"리뷰{j + 1}"] = None

    return data


#메인 실행 
def main():
    options = Options()
    # options.add_argument("--headless")  # 디버깅 시 주석 처리
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument(f"user-agent={HEADERS['User-Agent']}")
    driver = webdriver.Chrome(options=options)

    try:
        links = get_product_links(driver, TARGET_COUNT)
        if not links:
            print("링크 수집 실패. 종료합니다.")
            return

        pd.DataFrame({"링크": links}).to_csv("../../data/product_links.csv", index=False)
        print(f"링크 저장 완료: ../../data/product_links.csv\n")

        # 상품 상세 수집
        results = []
        print(f"[STEP 2] 상품 상세 데이터 수집 시작 ({len(links)}개)")

        for i in trange(len(links)):
            try:
                data = parse_product(driver, links[i])
                results.append(data)
            except Exception as e:
                print(f"\n  {i}번째 상품 오류: {e}")
                results.append({"링크": links[i], "오류": str(e)})

        # 저장
        df = pd.DataFrame(results)
        df.to_csv(OUTPUT_PATH, index=False, encoding="utf-8-sig")
        print(f"\n수집 완료! 저장 경로: {OUTPUT_PATH}")
        print(f"총 {len(df)}개 상품 / {len(df.columns)}개 컬럼")
        print(df[["상품명", "브랜드", "가격", "좋아요수", "평점", "리뷰수"]].head())

    finally:
        driver.quit()


if __name__ == "__main__":
    main()