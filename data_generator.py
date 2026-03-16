import os
import csv
import json
import urllib.request

def generate_target_data(limit=50, test_mode=True):
    url = "https://raw.githubusercontent.com/llm-attacks/llm-attacks/main/data/advbench/harmful_behaviors.csv"
    csv_path = "harmful_behaviors.csv"
    output_json = "attack_targets.json"

    # 1. 깃허브에서 CSV 다운로드
    if not os.path.exists(csv_path):
        print("[System] AdvBench 데이터셋 다운로드 중...")
        urllib.request.urlretrieve(url, csv_path)

    # 2. 'goal' 컬럼만 추출
    goals = []
    with open(csv_path, "r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            goals.append(row["goal"])

    # 3. 테스트 모드에 따라 개수 조절
    final_goals = goals[:5] if test_mode else goals[:limit]

    # 4. 다른 스크립트가 읽기 편하게 JSON으로 저장
    with open(output_json, "w", encoding="utf-8") as f:
        json.dump(final_goals, f, ensure_ascii=False, indent=4)
    
    print(f"[생성 완료] {len(final_goals)}개의 타겟 데이터가 '{output_json}'에 저장되었습니다.")
    print(f"(테스트 모드: {'ON (5개)' if test_mode else f'OFF ({limit}개)'})")

if __name__ == "__main__":
    # 테스트 모드면 True, 본 실험이면 False로 변경 후 실행하세요.
    generate_target_data(limit=50, test_mode=True)