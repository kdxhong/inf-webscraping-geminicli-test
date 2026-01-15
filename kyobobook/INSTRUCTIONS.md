# 교보문고 데이터 스크래핑 프로젝트 지시서

이 문서는 교보문고 도서 데이터를 수집하고 분석하기 위한 에이전트 작업 지침입니다.

## 1. 프로젝트 개요

- **목표**: 교보문고 베스트셀러 또는 특정 카테고리의 도서 정보를 스크래핑하여 데이터베이스화하고 트렌드를 분석함.
- **대상 **: 교보문고 베스트셀러
- **주요 수집 항목**:
  - 도서명, 저자, 출판사, 가격, 출판일
  - 판매 지수, 리뷰 평점, 리뷰 개수
  - 도서 카테고리 (국내도서/외국도서 및 세부 분류)

## 2. 기술 스택 및 환경

- **언어**: Python 3.12+
- **가상환경**: 프로젝트 루트의 `.venv` 사용
- **주요 라이브러리**:
  - `requests`, `beautifulsoup4`: 정적 페이지 스크래핑
  - `selenium` (필요 시): 동적 콘텐츠 렌더링 대응
  - `pandas`: 데이터 전처리 및 저장
  - `loguru`: 작업 로그 기록
  - `koreanize-matplotlib`: 데이터 시각화 시 한글 지원

## 3. 스크래핑 규칙 및 가이드라인

- **데이터 저장**:
  - 수집된 원본 데이터(CSV/JSON): `kyobobook/data/raw/`
  - 정제된 데이터: `kyobobook/data/processed/`
- **로깅**: `loguru`를 사용하여 `kyobobook/logs/scraping.log`에 실행 과정을 기록할 것.
- **예절(Politeness)**: `robots.txt`를 확인하고, 요청 간 적절한 지연 시간(1~2초)을 두어 서버 부하를 방지함.
- **에러 처리**: 네트워크 오류나 파싱 실패 시 예외 처리를 철저히 하고 로그에 기록할 것.
- **데이터 추출**: JSON 응답을 활용합니다. 1페이지부터 10페이지까지 수집하되 페이지당 50개의 도서를 가져올 것

## 4. 네트워크 정보 (분석 필요 시 업데이트)

> _스크래핑 구현 전 개발자 도구(F12) 네트워크 탭을 통해 확인한 정보를 아래에 기록하세요._

- **실제 데이터 URL**:
  Request URL
  https://store.kyobobook.co.kr/api/gw/best/best-seller/online?page=1&per=20&period=001&dsplDvsnCode=000&dsplTrgtDvsnCode=001
  Request Method
  GET
  Status Code
  200 OK
- **Header 정보**:
  referer
  https://store.kyobobook.co.kr/bestseller/online/daily?page=1
  sec-ch-ua
  "Google Chrome";v="143", "Chromium";v="143", "Not A(Brand";v="24"
  sec-ch-ua-mobile
  ?0
  sec-ch-ua-platform
  "Windows"
  sec-ch-ua-platform-version
  "15.0.0"
  sec-fetch-dest
  empty
  sec-fetch-mode
  cors
  sec-fetch-site
  same-origin
  user-agent
  Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/143.0.0.0 Safari/537.36
  x-api-gw-key
  eyJhbGciOiJkaXIiLCJlbmMiOiJBMjU2R0NNIn0..xbdmp20Emtwv2BoX.WuBZ3Ymy399atUzbI-sJu8FXs-XLZ0nHFWpbzNaFgJRH07fsHxOCRQWDL-NH2SuQCY0oUDCh64VIgQtw5Sn5rt-MfNxQ0i9KBtj57pMhPOfT_4ge73wuJWBOgF3NJPmLRVfUijv0.y8NtBzDe5wGk2CwuAQaCHA
- **Payload/Query Params**:
  page=1&per=20&period=001&dsplDvsnCode=000&dsplTrgtDvsnCode=001
