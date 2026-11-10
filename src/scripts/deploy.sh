#!/usr/bin/env bash
# Deploy na EC2: atualiza o código e recria os containers.
# Uso (dentro de src/):  ./scripts/deploy.sh
set -euo pipefail
cd "$(dirname "$0")/.."

if docker compose version >/dev/null 2>&1; then DC="docker compose"; else DC="docker-compose"; fi

[ -f .env ] || { echo "ERRO: crie o .env a partir do .env.example"; exit 1; }

# Rollback: guarda o commit atual e faz backup do banco antes de atualizar.
ANTERIOR="$(git rev-parse --short HEAD)"
echo ">> commit atual: $ANTERIOR (para voltar: git checkout $ANTERIOR && $DC up -d --build)"
if $DC ps --status running db 2>/dev/null | grep -q db; then
  echo ">> backup pre-deploy"; ./scripts/backup.sh || echo "AVISO: backup falhou"
fi

echo ">> git pull"
git pull --ff-only

echo ">> build + up"
$DC up -d --build

echo ">> aguardando health check..."
for i in $(seq 1 30); do
  if curl -fsS "http://127.0.0.1:${WEB_PORT:-8000}/health/" >/dev/null 2>&1; then
    echo ">> OK: API respondendo"; $DC ps; exit 0
  fi
  sleep 2
done
echo "ERRO: API não respondeu a tempo. Veja: $DC logs web"; exit 1
