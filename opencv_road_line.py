import cv2
import numpy as np

# 1. 주행 동영상 파일 불러오기
video_path = 'lane_video.mp4'  # 본인 동영상 파일 경로
cap = cv2.VideoCapture(video_path)

if not cap.isOpened():
  print('동영상을 열 수 없습니다. 파일 경로를 확인해주세요.')
  exit()

# 2. 결과 동영상 저장을 위한 설정
fourcc = cv2.VideoWriter_fourcc(*'mp4v')
fps = cap.get(cv2.CAP_PROP_FPS)
if fps == 0:
  fps = 25.0
width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))

# 저장될 결과 파일명 설정
out = cv2.VideoWriter('output_lane_result.mp4', fourcc, fps, (width, height))

while cap.isOpened():
  ret, frame = cap.read()
  if not ret:
    print('동영상이 모두 끝났습니다.')
    break

  # 3. 버드아이뷰(탑뷰) 변환을 위한 원근 영역 설정
  src_pts = np.float32(
      [
          [width * 0.46, height * 0.48],  # 위쪽 왼쪽
          [width * 0.54, height * 0.48],  # 위쪽 오른쪽
          [width * 0.15, height * 0.95],  # 아래쪽 왼쪽
          [width * 0.85, height * 0.95],  # 아래쪽 오른쪽
      ]
  )
  dst_pts = np.float32(
      [
          [width * 0.3, 0],
          [width * 0.7, 0],
          [width * 0.3, height],
          [width * 0.7, height],
      ]
  )

  # 변환 행렬 및 역변환 행렬 계산
  matrix = cv2.getPerspectiveTransform(src_pts, dst_pts)
  inv_matrix = cv2.getPerspectiveTransform(dst_pts, src_pts)

  # 버드아이뷰 이미지 생성
  bird_eye_img = cv2.warpPerspective(frame, matrix, (width, height))

  # 4. 탑뷰 화면 기반 차선 위치 분석 (히스토그램 활용)
  gray_bird = cv2.cvtColor(bird_eye_img, cv2.COLOR_BGR2GRAY)
  _, thresh = cv2.threshold(gray_bird, 200, 255, cv2.THRESH_BINARY)

  bottom_slice = thresh[int(height * 0.7) : height, :]
  histogram = np.sum(bottom_slice, axis=0)
  midpoint = int(histogram.shape[0] / 2)

  left_x = np.argmax(histogram[:midpoint])
  right_x = np.argmax(histogram[midpoint:]) + midpoint

  # 5. 차량 중앙과 차선 중앙 비교를 통한 이탈 감지 (Offset 계산)
  car_center = width / 2
  lane_center = (left_x + right_x) / 2
  offset = car_center - lane_center

  warning_text = 'Safe (Driving)'
  text_color = (0, 255, 0)  # 초록색 (안전)

  if offset > 50:
    warning_text = 'Right Lane Change'
    text_color = (0, 165, 255)  # 주황색 (우측 변경)
  elif offset < -50:
    warning_text = 'Left Lane Departure'
    text_color = (0, 0, 255)  # 빨간색 (좌측 이탈)

  # 6. 탑뷰 공간에 검출된 차선 영역(초록색 면) 및 차선 경계선(노란색) 그리기
  warp_zero = np.zeros_like(bird_eye_img).astype(np.uint8)
  pts = np.array(
      [[left_x, height], [left_x, 0], [right_x, 0], [right_x, height]],
      dtype=np.int32,
  )

  cv2.fillPoly(warp_zero, [pts], (0, 255, 0))  # 내부 초록색 채우기
  cv2.line(warp_zero, (left_x, height), (left_x, 0), (0, 255, 255), 15)  # 좌측 차선
  cv2.line(warp_zero, (right_x, height), (right_x, 0), (0, 255, 255), 15)  # 우측 차선

  # 7. 역변환을 통해 원본 주행 영상 시점으로 오버레이 결합
  unwarp_img = cv2.warpPerspective(warp_zero, inv_matrix, (width, height))
  output_img = cv2.addWeighted(frame, 1, unwarp_img, 0.4, 0)

  # 8. 상단 중앙에 상태 문구(LDW 알림) 텍스트 추가
  cv2.putText(
      output_img,
      warning_text,
      (int(width / 2) - 150, 80),
      cv2.FONT_HERSHEY_SIMPLEX,
      1,
      text_color,
      3,
  )

  # 9. 처리된 프레임 영상 파일로 저장 및 실시간 출력
  out.write(output_img)
  cv2.imshow('Lane Detection Result', output_img)

  if cv2.waitKey(25) & 0xFF == ord('q'):
    break

# 10. 자원 해제 및 마무리
cap.release()
out.release()
cv2.destroyAllWindows()
print('차선 인식 및 결과 영상 저장이 완료되었습니다!')