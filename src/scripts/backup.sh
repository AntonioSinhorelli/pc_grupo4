#!/usr/bin/env bash
# Backup lógico do PostgreSQL (pg_dump) com retenção dos 7 mais recentes.
# Uso (dentro de src/):  ./scripts/backup.sh
# Restore: gunzip -c backups/ARQUIVO.sql.gz | docker compose exec -T db sh -c 'psql -U "$POSTGRES_USER" "$POSTGRES_DB"'
set -euo pipefail
cd "$(dirname "$0")/.."

if docker compose version >/dev/null 2>&1; then DC="docker compose"; else DC="docker-compose"; fi

mkdir -p backups
arquivo="backups/lastmile_$(date +%Y-%m-%d_%H%M%S).sql.gz"

# As variáveis POSTGRES_* já existem dentro do container db
$DC exec -T db sh -c 'pg_dump -U "$POSTGRES_USER" "$POSTGRES_DB"' | gzip > "$arquivo"
echo "Backup criado: $arquivo ($(du -h "$arquivo" | cut -f1))"

ls -1t backups/*.sql.gz | tail -n +8 | xargs -r rm --
