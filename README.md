# 나스닥 나랑해❤️

**아침에 화장실에서 한 눈에 확인 가능한 AI융합 주식정보 제공 서비스**

![Service Logo](https://github.com/KwonYeonghoo/nasdaq/tree/main/logo.png)

---

## 프로젝트 개요 📈

**나스닥 나랑해❤️**는 AI를 활용하여 나스닥100을 중심으로 주요 주식 정보를 제공하는 서비스입니다. 
바쁜 아침, 간편하게 주식 정보를 확인할 수 있도록 도와드립니다.

### 프로젝트 기간
- **2024.05 ~ 진행중**

### 주요 기능
- 📊 주요 주식 뉴스 및 공시자료 요약 제공
- 🔍 과거 데이터 기반 5일치 주가 예측
- 🎯 3년치 나스닥 데이터를 기반한 산업군 클러스터링
- 🕖 매일 아침 7시에 자동 데이터 수집 및 업데이트
- 📆 주요 경제일정 캘린더 제공
---

## 기술 스택 🛠️

- **Back-End:** ![Java](https://img.shields.io/badge/Java-ED8B00?style=flat&logo=java&logoColor=white) ![Spring](https://img.shields.io/badge/Spring-6DB33F?style=flat&logo=spring&logoColor=white) ![JPA](https://img.shields.io/badge/JPA-6DB33F?style=flat&logo=hibernate&logoColor=white)
- **Database:** ![MySQL](https://img.shields.io/badge/MySQL-4479A1?style=flat&logo=mysql&logoColor=white) ![AWS RDS](https://img.shields.io/badge/AWS_RDS-527FFF?style=flat&logo=amazon-aws&logoColor=white)
- **Deployment:** ![AWS EC2](https://img.shields.io/badge/AWS_EC2-FF9900?style=flat&logo=amazon-aws&logoColor=white)
- **Automation:** ![Airflow](https://img.shields.io/badge/Airflow-017CEE?style=flat&logo=apache-airflow&logoColor=white)
- **AI 모델:** ![Google Gemini](https://img.shields.io/badge/Google_Gemini-4285F4?style=flat&logo=google&logoColor=white)
- **Storage:** ![AWS S3](https://img.shields.io/badge/AWS_S3-569A31?style=flat&logo=amazon-s3&logoColor=white)

---

## 서비스 소개 🌟

### 서비스 기획

- `내가 진짜 필요한 주식 정보들이 뭘까?`에 대한 고찰에서 시작
- **투자에 필요한 기본적인 정보들을 한 데 모아 확인하는 서비스를 만들자!**
- 여러 주식 사이트 (Investing.com, Yahoo Finance, Market Watch 등)에서 빈번하게 눈에 띄는 정보들 정리
- 투자자들의 장바구니에 빅테크주 비중이 가장 큼을 확인
- **나스닥100**을 대상으로 서비스를 우선 제공 결정


### 데이터 수집 및 분석

- 뉴스, 공시자료, 과거 주가 데이터를 활용한 정형&비정형 데이터 수집 및 분석
- Google Gemini 모델을 활용하여 뉴스와 공시자료 요약 및 분석
- 매일 업데이트되는 뉴스와 분기/년도 별로 업데이트되는 공시자료 분석
- **AirFlow를 통해 위의 과정들 자동화**

---

## 백엔드 구현 상세 ⚙️

### 데이터 수집 자동화
- 파이썬의 schedule 모듈 대신 Airflow 사용
- 데이터 수집 및 DB 적재를 태스크 단위로 수행
- 매일 아침 7시에 태스크 수행
  
### 서로다른 에러를 각각 다르게 처리
- 400, 404, 500에러 등등
- ExceptionHandler를 통해 각각의 에러에 대해 서로 다른 로직을 작성

### 복합키 문제 해결
- SpringBoot JPA 복합키 구현 시, `@Id` 어노테이션만으로는 부족
- `@IdClass` 혹은 `@EmbeddedId` 사용
- `@Embeddable`로 선언된 복합키 클래스 작성

### 협업을 위한 공용 DB
- AWS RDS 사용

### Gemini 모델 최적화
- 창의적 답변을 제한하기 위해 `temperature` 파라미터를 0.8에서 0.5로 하향 조정
- `max_output_token`을 250 토큰으로 제한

### DB와 S3 활용
- 뉴스 원문이나 공시리포트는 길이가 길어 S3에 저장
- S3 객체 키를 DB에 저장
- 데이터 저장 및 접근 비용이 크지 않음을 확인

---
## 서비스 화면
- 메인화면: 검색창, 핫한 산업군 top3와 각 산업군별 best 종목, 등락률 top3 종목
<img width="1496" alt="스크린샷 2024-06-16 오후 11 25 57" src="https://github.com/KwonYeonghoo/nasdaq/assets/100892536/99588891-4656-4a63-b106-05d3bea845af">

- 산업군 클러스터링: 상관관계 분석을 통해 연관성이 가장 높은 산업군 5개 표출
<img width="1496" alt="스크린샷 2024-06-16 오후 11 28 40" src="https://github.com/KwonYeonghoo/nasdaq/assets/100892536/5dcf73e5-d8b9-4e15-800b-35773311e2f9">

- 종목상세 페이지: 간단한 기업정보, 전 날 뉴스요약, 5일치 주가예측, 공시자료 요약, 산업군 재무지표 평균vs종목 재무지표, 볼린저밴드와 주가 차트 & 해석법
<img width="1501" alt="스크린샷 2024-06-16 오후 11 27 05" src="https://github.com/KwonYeonghoo/nasdaq/assets/100892536/eb1d81e6-c53c-41c2-a8c8-2e511a4d02f2">
<img width="1498" alt="스크린샷 2024-06-16 오후 11 28 13" src="https://github.com/KwonYeonghoo/nasdaq/assets/100892536/5703c2d7-75c7-4672-b96f-8ab06a1cca78">
<img width="1500" alt="스크린샷 2024-06-16 오후 11 27 28" src="https://github.com/KwonYeonghoo/nasdaq/assets/100892536/aeac97f8-929c-4200-a892-f3d3370f591c">

- 주요 경제이벤트 캘린더
<img width="1498" alt="스크린샷 2024-06-16 오후 11 29 17" src="https://github.com/KwonYeonghoo/nasdaq/assets/100892536/8f6a55e3-7827-4c0a-9a3f-307600fe7a3c">

---

## 깃허브 링크 🔗
[나스닥 나랑해❤️ GitHub](https://github.com/KwonYeonghoo/nasdaq/tree/main)

---
