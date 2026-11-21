#!/bin/sh
# 빌드 결과만 공개 저장소(dev-donghwan/study-notes, GitHub Pages)로 올린다.
# 원본(src · tools · templates)은 비공개 저장소 study-notes-src 에만 둔다.
#     sh tools/deploy.sh
set -e
ROOT=$(cd "$(dirname "$0")/.." && pwd)
SITE="$ROOT/.site"
cd "$ROOT"
python3 tools/build.py
if [ ! -d "$SITE/.git" ]; then
  git clone -q https://github.com/dev-donghwan/study-notes.git "$SITE" 2>/dev/null || { mkdir -p "$SITE"; git -C "$SITE" init -q -b main; git -C "$SITE" remote add origin https://github.com/dev-donghwan/study-notes.git; }
fi
# 공개할 것: 홈 · 주제 폴더 · assets · LICENSE (sample 은 제외)
find "$SITE" -mindepth 1 -maxdepth 1 ! -name .git -exec rm -rf {} +
cp -R index.html assets LICENSE .nojekyll "$SITE"/
for t in $(python3 -c 'import json;print(" ".join(json.load(open("src/site.json"))["topics"]))'); do cp -R "$t" "$SITE"/; done
cd "$SITE"
git add -A
if git diff --cached --quiet; then echo "변경 없음"; exit 0; fi
git commit -qm "사이트 갱신 $(git -C "$ROOT" rev-parse --short HEAD)"
git push -q -u origin main
echo "배포: https://dev-donghwan.github.io/study-notes/"
