import os
import markdown
import asyncio
import re
import base64
from playwright.async_api import async_playwright
from loguru import logger

def get_base64_image(img_path):
    """이미지 파일을 읽어서 Base64 문자열로 변환합니다."""
    try:
        if not os.path.exists(img_path):
            logger.warning(f"이미지 파일을 찾을 수 없습니다: {img_path}")
            return None
        
        ext = os.path.splitext(img_path)[1].lower().replace('.', '')
        if ext == 'wmf': # 브라우저에서 지원하지 않는 형식
            logger.warning(f"브라우저에서 지원하지 않는 이미지 형식(wmf)입니다: {img_path}")
            return None
            
        mime_type = f"image/{ext}"
        if ext == 'jpg': mime_type = "image/jpeg"
        
        with open(img_path, "rb") as image_file:
            encoded_string = base64.b64encode(image_file.read()).decode('utf-8')
            return f"data:{mime_type};base64,{encoded_string}"
    except Exception as e:
        logger.error(f"이미지 인코딩 실패 ({img_path}): {e}")
        return None

async def convert_md_to_pdf(md_path, pdf_path):
    logger.info(f"변환 시작: {md_path} -> {pdf_path}")
    
    if not os.path.exists(md_path):
        logger.error(f"파일을 찾을 수 없습니다: {md_path}")
        return

    # 1. Markdown 읽기
    with open(md_path, 'r', encoding='utf-8') as f:
        md_text = f.read()

    # 2. HTML로 변환
    html_content = markdown.markdown(md_text, extensions=['tables', 'fenced_code', 'codehilite'])

    # 3. 이미지 태그를 찾아서 Base64 데이터로 교체
    base_dir = os.path.dirname(os.path.abspath(md_path))
    
    def replacer(match):
        # images\filename.png 또는 images/filename.png 추출
        rel_path = match.group(1).replace(os.sep, '/')
        full_path = os.path.join(base_dir, rel_path)
        
        b64_data = get_base64_image(full_path)
        if b64_data:
            return f'src="{b64_data}"'
        else:
            return match.group(0) # 실패 시 원래 태그 유지

    # <img> 태그의 src 속성 중 images 폴더로 시작하는 것들을 타겟팅
    html_content = re.sub(r'src="(images[\\/][^"]+)"', replacer, html_content)

    # 4. HTML 템플릿 구성 (스타일 추가)
    full_html = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="utf-8">
        <style>
            body {{
                font-family: 'Malgun Gothic', 'Apple SD Gothic Neo', sans-serif;
                line-height: 1.6;
                padding: 40px;
                color: #333;
                font-size: 13px;
            }}
            table {{
                border-collapse: collapse;
                width: 100%;
                margin: 20px 0;
                page-break-inside: avoid;
            }}
            th, td {{
                border: 1px solid #ddd;
                padding: 8px;
                text-align: left;
                word-break: break-all;
            }}
            th {{
                background-color: #f4f4f4;
            }}
            img {{
                max-width: 100%;
                height: auto;
                display: block;
                margin: 15px 0;
            }}
            h1, h2, h3 {{
                color: #2c3e50;
                border-bottom: 2px solid #3498db;
                padding-bottom: 10px;
                margin-top: 30px;
                page-break-after: avoid;
            }}
            hr {{
                border: 0;
                border-top: 1px solid #eee;
                margin: 40px 0;
            }}
            pre {{
                background-color: #f8f8f8;
                padding: 15px;
                border-radius: 5px;
                overflow-x: auto;
                border: 1px solid #ddd;
            }}
            .page-break {{
                page-break-before: always;
            }}
        </style>
    </head>
    <body>
        {html_content}
    </body>
    </html>
    """

    # 5. Playwright를 이용한 PDF 렌더링
    async with async_playwright() as p:
        browser = await p.chromium.launch()
        page = await browser.new_page()
        
        try:
            # HTML 내용 주입 (Base64 방식이므로 base_url 불필요)
            await page.set_content(full_html)
            
            # 리소스가 완전히 로드될 때까지 대기
            await page.wait_for_load_state("load")
            
            # PDF 저장
            await page.pdf(path=pdf_path, format="A4", margin={
                "top": "2cm",
                "bottom": "2cm",
                "left": "2cm",
                "right": "2cm"
            }, print_background=True)
            
            logger.info("PDF 변환 및 이미지 임베딩 완료!")
        except Exception as e:
            logger.error(f"PDF 생성 중 오류 발생: {e}")
        finally:
            await browser.close()

if __name__ == "__main__":
    current_dir = os.path.dirname(os.path.abspath(__file__))
    input_md = os.path.join(current_dir, "output.md")
    output_pdf = os.path.join(current_dir, "output.pdf")
    
    asyncio.run(convert_md_to_pdf(input_md, output_pdf))
