import os
import sys
import win32com.client
from tkinter import filedialog, messagebox
import tkinter as tk
from loguru import logger

# 로깅 설정
logger.add("logs/hwp2pdf.log", rotation="500 MB", encoding="utf-8")

def hwp_to_pdf(hwp_path):
    """
    HWP 파일을 동일한 경로에 동일한 이름의 PDF로 변환합니다.
    """
    try:
        # 절대 경로로 변환
        abs_hwp_path = os.path.abspath(hwp_path)
        pdf_path = os.path.splitext(abs_hwp_path)[0] + ".pdf"
        
        logger.info(f"변환 시작: {abs_hwp_path}")
        
        # 한글 OLE 인스턴스 생성
        hwp = win32com.client.gencache.EnsureDispatch("HWPFrame.HwpObject")
        
        # 보안 경고 창 방지 (필요 시)
        # hwp.RegisterModule("FilePathCheckDLL", "FilePathCheckerModule") 
        
        # 파일 열기
        # Open(파일경로, 포맷, 파라미터)
        if not hwp.Open(abs_hwp_path):
            logger.error(f"파일을 열 수 없습니다: {abs_hwp_path}")
            return False
            
        # PDF로 저장 (SaveAs 파라미터 1: 파일경로, 2: 포맷 "PDF", 3: 옵션)
        # "PDF" 포맷은 한컴오피스 버전에 따라 다를 수 있으나 최신 버전은 지원함
        hwp.SaveAs(pdf_path, "PDF")
        
        # 한글 종료
        hwp.Quit()
        
        logger.success(f"변환 완료: {pdf_path}")
        return pdf_path
        
    except Exception as e:
        logger.exception(f"변환 중 오류 발생: {e}")
        return None

def main():
    # GUI 루트 생성 (표시되지 않게 설정)
    root = tk.Tk()
    root.withdraw()
    
    file_paths = []
    
    # 커맨드라인 인자 확인 (우클릭 메뉴 등에서 여러 파일 경로가 넘어올 경우)
    if len(sys.argv) > 1:
        file_paths = sys.argv[1:]
        logger.info(f"인자로 받은 파일 개수: {len(file_paths)}")
    else:
        # 인자가 없으면 다중 파일 선택창 띄우기
        selected_files = filedialog.askopenfilenames(
            title="PDF로 변환할 HWP 파일들을 선택하세요",
            filetypes=[("HWP 파일", "*.hwp *.hwpx"), ("모든 파일", "*.*")]
        )
        if selected_files:
            file_paths = list(selected_files)
    
    if not file_paths:
        logger.info("대상 파일이 없습니다.")
        return

    success_count = 0
    fail_count = 0
    
    # 여러 파일 순차 변환
    for path in file_paths:
        result_path = hwp_to_pdf(path)
        if result_path:
            success_count += 1
        else:
            fail_count += 1
            
    # 결과 요약 알림
    summary_msg = f"변환 완료!\n- 성공: {success_count}건"
    if fail_count > 0:
        summary_msg += f"\n- 실패: {fail_count}건 (로그 확인 필요)"
        messagebox.showwarning("결과 요약", summary_msg)
    else:
        messagebox.showinfo("결과 요약", summary_msg)

if __name__ == "__main__":
    # 로그 디렉토리 생성
    os.makedirs("logs", exist_ok=True)
    main()
