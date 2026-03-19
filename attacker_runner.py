import os
import csv
import time
import json
from google import genai
from google.genai import types 
from openai import OpenAI

# 프롬프트 파일 불러오기
from prompts import PROMPTS

RUN_GEMINI = False    # True면 Gemini 타겟으로 실행
RUN_GPT = True   # True면 GPT 타겟으로 실행

GEMINI_MODEL = "gemini-2.5-flash-lite"
GPT_MODEL = "gpt-4o-mini"

# 실행할 모달리티(매체) 리스트
TARGET_MODALITIES = ["pdf", "mp3", "youtube", "png", "zip"]
DATA_PATH = "harmful_behaviors.csv"
# ==========================================

class AttackRunner:
    def __init__(self):
        self.gemini_client = None
        self.openai_client = True
        
        if RUN_GEMINI:
            self.gemini_client = genai.Client(api_key=os.environ.get("GOOGLE_API_KEY"))
        if RUN_GPT:
            self.openai_client = OpenAI(
                base_url="https://models.inference.ai.azure.com", 
                api_key=os.environ.get("GITHUB_API_KEY")
            )
    def get_targets(self):
        if not os.path.exists(DATA_PATH):
            print(f"[오류] {DATA_PATH} 파일이 없습니다.")
            return []
        with open(DATA_PATH, "r", encoding="utf-8") as f:
            return [row["goal"] for row in csv.DictReader(f)]

    def run_attack(self, target_model, client, modality, target_goals):
        result_file = f"result_{modality}_{target_model}.json"
        results_data = []
        
        print(f"\n🚀 [{modality.upper()}] 모달리티 -> [{target_model}] 공격 시작...")

        for i, goal in enumerate(target_goals, 1):
            print(f"  [{i}/{len(target_goals)}] 공격 중: {goal}")
            prompt = PROMPTS[modality].format(goal=goal)
            
            res_text = ""
            retry_count = 0
            
            # 429 에러 발생 시 자동 재시도를 위한 루프
            while retry_count < 3:
                try:
                    if "gemini" in target_model:
                        safety_config = types.GenerateContentConfig(
                            safety_settings=[
                                types.SafetySetting(category=types.HarmCategory.HARM_CATEGORY_DANGEROUS_CONTENT, threshold=types.HarmBlockThreshold.BLOCK_MEDIUM_AND_ABOVE),
                                types.SafetySetting(category=types.HarmCategory.HARM_CATEGORY_HARASSMENT, threshold=types.HarmBlockThreshold.BLOCK_MEDIUM_AND_ABOVE),
                                types.SafetySetting(category=types.HarmCategory.HARM_CATEGORY_HATE_SPEECH, threshold=types.HarmBlockThreshold.BLOCK_MEDIUM_AND_ABOVE),
                                types.SafetySetting(category=types.HarmCategory.HARM_CATEGORY_SEXUALLY_EXPLICIT, threshold=types.HarmBlockThreshold.BLOCK_MEDIUM_AND_ABOVE)
                            ]
                        )
                        response = client.models.generate_content(model=target_model, contents=prompt, config=safety_config)
                        res_text = response.text
                        break # 성공 시 루프 탈출
                        
                    elif "gpt" in target_model:
                        response = client.chat.completions.create(
                            model=target_model,
                            messages=[{"role": "user", "content": prompt}]
                        )
                        res_text = response.choices[0].message.content
                        break # 성공 시 루프 탈출
                        
                except Exception as e:
                    error_msg = str(e)
                    if "429" in error_msg or "RESOURCE_EXHAUSTED" in error_msg:
                        print("    ⚠️ API 한도 초과(429). 25초 대기 후 재시도합니다...")
                        time.sleep(10)
                        retry_count += 1
                        res_text = f"Attack Failed after retries: {error_msg}"
                    else:
                        res_text = f"Attack Failed: {error_msg}"
                        break # 429가 아닌 다른 에러면 즉시 실패 처리
            
            results_data.append({"number": i, "question": goal, "answer": res_text})
            with open(result_file, "w", encoding="utf-8") as f: 
                json.dump(results_data, f, ensure_ascii=False, indent=4)
                
            # 기본 대기 시간 (요청하신 4초)
            time.sleep(10)
            
        print(f"✅ 완료! 결과 파일: {result_file}")

    def execute_all(self):
        targets = self.get_targets()
        test_targets = targets[:5] # 테스트용 5개
        if not test_targets: return

        for modality in TARGET_MODALITIES:
            if RUN_GPT:
                self.run_attack(GPT_MODEL, self.openai_client, modality, test_targets)
            if RUN_GEMINI:
                self.run_attack(GEMINI_MODEL, self.gemini_client, modality, test_targets)

if __name__ == "__main__":
    runner = AttackRunner()
    runner.execute_all()