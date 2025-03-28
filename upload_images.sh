#!/bin/bash

usage() {
    echo "Uso: $0 [-u|--url <url_de_la_api>] [-p|--path <ruta_de_la_carpeta_con_imagenes>]"
    echo "Ejemplo: $0 -u http://3.128.67.173:8000/images/ -p /home/ubuntu/dismac"
    echo "Si no se proporcionan argumentos, se usa http://127.0.0.1:8000/images/ y /home/ubuntu/uploads por defecto."
    exit 1
}

API_URL="http://127.0.0.1:8000/images/"
SOURCE_DIR="/home/ubuntu/uploads"

while [[ "$#" -gt 0 ]]; do
    case $1 in
        -u|--url) API_URL="$2"; shift ;;
        -p|--path) SOURCE_DIR="$2"; shift ;;
        -h|--help) usage ;;
        *) echo "Argumento desconocido: $1"; usage ;;
    esac
    shift
done

if [[ ! "$API_URL" =~ /images/?$ ]]; then
    API_URL="${API_URL%/}/images/"
fi

if [ ! -d "$SOURCE_DIR" ]; then
    echo "Error: La carpeta '$SOURCE_DIR' no existe."
    exit 1
fi

IMAGES=$(find "$SOURCE_DIR" -type f \( -iname "*.png" -o -iname "*.jpg" -o -iname "*.jpeg" -o -iname "*.gif" -o -iname "*.bmp" \) | sort -V)

if [ -z "$IMAGES" ]; then
    echo "Error: No se encontraron imágenes en '$SOURCE_DIR'."
    exit 1
fi

TOTAL=$(echo "$IMAGES" | wc -l)
COUNT=0

echo "Subiendo $TOTAL imágenes desde '$SOURCE_DIR' a '$API_URL'..."

while IFS= read -r IMAGE; do
    ((COUNT++))
    FILENAME=$(basename "$IMAGE")
    echo "[$COUNT/$TOTAL] Subiendo: $FILENAME"

    RESPONSE=$(curl -s -w "%{http_code}" -o /tmp/curl_response \
        -X POST "$API_URL" \
        -F "nombre=$FILENAME" \
        -F "file=@$IMAGE;type=image/jpeg")

    if [ "$RESPONSE" -eq 200 ]; then
        echo "[$COUNT/$TOTAL] Subida exitosa: $FILENAME"
    else
        echo "[$COUNT/$TOTAL] Error subiendo $FILENAME: Código HTTP $RESPONSE"
        cat /tmp/curl_response
    fi
done <<< "$IMAGES"

rm -f /tmp/curl_response

echo "Proceso completado: $COUNT imágenes procesadas."