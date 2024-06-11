# 나스닥 나랑해❤️

**아침에 화장실에서 한 눈에 확인 가능한 AI융합 주식정보 제공 서비스**

![Service Logo](https://github.com/KwonYeonghoo/nasdaq/tree/main/logo.png)

---

## 프로젝트 개요 📈

**나스닥 나랑해❤️**는 AI를 활용하여 나스닥100을 중심으로 주요 주식 정보를 제공하는 서비스입니다. 바쁜 아침, 간편하게 주식 정보를 확인할 수 있도록 도와드립니다.

### 프로젝트 기간
- **2024.05 ~ 진행중**

### 주요 기능
- 📊 주요 주식 뉴스 및 공시자료 요약 제공
- 🔍 과거 주가 데이터 분석
- 🕖 매일 아침 7시에 자동 데이터 수집 및 업데이트

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
- 여러 주식 사이트 (Investing.com, Yahoo Finance, Market Watch 등)에서 빈번하게 눈에 띄는 정보들 정리
- 투자자들의 장바구니에 빅테크주 비중이 가장 큼을 확인
- **나스닥100**을 대상으로 서비스를 우선 제공 결정

### 데이터 수집 및 분석

- 뉴스, 공시자료, 과거 주가 데이터를 활용한 정형&비정형 데이터 수집 및 분석
- Google Gemini 모델을 활용하여 뉴스와 공시자료 요약 및 분석
- 매일 업데이트되는 뉴스와 분기/년도 별로 업데이트되는 공시자료 분석

---

## 백엔드 구현 상세 ⚙️

### 복합키 문제 해결
- SpringBoot JPA 복합키 구현 시, `@Id` 어노테이션만으로는 부족
- `@IdClass` 혹은 `@EmbeddedId` 사용
- `@Embeddable`로 선언된 복합키 클래스 작성

### 협업을 위한 공용 DB
- AWS RDS 사용

### 데이터 수집 자동화
- 파이썬의 schedule 모듈 대신 Airflow 사용
- 데이터 수집 및 DB 적재를 태스크 단위로 수행
- 매일 아침 7시에 태스크 수행

### Gemini 모델 최적화
- 창의적 답변을 제한하기 위해 `temperature` 파라미터를 0.8에서 0.5로 하향 조정
- `max_output_token`을 250 토큰으로 제한

### DB와 S3 활용
- 뉴스 원문이나 공시리포트는 길이가 길어 S3에 저장
- S3 객체 키를 DB에 저장
- 데이터 저장 및 접근 비용이 크지 않음을 확인

---

## 깃허브 링크 🔗
[나스닥 나랑해❤️ GitHub](https://github.com/KwonYeonghoo/nasdaq/tree/main)

---

Feel free to adjust any details to better fit your project.

---
