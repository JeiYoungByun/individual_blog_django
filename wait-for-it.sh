#!/bin/bash
# wait-for-it.sh: Ư�� ȣ��Ʈ�� ��Ʈ�� �غ�� ������ ����ϴ� ��ũ��Ʈ

# ����: ./wait-for-it.sh HOST PORT [TIMEOUT] [COMMAND...]
if [ "$#" -lt 2 ]; then
  echo "Usage: $0 host port [timeout] [command...]"
  exit 1
fi

HOST="$1"
PORT="$2"
TIMEOUT="${3:-30}"  # �⺻ Ÿ�Ӿƿ��� 30��

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

# �߰� ��ɾ �ִٸ� ���� (��: �� ���� ����)
if [ "$#" -gt 3 ]; then
  shift 3
  exec "$@"
fi
