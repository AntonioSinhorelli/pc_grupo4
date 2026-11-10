#!/bin/sh
# Executado a cada start do container "web".
# Migrations e collectstatic rodam no deploy (requisito B5).
set -e

echo ">> Aplicando migrations..."
python manage.py migrate --noinput

echo ">> Coletando arquivos estáticos..."
python manage.py collectstatic --noinput

echo ">> Garantindo superusuário do Admin..."
python manage.py criar_superusuario

case "$(echo "${SEED_ON_START:-false}" | tr 'A-Z' 'a-z')" in
    true|1|yes|sim)
        echo ">> Carregando dados de exemplo (idempotente)..."
        python manage.py seed_dados
        ;;
esac

echo ">> Iniciando gunicorn na porta 8000..."
exec gunicorn lastmile.wsgi:application \
    --bind 0.0.0.0:8000 \
    --workers "${GUNICORN_WORKERS:-2}" \
    --access-logfile - \
    --error-logfile -