- **응답 예시**:
  bestSeller의 하위 정보를 모두 수집, 응답은 JSON으로 받습니다.

  {
  "data": {
  "bestSeller": [

해당 도서가 html로 보여질때는 다음의 예시로 보여집니다.

<div class="flex items-top justify-start mr-[35px] w-full"><div class="relative flex-shrink-0 overflow-hidden w-[144px]"><a class="prod_link relative block overflow-hidden border border-gray-300" href="https://product.kyobobook.co.kr/detail/S000218438100"><div class="relative h-full" style="width: 144px; height: auto; max-height: 208px;"><img alt="괴테는 모든 것을 말했다" fetchpriority="high" loading="eager" width="144" height="208" decoding="async" data-nimg="1" class="transition-[transform, opacity] duration-300" src="https://contents.kyobobook.co.kr/sih/fit-in/300x0/filters:format(webp)/pdt/9791194530701.jpg" style="color: transparent; width: 144px; height: auto; max-height: 208px; object-fit: fill;"></div></a><div class="fz-12 mt-2 flex items-center justify-center text-center text-gray-700"><a target="_blank" class="prod_link flex items-center gap-0.5" href="https://product.kyobobook.co.kr/detail/S000218438100"><svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" fill="none" viewBox="0 0 16 16" stroke="#767676"><desc>새창보기 아이콘</desc><path stroke="current" stroke-linecap="round" stroke-linejoin="round" d="M10 3.333h2.667V6M12.666 8v2.518c0 1.19-.96 2.149-2.149 2.149H5.483c-1.19 0-2.149-.96-2.149-2.15V5.483c0-1.189.96-2.149 2.149-2.149h2.591M12.666 3.333 9.333 6.667"></path></svg><span class="inline-block">새창보기</span></a><span class="mx-2 h-2 w-px bg-gray-500"></span><a class="flex items-center gap-0.5" href=""><svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" fill="none" viewBox="0 0 16 16" stroke="#767676"><desc>검색 아이콘</desc><g stroke="current" clip-path="url(#ico_search_svg__a)"><path d="M7 11.333a4.333 4.333 0 1 0 0-8.666 4.333 4.333 0 0 0 0 8.666Z"></path><path stroke-linecap="round" d="m10.333 10.333 3 3"></path></g><defs><clipPath id="ico_search_svg__a"><path fill="#fff" d="M0 0h16v16H0z"></path></clipPath></defs></svg><span class="inline-block align-top">미리보기</span></a></div></div><div class="ml-4 w-full min-w-[516px]"><div class="flex flex-col gap-1"><div class="flex flex-wrap gap-2"><div class="flex justify-between    items-start"><div class="block min-w-[22px]"><svg xmlns="http://www.w3.org/2000/svg" width="118" height="24" fill="none" viewBox="0 0.5 118 24"><desc>교보문고 Best 1</desc><path fill="url(#badge_best_kbb_svg__a)" d="M0 8.5a8 8 0 0 1 8-8h110v16a8 8 0 0 1-8 8H0z"></path><mask id="badge_best_kbb_svg__b" width="118" height="24" x="0" y="0" maskUnits="userSpaceOnUse" style="mask-type: luminance;"><path fill="#fff" d="M6 .5h112v18a6 6 0 0 1-6 6H0v-18a6 6 0 0 1 6-6"></path></mask><g mask="url(#badge_best_kbb_svg__b)"><path fill="url(#badge_best_kbb_svg__c)" d="M101.5 42.5c11.322 0 20.5-10.297 20.5-23s-9.178-23-20.5-23S81 6.797 81 19.5s9.178 23 20.5 23" opacity="0.15"></path><path fill="url(#badge_best_kbb_svg__d)" d="M80.5 59.5c12.426 0 22.5-11.193 22.5-25s-10.074-25-22.5-25S58 20.693 58 34.5s10.074 25 22.5 25" opacity="0.13"></path></g><path fill="#fff" d="M22.927 19H11.119a.55.55 0 0 1-.333-.136.56.56 0 0 1-.182-.314l-1.34-7.422H9.23c-.27 0-.532-.09-.747-.257-.215-.166-.37-.4-.44-.664a1.27 1.27 0 0 1 .046-.8c.102-.254.283-.468.516-.607a1.215 1.215 0 0 1 1.483.181 1.268 1.268 0 0 1 .219 1.502l3.107 1.692q.041.024.085.04a.522.522 0 0 0 .51-.24l.949-1.45 1.342-2.247a1.25 1.25 0 0 1-.464-.619 1.27 1.27 0 0 1 .429-1.412 1.22 1.22 0 0 1 1.455-.01c.212.156.37.377.45.63a1.27 1.27 0 0 1-.46 1.402l2.386 3.706a.56.56 0 0 0 .281.238q.038.006.075.005a.5.5 0 0 0 .24-.06l2.15-1.178.852-.49a1.27 1.27 0 0 1 .21-1.504 1.215 1.215 0 0 1 1.483-.187c.234.138.415.35.518.605.102.254.12.535.05.8-.071.265-.226.498-.44.665a1.2 1.2 0 0 1-.747.258h-.025l-.071.362-.067.374-.043.242-.019.11c-.344 1.93-1.058 5.949-1.148 6.335-.095.404-.36.45-.47.45M17 16.287q.076 0 .142.037l1.2.652a.3.3 0 0 0 .27.008.3.3 0 0 0 .163-.201.3.3 0 0 0 .003-.134l-.253-1.304a.31.31 0 0 1 .092-.285l.977-.902a.307.307 0 0 0-.167-.528l-1.344-.168a.29.29 0 0 1-.233-.169l-.582-1.219a.298.298 0 0 0-.54 0l-.583 1.22a.3.3 0 0 1-.234.168l-1.342.168a.3.3 0 0 0-.251.209.31.31 0 0 0 .084.319l.977.902a.3.3 0 0 1 .092.285l-.253 1.304a.3.3 0 0 0 .06.251.3.3 0 0 0 .234.114q.076 0 .142-.037l1.2-.652a.3.3 0 0 1 .146-.038"></path><g filter="url(#badge_best_kbb_svg__e)"><path fill="#fff" d="m39.24 14.608-1.584-.156c.36-2.004.372-3.492.372-4.764h-6.54v-1.26h8.124v1.068c0 1.356 0 2.88-.372 5.112m-2.34 1.32h3.624V17.2H30.516v-1.272h2.1v-3.492h1.56v3.492h1.176v-3.492H36.9zm7.163-4.8v1.548h4.728v-1.548zm3.156 4.836h4.224v1.284H41.435v-1.284h4.2v-2.028h-3.144V8.164h1.572V9.88h4.728V8.164h1.56v5.772H47.22zm12.3-5.148V9.184h-4.38v1.632zm1.56-2.868v4.116h-7.5V7.948zm-5.989 7.188v1.944h6.156v1.26h-7.74v-3.204zm-2.748-2.196H62.35v1.248h-4.068v1.884h-1.584v-1.884h-4.356zm19.535 1.836-1.584-.18c.42-2.088.444-3.624.444-4.908h-6.444v-1.26h8.028v1.056c0 1.38 0 2.94-.444 5.292m-3.48 1.152h4.884V17.2h-9.996v-1.272h3.528v-3.804h1.584zm11.944-2.283h-2.173l-.012-1.073h1.898q.48 0 .815-.14.34-.147.515-.416.176-.276.176-.662 0-.428-.164-.698a.94.94 0 0 0-.504-.392q-.334-.123-.855-.123h-1.424V17.5h-1.47V8.969h2.894q.702 0 1.254.135.556.135.943.421.393.282.592.715.205.434.205 1.031 0 .528-.252.967a1.9 1.9 0 0 1-.744.71q-.492.275-1.225.327zm-.064 3.855h-2.572l.662-1.166h1.91q.499 0 .832-.164.335-.17.498-.463.17-.3.17-.697 0-.417-.147-.72a1 1 0 0 0-.462-.475q-.317-.17-.827-.17H78.69l.012-1.073h2.15l.334.405q.704.023 1.154.31.458.287.68.744t.223.985q0 .815-.358 1.365a2.2 2.2 0 0 1-1.013.838q-.663.28-1.594.281m6.981.117q-.702 0-1.271-.228a2.8 2.8 0 0 1-.96-.65 2.9 2.9 0 0 1-.604-.98 3.4 3.4 0 0 1-.211-1.212v-.235q0-.744.216-1.347a3.1 3.1 0 0 1 .604-1.031q.387-.434.914-.662a2.8 2.8 0 0 1 1.143-.229q.68 0 1.189.229.51.228.844.644.339.41.504.979.17.567.17 1.253v.604h-4.899v-1.014h3.504v-.111a2 2 0 0 0-.152-.715 1.2 1.2 0 0 0-.416-.539q-.282-.205-.75-.205-.353 0-.627.152-.27.146-.451.428a2.3 2.3 0 0 0-.282.68 3.8 3.8 0 0 0-.093.884v.235q0 .416.11.773.119.352.34.615.224.264.54.417.316.146.72.146.51 0 .909-.205.398-.205.691-.58l.744.72q-.204.3-.533.575a2.7 2.7 0 0 1-.803.44q-.468.17-1.09.17m7.076-1.834a.7.7 0 0 0-.106-.38q-.105-.177-.404-.317-.292-.141-.867-.258a7.5 7.5 0 0 1-.926-.263 3 3 0 0 1-.715-.381 1.6 1.6 0 0 1-.463-.528 1.46 1.46 0 0 1-.164-.703q0-.387.17-.732.17-.346.487-.61a2.4 2.4 0 0 1 .767-.416 3.2 3.2 0 0 1 1.02-.152q.796 0 1.365.27.574.263.879.72.305.45.305 1.02h-1.413a.9.9 0 0 0-.129-.469.9.9 0 0 0-.374-.357 1.3 1.3 0 0 0-.633-.141q-.364 0-.604.117a.83.83 0 0 0-.351.293.75.75 0 0 0-.053.686.7.7 0 0 0 .21.228q.147.1.4.188.257.087.644.17.726.152 1.248.392.526.234.808.61.282.369.282.937 0 .422-.182.773-.176.346-.516.604a2.6 2.6 0 0 1-.814.393q-.469.14-1.055.14-.86 0-1.459-.305-.597-.31-.908-.79a1.87 1.87 0 0 1-.305-1.008h1.366q.023.392.216.627.2.228.493.334.299.1.615.1.381 0 .638-.1a.9.9 0 0 0 .393-.282.67.67 0 0 0 .135-.41m5.405-4.623v1.031h-3.574v-1.03zm-2.543-1.553h1.412v6.141q0 .293.082.451.09.153.24.205.153.053.358.053.147 0 .281-.018a3 3 0 0 0 .217-.035l.006 1.078a4 4 0 0 1-.41.094 3 3 0 0 1-.528.041q-.486 0-.86-.17a1.27 1.27 0 0 1-.587-.568q-.21-.393-.21-1.043zm10.155-.668V17.5h-1.412v-6.885l-2.092.71v-1.167l3.334-1.219z"></path></g><defs><linearGradient id="badge_best_kbb_svg__a" x1="-5" x2="123" y1="28.5" y2="7" gradientUnits="userSpaceOnUse"><stop stop-color="#3853E3"></stop><stop offset="1" stop-color="#44D166"></stop></linearGradient><linearGradient id="badge_best_kbb_svg__c" x1="94.202" x2="118.994" y1="21.156" y2="8.782" gradientUnits="userSpaceOnUse"><stop stop-color="#fff"></stop><stop offset="1" stop-color="#fff" stop-opacity="0"></stop></linearGradient><linearGradient id="badge_best_kbb_svg__d" x1="80.5" x2="50.251" y1="9.5" y2="48.041" gradientUnits="userSpaceOnUse"><stop stop-color="#fff"></stop><stop offset="1" stop-color="#fff" stop-opacity="0"></stop></linearGradient><filter id="badge_best_kbb_svg__e" width="86.835" height="20.392" x="25.516" y="4.948" color-interpolation-filters="sRGB" filterUnits="userSpaceOnUse"><feFlood flood-opacity="0" result="BackgroundImageFix"></feFlood><feColorMatrix in="SourceAlpha" result="hardAlpha" values="0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 127 0"></feColorMatrix><feOffset dy="2"></feOffset><feGaussianBlur stdDeviation="2.5"></feGaussianBlur><feComposite in2="hardAlpha" operator="out"></feComposite><feColorMatrix values="0 0 0 0 0.157901 0 0 0 0 0.182164 0 0 0 0 0.628608 0 0 0 0.1 0"></feColorMatrix><feBlend in2="BackgroundImageFix" mode="overlay" result="effect1_dropShadow_6089_938"></feBlend><feBlend in="SourceGraphic" in2="effect1_dropShadow_6089_938" result="shape"></feBlend></filter></defs></svg></div></div><span class="text-red-error fz-12 flex items-center gap-0.5 font-medium"><svg xmlns="http://www.w3.org/2000/svg" width="12" height="12" fill="#EC1F2D" viewBox="0 0 12 12"><path fill="current" d="m6 3 4 5H2z"></path></svg>1</span></div><div class="flex flex-wrap gap-1 text-[0px]"><span class="h-[22px] px-1 py-0.5 flex items-center font-text-m text-center border box-border font-weight-medium text-blue-800 border-blue-700 rounded">오늘의 선택</span><span class="h-[22px] px-1 py-0.5 flex items-center font-text-m text-center border box-border font-weight-medium text-gray-700 border-gray-400 rounded">이벤트</span><span class="h-[22px] px-1 py-0.5 flex items-center font-text-m text-center border box-border font-weight-medium text-gray-700 border-gray-400 rounded">사은품</span><span class="h-[22px] px-1 py-0.5 flex items-center font-text-m text-center border box-border font-weight-medium text-gray-700 border-gray-400 rounded">소득공제</span></div></div><a class="prod_link line-clamp-2 font-medium text-black hover:underline fz-16 mt-2" href="https://product.kyobobook.co.kr/detail/S000218438100">괴테는 모든 것을 말했다</a><div class="line-clamp-2 flex overflow-hidden whitespace-normal break-all text-gray-800 fz-14 mt-1">스즈키 유이<span class="mx-1">&nbsp;·&nbsp;</span>리프<span class="mx-1">&nbsp;·&nbsp;</span><span class="date">2025.11.18</span></div><div class="flex flex-col mt-3"><div class="flex flex-row flex-wrap place-items-center items-center justify-start gap-1 mt-0.5"><span class="font-bold inline-block align-top text-green-800 fz-16">10%</span><span class="inline-block align-top fz-16"><span class="font-bold">15,300</span><span class="font-normal">원</span></span><span class="inline-block align-top"><span class="hidden">정가</span><s class="text-gray-700">17,000원</s></span><div class="inline-block h-2 w-px items-center bg-black opacity-20"></div><span class="fz-12 line-block items-center uppercase text-gray-800">850p</span></div></div><p class="prod_introduction fz-14 break-all font-normal text-gray-800 mt-3 line-clamp-2 max-w-[516px]">저명한 괴테 연구가 도이치는 홍차 티백에서 출처 불명의 괴테 명언을 발견한다. “사랑은 모든 것을 혼동시키지 않고 혼연일체로 만든다.” 평생 괴테를 연구한 그조차 본 적 없는 낯선 문장이지만, 이상하게도 자신이 주장해 온 이론을 완벽하게 요약하는 것처럼 느껴진다. 출처를 찾을 수 없는 말은 거짓인가, 아니면 새로운 진실인가? 이 한 문장이 도이치의 삶을 뒤흔들기 시작한다.
『괴테는 모든 것을 말했다』는 23세 대학원생 스즈키 유이의 첫 장편소설로, 제172회 아쿠타가와상을 수상했다. 일본 언론은 그를 움베르토 에코, 칼비노, 보르헤스에 견주며 “일본 문학의 샛별”이라 극찬했다. 스무 살 남짓한 청년이 쓴 이 작품에서는 고전문학의 풍부한 깊이와 신인만의 참신함이 동시에 느껴진다.
『괴테는 모든 것을 말했다』는 한 가족의 일상을 통해 사랑과 언어, 문학의 본질을 탐구한다. 괴테, 니체부터 보르헤스, 말라르메까지 방대한 인문학 지식이 소설 곳곳에 녹아 있지만, 어딘가 어리숙하고 사랑스러운 인물들과 어우러져 난해하지 않게 다가온다. 잔잔하게 흘러가던 일상이 후반부로 가며 서로 연결되고, 저마다 다른 인물들이 하나가 되어간다. 학문과 일상, 고전과 현대가 각자의 개성을 유지하면서도 아름답게 어우러지는 이 소설은, 사랑의 온기로 모든 것을 다시 읽어내는 이야기이다.</p><div class=" flex w-full flex-wrap gap-3"><div class="flex-grow flex flex-col"><div class="flex items-center justify-between"><div class="mt-2 flex flex-1 justify-between"><div class="flex flex-row items-center gap-1 fz-14"><svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" fill="#4DAC27" viewBox="0 0 17 16" stroke="none"><desc>별점 클로버 아이콘</desc><g clip-path="url(#ico_clover_svg__a)"><path fill="current" d="M8.489 13.546V7.817h3.139a2.4 2.4 0 0 1 2.4 2.403v.092a2.403 2.403 0 0 1-2.4 2.403h-.74a2.4 2.4 0 0 1-1.476-.52v1.343a.462.462 0 0 1-.923 0zm-4.062-.822a2.397 2.397 0 0 1-2.4-2.403v-.092a2.405 2.405 0 0 1 2.4-2.402h3.139v2.494a2.404 2.404 0 0 1-2.4 2.403zm4.062-5.827V4.402A2.403 2.403 0 0 1 10.889 2h.739a2.4 2.4 0 0 1 2.4 2.402v.093a2.403 2.403 0 0 1-2.4 2.402zm-4.062 0a2.4 2.4 0 0 1-1.697-.703 2.4 2.4 0 0 1-.703-1.7v-.092A2.403 2.403 0 0 1 4.427 2h.74a2.4 2.4 0 0 1 2.399 2.402v2.495z"></path></g><defs><clipPath id="ico_clover_svg__a"><path fill="#fff" d="M.027 0h16v16h-16z"></path></clipPath></defs></svg><span class="font-bold text-black">9.32</span><span class="font-normal text-gray-700">(281개의 리뷰)</span><svg xmlns="http://www.w3.org/2000/svg" width="4" height="8" fill="none"><desc>slash 아이콘</desc><path fill="#CCC" d="M1 8H0l3-8h1z"></path></svg><svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" fill="#5055B1" viewBox="0 0 17 16" stroke="none"><desc>리뷰 아이콘</desc><g clip-path="url(#ico_review_svg__a)"><path fill="current" d="M11.298 11.997a2.6 2.6 0 0 1-1.069-.206 2.6 2.6 0 0 1-.885-.62 2.9 2.9 0 0 1-.612-.944 2.8 2.8 0 0 1-.196-1.1c.016-.562.136-1.115.355-1.634.236-.6.55-1.167.932-1.69a5.3 5.3 0 0 1 1.345-1.295c.43-.312.946-.488 1.48-.507.21-.012.418.05.585.175a.46.46 0 0 1 .199.346.68.68 0 0 1-.177.351 5 5 0 0 1-.45.512q-.278.275-.492.6c-.147.199-.231.434-.244.679 0 .257.312.402.415.45.2.092.425.195.667.313.253.147.457.362.588.62.202.37.3.787.286 1.207.016.364-.043.726-.172 1.068-.129.34-.326.653-.58.919a2.6 2.6 0 0 1-.905.583c-.34.13-.705.19-1.07.173m-6.509 0a2.6 2.6 0 0 1-1.068-.206 2.6 2.6 0 0 1-.885-.62 2.9 2.9 0 0 1-.612-.944 2.8 2.8 0 0 1-.196-1.1c.016-.562.136-1.115.355-1.634a7.6 7.6 0 0 1 .932-1.69A5.3 5.3 0 0 1 4.66 4.507c.43-.312.946-.488 1.481-.507a.9.9 0 0 1 .583.175.46.46 0 0 1 .199.346c0 .048-.029.191-.296.486a19 19 0 0 0-.69.803 1.4 1.4 0 0 0-.38.853c0 .257.312.402.415.45.199.092.425.195.666.313.253.147.458.362.589.62.202.37.3.787.285 1.207a2.7 2.7 0 0 1-.171 1.068 2.7 2.7 0 0 1-.58.919 2.6 2.6 0 0 1-.904.582c-.34.13-.703.19-1.068.174"></path></g><defs><clipPath id="ico_review_svg__a"><path fill="#fff" d="M.027 0h16v16h-16z"></path></clipPath></defs></svg><span class="font-medium text-blue-800">최고예요</span></div></div></div></div></div></div></div>

## 5. 수행 단계

1. `kyobobook/scripts/` 폴더 내에 스크래핑 스크립트 작성 (`fetch_best_sellers.py` 등).
2. 수집된 데이터를 `data/raw/`에 저장.
3. 데이터 정제 후 `data/processed/`에 저장.
4. `notebooks/`에서 기초 통계 및 시각화 분석 수행.
