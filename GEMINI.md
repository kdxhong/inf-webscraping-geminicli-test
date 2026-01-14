# Project Context: Web Scraping & AI Analysis Agent

## Project Overview

이 프로젝트는 파이썬을 기반으로 한 **웹 스크래핑, 데이터 분석, 그리고 예측 모델링**을 수행하는 자동화 에이전트 환경입니다. Gemini CLI를 통해 복잡한 데이터 수집 및 분석 태스크를 효율적으로 수행하는 것을 목표로 합니다.

## Project Structure

루트 디렉토리에는 공용 가상환경이 위치하며, 실제 작업은 프로젝트별 폴더 내에서 수행됩니다:

- `.venv/`: 프로젝트 전체에서 공유하는 고속 가상환경 (Root)
- `common/`: 프로젝트 간 공유되는 공용 모듈 및 유틸리티
- `{project_name}/`: 개별 태스크/프로젝트 폴더
  - `scripts/`: 스크래핑 및 전처리 스크립트
  - `data/`: 프로젝트 전용 데이터 (raw, processed)
  - `models/`: 학습된 모델 파일
  - `notebooks/`: EDA 및 실험용 Notebook

## Setup Guide (using `uv`)

### 1. 가상환경 생성 및 패키지 설치

루트 디렉토리에서 가상환경을 한 번만 생성하여 모든 프로젝트 폴더에서 공유합니다.

```powershell
# 가상환경 생성 (루트에서 수행)
uv venv

# 가상환경 활성화
.venv\Scripts\activate

# 주요 의존성 설치

uv pip install requests beautifulsoup4 selenium pandas numpy matplotlib seaborn scikit-learn jupyter koreanize-matplotlib loguru

```

## Special Configurations

### Logging (Loguru)

표준 `logging` 모듈 대신 직관적이고 강력한 `loguru` 라이브러리를 사용합니다.

별도의 복잡한 설정 없이 즉시 파일 로깅 및 포맷팅된 출력이 가능합니다.

```python

from loguru import logger



# 파일 로깅 추가 (프로젝트 폴더 내 logs/ 디렉토리에 저장 권장)

logger.add("logs/project.log", rotation="500 MB")



logger.info("작업을 시작합니다.")

logger.error("에러 발생 시 기록됩니다.")

```

### Visualization (Korean Font)

Matplotlib 시각화 시 한글 깨짐 방지를 위해 `koreanize-matplotlib` 라이브러리를 사용합니다.

별도의 복잡한 설정 없이 임포트만으로 모든 그래프에서 한글이 정상 출력됩니다.

```python
import matplotlib.pyplot as plt
import koreanize_matplotlib

# 이후 그래프 작성 시 한글이 자동으로 지원됨
plt.title('한글 제목 테스트')
plt.show()
```

- seaborn의 스타일 설정은 사용하지 말 것

### Agent Instructions for Future Tasks

이 프로젝트에서 작업을 수행할 때 Gemini CLI 에이전트는 다음 원칙을 따릅니다:

1. **데이터 보안**: 스크래핑 시 `robots.txt`를 존중하고 적절한 지연 시간(delay)을 둡니다.
2. **프로젝트 격리**: 모든 스크립트와 데이터는 해당 `{project_name}/` 폴더 내에서 관리합니다.
3. **데이터 보존**: 가공 전 원본 데이터는 반드시 프로젝트 내 `data/raw/` 경로에 보존합니다.
4. **재현성**: 모든 분석 및 모델링 과정은 루트의 `.venv` 환경 내에서 재현 가능해야 합니다.
5. **한글 지원**: 시각화 시 `koreanize-matplotlib`을 활용하여 한글이 정상적으로 출력되도록 합니다.
6. **로깅**: 모든 프로젝트 스크립트에는 `loguru`를 사용하여 주요 진행 상황과 오류를 기록합니다.

---

## 데이터 수집에 꼭 필요한 핵심 정보로 꼭 문서에 포함 할 것

### 네트워크 메뉴를 통해 실제 데이터를 가져오는 URL

### 해당 Request에 대한 Header 정보

### Payload

### 응답 예시 (HTML, JSON 의 일부 정보)

_이 파일은 프로젝트의 마스터 가이드라인입니다. 새로운 기능을 추가하거나 라이브러리를 설치할 때 이 문서를 참조하고 업데이트하십시오._
