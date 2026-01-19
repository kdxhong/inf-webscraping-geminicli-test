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
    
    # 커맨드라인 인자 확인 (우클릭 메뉴 등에서 파일 경로가 넘어올 경우)
    if len(sys.argv) > 1:
        file_path = sys.argv[1]
        logger.info(f"인자로 받은 파일 경로: {file_path}")
    else:
        # 인자가 없으면 파일 선택창 띄우기
        file_path = filedialog.askopenfilename(
            title="PDF로 변환할 HWP 파일을 선택하세요",
            filetypes=[("HWP 파일", "*.hwp *.hwpx"), ("모든 파일", "*.*")]
        )
    
    if not file_path:
        logger.info("대상 파일이 없습니다.")
        return

    # 변환 실행
    result_path = hwp_to_pdf(file_path)
    
    if result_path:
        # 인자로 실행된 경우(우클릭 등)는 메시지 박스 없이 조용히 종료하거나 성공 알림만 띄움
        # 여기서는 사용자 경험을 위해 성공 알림을 띄웁니다.
        messagebox.showinfo("성공", f"변환이 완료되었습니다!\n저장 위치: {result_path}")
    else:
        messagebox.showerror("실패", "변환 중 오류가 발생했습니다. 로그를 확인하세요.")

if __name__ == "__main__":
    # 로그 디렉토리 생성
    os.makedirs("logs", exist_ok=True)
    main()
