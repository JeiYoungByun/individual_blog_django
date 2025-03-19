#!/bin/bash
# wait-for-it.sh: 특정 호스트와 포트가 준비될 때까지 대기하는 스크립트

# 사용법: ./wait-for-it.sh HOST PORT [TIMEOUT] [COMMAND...]
if [ "$#" -lt 2 ]; then
  echo "Usage: $0 host port [timeout] [command...]"
  exit 1
fi

HOST="$1"
PORT="$2"
TIMEOUT="${3:-30}"  # 기본 타임아웃은 30초

echo "Waiting for $HOST:$PORT to be available (timeout: $TIMEOUT seconds)..."

while ! nc -z "$HOST" "$PORT"; do
  sleep 1
  TIMEOUT=$((TIMEOUT-1))
  if [ "$TIMEOUT" -le 0 ]; then
    echo "Timeout occurred while waiting for $HOST:$PORT"
    exit 1
  fi
done

echo "$HOST:$PORT is available!"

# 추가 명령어가 있다면 실행 (예: 웹 서버 시작)
if [ "$#" -gt 3 ]; then
  shift 3
  exec "$@"
fi
