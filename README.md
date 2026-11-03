# 🚗 OpenCV 기반 ADAS 차선 이탈 경고 (LDW) 시스템 및 로직 검증

## 📌 프로젝트 소개
- 블랙박스 주행 영상을 활용하여 실시간으로 차선을 검출하고, 차량 중앙과 차선 중앙의 오프셋(Offset)을 계산하여 **차선 이탈 및 변경 상태(Safe, Left Departure, Right Lane Change)**를 판별하고 시각화하는 컴퓨터 비전 시스템입니다.
- 소프트웨어 품질 및 알고리즘 동작의 신뢰성을 검증하기 위한 테스트 관점에서 구현되었습니다.

---

## 🛠️ 주요 기술 스택 및 개념
- **Language**: Python
- **Library**: OpenCV, NumPy, ImageIO
- **Key Concepts**:
  - **ROI (Region of Interest)**: 불필요한 배경 영역을 제거하고 도로 주행 영역 추출
  - **Canny Edge & Hough Transform**: 에지 검출 및 직선(차선) 후보군 추출
  - **Perspective Transform (Bird's-Eye View)**: 원근 왜곡(사다리꼴)을 제거하여 정밀한 거리 계산을 수행하는 탑뷰 변환 및 역변환
  - **LDW Logic & Threshold**: 히스토그램 분석 기반 좌우 차선 중심점 도출 및 임계값(±50픽셀) 기준 이탈 판별

---

## 💻 실행 결과 (Result)
> 아래와 같이 정상 주행 시에는 초록색 영역과 `Safe` 상태가 표시되며, 차선 이탈 및 변경 시에는 경고 문구가 출력됩니다.

<img width="478" height="270" alt="output_lane_result2" src="https://github.com/user-attachments/assets/803791c0-8d26-445a-83dd-63d24ad1afec" />

<img width="2672" height="1426" alt="safe_driving" src="https://github.com/user-attachments/assets/e7359590-e35f-44cc-9347-263535279f91" />

<img width="2642" height="1420" alt="right_lane" src="https://github.com/user-attachments/assets/d74087b8-6a78-409a-b11a-51c52b6274d4" />


---

## 🔍 QA 및 검증 관점의 트러블슈팅
- **원근 왜곡 및 오탐지 방지**: 초기 블랙박스 시점에서의 거리 계산 한계를 극복하기 위해 버드아이뷰 변환 행렬과 `src_pts` 좌표를 튜닝하여 차선 인식 정확도 검증
- **시각화 가인성 확보**: 역변환(Inverse Perspective Transform) 기술을 적용해 원본 주행 화면 위에 오버레이 시각화를 구현하고, 상태별 텍스트 색상 분기로 직관성 강화
