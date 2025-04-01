#!/bin/bash

API_URL="http://127.0.0.1:8000"
SOURCE_DIR="/home/ubuntu/uploads"
USERNAME="admin"
PASSWORD="admin"

while [[ "$#" -gt 0 ]]; do
    case $1 in
        -u|--url) API_URL="$2"; shift ;;
        -p|--path) SOURCE_DIR="$2"; shift ;;
        -h|--help) echo "Uso: $0 [-u|--url <url>] [-p|--path <ruta>]"; exit 1 ;;
        *) echo "Argumento desconocido: $1"; exit 1 ;;
    esac
    shift
done

if [[ ! "$API_URL" =~ /$ ]]; then
    API_URL="${API_URL%/}"
fi

if [ ! -d "$SOURCE_DIR" ]; then
    echo "Error: La carpeta '$SOURCE_DIR' no existe."
    exit 1
fi

API_KEY=$(psql -U postgres -d dismac -t -c "SELECT api_key FROM users WHERE username='$USERNAME'" | tr -d '[:space:]')

TOKEN_RESPONSE=$(curl -s -X POST "${API_URL}/auth/login" \
    -H "apikey: $API_KEY" \
    -d "username=$USERNAME&password=$PASSWORD")

TOKEN=$(echo "$TOKEN_RESPONSE" | grep -o '"access_token":"[^"]*' | cut -d'"' -f4)

if [ -z "$TOKEN" ]; then
    echo "Error: No se pudo obtener el token. Respuesta: $TOKEN_RESPONSE"
    exit 1
fi

IMAGES=$(find "$SOURCE_DIR" -type f \( -iname "*.png" -o -iname "*.jpg" -o -iname "*.jpeg" -o -iname "*.gif" -o -iname "*.bmp" \) | sort -V)

if [ -z "$IMAGES" ]; then
    echo "Error: No se encontraron imÃ¡genes en '$SOURCE_DIR'."
    exit 1
fi

TOTAL=$(echo "$IMAGES" | wc -l)
COUNT=0

echo "Subiendo $TOTAL imÃ¡genes desde '$SOURCE_DIR' a '${API_URL}/images/'..."

while IFS= read -r IMAGE; do
    ((COUNT++))
    FILENAME=$(basename "$IMAGE")
    echo "[$COUNT/$TOTAL] Subiendo: $FILENAME"

    RESPONSE=$(curl -s -w "%{http_code}" -o /tmp/curl_response \
        -X POST "${API_URL}/images/" \
        -H "Authorization: Bearer $TOKEN" \
        -H "apikey: $API_KEY" \
        -F "name=$FILENAME" \
        -F "file=@$IMAGE;type=image/jpeg")

    if [ "$RESPONSE" -eq 200 ]; then
        echo "[$COUNT/$TOTAL] Subida exitosa: $FILENAME"
    else
        echo "[$COUNT/$TOTAL] Error subiendo $FILENAME: CÃ³digo HTTP $RESPONSE"
        cat /tmp/curl_response
    fi
done <<< "$IMAGES"

rm -f /tmp/curl_response

echo "Proceso completado: $COUNT imÃ¡genes procesadas."
