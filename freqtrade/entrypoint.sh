#!/bin/sh
set -e

echo "🤖 janostrader bot: ${BOT_NAME}"
echo "📡 Buscando config do hub: ${HUB_URL}/internal/config/${BOT_NAME}"

# Tenta buscar config do hub (até 30s)
RETRIES=6
CONFIG=""
while [ $RETRIES -gt 0 ]; do
    CONFIG=$(curl -sf -H "X-Internal-Key: ${INTERNAL_KEY}" "${HUB_URL}/internal/config/${BOT_NAME}" 2>/dev/null || true)
    if [ -n "$CONFIG" ]; then
        break
    fi
    echo "⏳ Hub não disponível ainda, tentando em 5s... ($RETRIES restantes)"
    sleep 5
    RETRIES=$((RETRIES - 1))
done

mkdir -p /freqtrade/user_data/logs /freqtrade/user_data/data

if [ -n "$CONFIG" ]; then
    echo "$CONFIG" > /freqtrade/config.json
    # Cache local para fallback
    cp /freqtrade/config.json /freqtrade/user_data/config_cache.json
    echo "✅ Config recebida do hub"
elif [ -f /freqtrade/user_data/config_cache.json ]; then
    echo "⚠️  Hub indisponível — usando config em cache"
    cp /freqtrade/user_data/config_cache.json /freqtrade/config.json
else
    echo "❌ Hub indisponível e sem cache. Abortando."
    exit 1
fi

# Heartbeat em background: avisa o hub a cada 60s que o bot está vivo
heartbeat() {
    while true; do
        sleep 60
        curl -sf \
            -X POST \
            -H "X-Internal-Key: ${INTERNAL_KEY}" \
            "${HUB_URL}/internal/heartbeat/${BOT_NAME}" \
            >/dev/null 2>&1 || true
    done
}
heartbeat &

exec freqtrade "$@"
