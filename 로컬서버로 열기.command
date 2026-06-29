#!/bin/bash
# 이 파일을 더블클릭하면 http://localhost 로 앱을 띄웁니다.
# (file:// 더블클릭과 달리, 크롬이 마이크 권한을 기억해서 한 번만 허용하면 됩니다)
cd "$(dirname "$0")"
PORT=8765

# 이미 떠 있으면 그 포트 정리
lsof -ti tcp:$PORT 2>/dev/null | xargs kill -9 2>/dev/null
sleep 1

# 크롬으로 열기 (음성 인식은 크롬에서만 동작)
( sleep 1; open -a "Google Chrome" "http://localhost:$PORT/index.html" 2>/dev/null \
  || open "http://localhost:$PORT/index.html" ) &

echo "▶ 로컬 서버 실행 중: http://localhost:$PORT/index.html"
echo "  창을 닫지 말고 두세요. 종료하려면 이 창에서 Ctrl + C."
python3 -m http.server $PORT
