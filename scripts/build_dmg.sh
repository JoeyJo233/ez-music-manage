#!/usr/bin/env bash

set -euo pipefail

APP_NAME="EZ Music Manage.app"
VOLUME_NAME="EZ Music Manage"
DIST_DIR="dist"
APP_PATH="${DIST_DIR}/${APP_NAME}"
DMG_PATH="${DIST_DIR}/EZ Music Manage.dmg"
STAGING_DIR="$(mktemp -d)"

cleanup() {
  rm -rf "${STAGING_DIR}"
}

trap cleanup EXIT

if [[ ! -d "${APP_PATH}" ]]; then
  echo "Missing app bundle: ${APP_PATH}" >&2
  echo "Build the app first with: uv run --with pyinstaller pyinstaller -y ez_music_manage.spec" >&2
  exit 1
fi

cp -R "${APP_PATH}" "${STAGING_DIR}/"
ln -s /Applications "${STAGING_DIR}/Applications"

hdiutil create \
  -volname "${VOLUME_NAME}" \
  -srcfolder "${STAGING_DIR}" \
  -ov \
  -format UDZO \
  "${DMG_PATH}"

echo "Created ${DMG_PATH}"
