#!/usr/bin/env bash

set -euo pipefail

CUSTOM_PNG="assets/icon/source/app_icon_1024.png"
CUSTOM_PNG_512="assets/icon/source/app_icon_512.png"
SOURCE_SVG="assets/icon/emm_app_icon.svg"
ICONSET_DIR="assets/icon/emm.iconset"
ICON_PATH="assets/icon/emm_app_icon.icns"
SOURCE_PNG="assets/icon/emm_app_icon_source.png"
MASTER_PNG="assets/icon/emm_app_icon.png"

rm -rf "${ICONSET_DIR}"
mkdir -p "${ICONSET_DIR}"

if [[ -f "${CUSTOM_PNG_512}" ]]; then
  # 512px source: squircle already applied by IconKitchen, use as-is
  cp "${CUSTOM_PNG_512}" "${MASTER_PNG}"
elif [[ -f "${CUSTOM_PNG}" ]]; then
  cp "${CUSTOM_PNG}" "${SOURCE_PNG}"
  uv run python scripts/round_icon.py "${SOURCE_PNG}" "${MASTER_PNG}"
else
  qlmanage -t -s 1024 -o assets/icon "${SOURCE_SVG}" >/dev/null
  mv assets/icon/emm_app_icon.svg.png "${SOURCE_PNG}"
  uv run python scripts/round_icon.py "${SOURCE_PNG}" "${MASTER_PNG}"
fi

sips -z 16 16 "${MASTER_PNG}" --out "${ICONSET_DIR}/icon_16x16.png" >/dev/null
sips -z 32 32 "${MASTER_PNG}" --out "${ICONSET_DIR}/icon_16x16@2x.png" >/dev/null
sips -z 32 32 "${MASTER_PNG}" --out "${ICONSET_DIR}/icon_32x32.png" >/dev/null
sips -z 64 64 "${MASTER_PNG}" --out "${ICONSET_DIR}/icon_32x32@2x.png" >/dev/null
sips -z 128 128 "${MASTER_PNG}" --out "${ICONSET_DIR}/icon_128x128.png" >/dev/null
sips -z 256 256 "${MASTER_PNG}" --out "${ICONSET_DIR}/icon_128x128@2x.png" >/dev/null
sips -z 256 256 "${MASTER_PNG}" --out "${ICONSET_DIR}/icon_256x256.png" >/dev/null
sips -z 512 512 "${MASTER_PNG}" --out "${ICONSET_DIR}/icon_256x256@2x.png" >/dev/null
cp "${MASTER_PNG}" "${ICONSET_DIR}/icon_512x512.png"
cp "${MASTER_PNG}" "${ICONSET_DIR}/icon_512x512@2x.png"

iconutil -c icns "${ICONSET_DIR}" -o "${ICON_PATH}"

echo "Created ${ICON_PATH}"
