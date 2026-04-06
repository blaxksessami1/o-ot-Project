import cv2
import os
import random

def is_valid_image(path, min_size=100, blur_threshold=50):
    img = cv2.imread(path)
    if img is None:
        return False
    h, w = img.shape[:2]
    if h < min_size or w < min_size:
        return False
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    if cv2.Laplacian(gray, cv2.CV_64F).var() < blur_threshold:
        return False
    return True

data_dir = r"database"  # 데이터 폴더 경로로 수정하세요
target = 800

for category in os.listdir(data_dir):
    folder = os.path.join(data_dir, category)
    if not os.path.isdir(folder):
        continue

    files = os.listdir(folder)
    valid = [f for f in files if is_valid_image(os.path.join(folder, f))]
    
    print(f"{category}: 전체 {len(files)}장 → 유효 {len(valid)}장")

    if len(valid) > target:
        to_delete = random.sample(valid, len(valid) - target)
        for f in to_delete:
            os.remove(os.path.join(folder, f))
        print(f"  → {target}장으로 다운샘플링 완료")
    elif len(valid) < target:
        print(f"  ⚠️ {target - len(valid)}장 부족")