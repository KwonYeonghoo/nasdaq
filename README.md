# 나스닥 나랑해❤️

**아침에 화장실에서 한 눈에 확인 가능한 AI융합 주식정보 제공 서비스**

![Service Logo](https://github.com/KwonYeonghoo/nasdaq/tree/main/logo.png)

---

## 프로젝트 개요 📈

**나스닥 나랑해❤️**는 AI를 활용하여 나스닥100을 중심으로 주요 주식 정보를 제공하는 서비스입니다.<br>바쁜 아침, 간편하게 주식 정보를 확인할 수 있도록 도와드립니다.

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

---

### 프로젝트 아키텍처
![나스닥나랑해_아키텍처 (2)](https://github.com/KwonYeonghoo/nasdaq/assets/100892536/05af0516-388c-40fc-b713-4ff9eed604b0)

---

### 데이터 수집 및 분석

- 뉴스, 공시자료, 과거 주가 데이터를 활용한 정형&비정형 데이터 수집 및 분석
- Google Gemini 모델을 활용하여 뉴스와 공시자료 요약 및 분석
- 매일 업데이트되는 뉴스와 분기/년도 별로 업데이트되는 공시자료 분석
- **AirFlow를 통해 위의 과정들 자동화**

---

## 백엔드 구현 상세 ⚙️

### 데이터 수집의 자동화 및 관측성(Observability) 향상
- 기존에 사용하던 파이썬의 schedule 모듈에서 각 함수의 태스크 단위 실행 및 관측성 개
선의 필요성을 체감하여 Airflow로 전환
  - 데이터 수집 및 DB 적재 태스크를 병렬로 수행하여 실행 시간 단축
    - 기존 순차적으로 실행하던 때와 비교해 약 30분 절약
  - AWS EC2에 Airflow 환경을 구축하여 매일 아침 6시에 태스크 수행
    - Graph를 통해 직관적인 실행 흐름 확인 가능
    - <img width="1491" alt="스크린샷 2024-06-17 오전 12 16 45" src="https://github.com/KwonYeonghoo/nasdaq/assets/100892536/39157ece-7de1-4638-b051-4691bd68d3ab">

### 비용 효율적인 LLM 모델 선정
- 토큰 단위가 아닌 글자 단위의 가격 정책을 적용하는 Gemini Pro 모델 사용
  - 한국어는 토큰을 더 많이 사용하므로, GPT보다 비용 측면에서 효율적

### Gemini 모델 최적화
- 창의적 답변을 제한하기 위해 temperature 파라미터를 0.8에서 0.5로 하향 조정
- 필요 이상으로 긴 답변을 제한하기 위해 max_output_token 을 250 토큰으로 제한
- 프롬프트에 원하는 답변 템플릿을 제공하여 답변의 일관성 유지

### REST 아키텍쳐에 기반한 API 작성
- 협업의 중요성을 고려하여 직관적인 설계와 사용이 가능한 REST API 작성
  - GET, POST 등 HTTP 메소드를 활용하여 자원 관리 용이
  - Swagger UI를 통한 API 문서화 및 효율적인 테스트 과정 관리
    - 실시간으로 API를 테스트하고 검증하여 개발 속도 향상
    - <img width="1495" alt="스크린샷 2024-06-16 오후 11 54 57" src="https://github.com/KwonYeonghoo/nasdaq/assets/100892536/2191261f-a1d2-417c-b994-383e7a860fc5">

### 서로다른 에러를 각각 다르게 처리
- 400, 404, 500에러 등등
- ExceptionHandler를 통해 각각의 에러에 대해 서로 다른 로직을 작성
- <img width="905" alt="스크린샷 2024-06-17 오전 12 18 57" src="https://github.com/KwonYeonghoo/nasdaq/assets/100892536/524fb0bc-46d3-428e-ae56-67adbd792934">

### SpringBoot JPA 복합키 구현 문제 해결
- 단순히 @Id 어노테이션을 여러 개 사용하는 것으로는 부족하여 @EmbeddedId 어노테이션
을 사용
  - @Embeddable 로 선언된 복합키 클래스를 작성하여 JPA 엔터티에서 복합키를 정의하
고 관리

### 협업을 위한 공용 DB
- 협업자 모두가 사용할 수 있는 DB를 AWS RDS를 통해 생성
  - EC2에서 MySQL을 호스팅하는 것도 고려했으나, RDS의 1년 무료 이용 혜택을 활용
  - ![스크린샷 2024-06-17 오전 12 22 07](https://github.com/KwonYeonghoo/nasdaq/assets/100892536/b29326d2-549f-4692-b390-9980b5e9f342)

### RDS와 함께 S3 활용
- 뉴스 원문이나 공시 리포트를 DB에 적재하기에는 텍스트가 너무 길다는 판단
    - S3에 데이터를 저장하고, S3 객체 키를 DB에 저장하여 데이터에 접근하는 방식으로 변경 (비용 문제🙅‍♂️)
    - <img width="1154" alt="스크린샷 2024-06-17 오전 12 20 04" src="https://github.com/KwonYeonghoo/nasdaq/assets/100892536/3f4ade83-65b2-47b8-a997-94af94fc7739">

### CI/CD 자동화를 위한 AWS CodePipeline
- AWS CodePipeline을 활용하여 6월 안으로 CI/CD 파이프라인 구축 예정!

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
