# projects
## 빅데이터프로그래밍응용 수업

### Codespace 실행  
1. **projects** Repo 선택
2. "<> Code" 버튼 - Codespaces 탭 선택
3. "Create codespace on main" 버튼 클릭

### 초기화 단계  
터미널에서 아래 명령 입력  
1. `pip install uv`
2. `uv init`
3. `uv add streamlit pandas seaborn plotly` (이후 streamlit 실행 시 생략 가능)  

### streamlit 파일 실행  
`uv run streamlit run app.py`

### matplotlib, seaborn 차트 한글 사용
쉬운 방법 - koreanize_matplotlib 사용  
아래 모듈을 설치한다.
> setuptools, koreanize-matplotlib  
소스 파일 상단에 `koreanize_matplotlib`를 import 한다.

글꼴 직접 선택하기 - fonts-nanum 설치
터미널에서 아래 명령을 실행한다.
>sudo apt-get install -y fonts-nanum  
>sudo fc-cache -fv  
>rm ~/.cache/matplotlib -rf

코드 내에서 아래 코드를 포함시킨다.  
> import matplotlib.pyplot as plt  
> plt.rc('font', family='NanumGothic')  
> plt.rc('axes', unicode_minus=False)

사용 가능한 글꼴 종류
- NanumBarunGothic
- NanumGothic
- NanumGothicCoding
- NanumMyeongjo
- NanumSquare
- NanumSquare Bold
- NanumSquareRound
- NanumSquareRound Bold
- NanumSquareRound Regular
