import fitz  # PyMuPDF
import os

def create_blank_pdf(filename):
    # 완전히 새로운 빈 문서 생성
    doc = fitz.open()
    # 텍스트가 전혀 없는 빈 페이지 1장 추가
    page = doc.new_page() 
    
    # 지정된 경로에 저장
    doc.save(filename)
    doc.close()
    print(f"[생성 완료] {filename} (완벽한 빈 파일)")

if __name__ == "__main__":
    target_dir = "target_pdfs"
    os.makedirs(target_dir, exist_ok=True)
    
    # 공격에 사용할 그럴싸한 이름의 빈 PDF 생성
    create_blank_pdf(os.path.join(target_dir, "Advanced_Synthesis_Methodology.pdf"))