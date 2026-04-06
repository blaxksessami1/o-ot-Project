import os
import time
import urllib.request
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager

# 1. 카테고리별 검색어 설정
search_config = {
    
    "Athleisure": ["athleisure outfit", "sporty casual look", "gym to street style"],
    "Formal":    ["classic style outfit", "formal fashion look", "business formal wear"],
    "Minimal":   ["minimalist outfit", "clean aesthetic fashion", "minimal style look"],
    "Romantic":  ["feminine outfit", "romantic style look", "soft girl aesthetic"],
    "Edge":      ["edgy outfit", "dark aesthetic fashion", "grunge style look"],
    "Glam":      ["glam outfit", "glamorous fashion look", "party glam style"],
    "Bohemian":  ["boho outfit", "bohemian style look", "boho chic fashion"],
    "Preppy":    ["preppy outfit", "ivy league style", "preppy aesthetic look"],
}

target_per_keyword = 350  # 검색어당 목표 장수
base_folder = "database"

# 2. 크롬 설정
options = webdriver.ChromeOptions()
options.add_experimental_option("detach", True)
options.add_experimental_option("excludeSwitches", ["enable-automation"])
options.add_experimental_option("useAutomationExtension", False)

driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)

# 3. 로그인 (한 번만)
print("핀터레스트에 접속합니다...")
driver.get("https://www.pinterest.co.kr/")
input("\n[필수] 로그인 완료 후 Enter를 누르세요...\n")

# 4. URL 수집 함수
def collect_image_urls(driver, search_keyword, target_count):
    url = f"https://www.pinterest.co.kr/search/pins/?q={search_keyword}"
    driver.get(url)
    time.sleep(4)

    image_urls = set()
    scroll_attempts = 0

    while len(image_urls) < target_count:
        previous_count = len(image_urls)

        for img in driver.find_elements(By.TAG_NAME, "img"):
            try:
                src = img.get_attribute("src")
                if src and "pinimg.com" in src:
                    if "236x" in src:
                        image_urls.add(src.replace("236x", "736x"))
                    elif "736x" in src:
                        image_urls.add(src)
            except Exception:
                continue

        print(f"  [{search_keyword}] 수집된 URL: {len(image_urls)}개")

        if len(image_urls) >= target_count:
            break
        if len(image_urls) == previous_count:
            scroll_attempts += 1
        else:
            scroll_attempts = 0
        if scroll_attempts >= 10:
            print(f"  새 이미지 없음 — 조기 종료")
            break

        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        time.sleep(3)

    return list(image_urls)[:target_count]

# 5. 다운로드 함수
def download_images(urls, save_folder, category_name):
    existing = len([f for f in os.listdir(save_folder) if f.endswith(".jpg")])
    success, fail = 0, 0

    for i, img_url in enumerate(urls, start=existing + 1):
        file_path = f"{save_folder}/{category_name}_{i}.jpg"
        try:
            req = urllib.request.Request(img_url, headers={"User-Agent": "Mozilla/5.0"})
            with urllib.request.urlopen(req) as response, open(file_path, "wb") as f:
                f.write(response.read())
            print(f"  [{i}] 저장 완료")
            success += 1
        except Exception as e:
            print(f"  [{i}] 실패 — {e}")
            fail += 1

    return success, fail

# 6. 전체 배치 실행
for category_name, keywords in search_config.items():
    save_folder = f"{base_folder}/{category_name}"
    os.makedirs(save_folder, exist_ok=True)

    print(f"\n{'='*40}")
    print(f"카테고리: {category_name}")
    print(f"{'='*40}")

    total_success, total_fail = 0, 0

    for keyword in keywords:
        print(f"\n검색어: '{keyword}'")
        urls = collect_image_urls(driver, keyword, target_per_keyword)
        success, fail = download_images(urls, save_folder, category_name)
        total_success += success
        total_fail += fail

    print(f"\n[{category_name}] 완료 — 성공 {total_success}장 / 실패 {total_fail}장")

print("\n🎉 전체 크롤링 완료!")
driver.quit()