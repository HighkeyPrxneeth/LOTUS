#!/usr/bin/env bash
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
DEST="$ROOT/.tooling/firefly"
mkdir -p "$DEST/bin"
command -v gcc >/dev/null || { echo 'FireFly SQLite needs gcc and libc6-dev.' >&2; exit 1; }
if [ ! -x "$DEST/go/bin/go" ]; then
  curl -fL --retry 3 https://go.dev/dl/go1.27.2.linux-amd64.tar.gz -o "$DEST/go.tar.gz"
  echo 'ecbadb99091a3f46e31f5f934b068b1864eafa7995211b39eaddf76996045fe5  '"$DEST/go.tar.gz" | sha256sum -c -
  tar -xzf "$DEST/go.tar.gz" -C "$DEST"
fi
export PATH="$DEST/go/bin:$PATH"
export GOPATH="$DEST/go-cache" GOCACHE="$DEST/build-cache" GOTOOLCHAIN=local
for entry in firefly:1.5.0 fabconnect:0.10.0; do
  repo="${entry%%:*}"; version="${entry##*:}"
  if [ ! -d "$DEST/$repo-$version" ]; then
    curl -fL --retry 3 "https://codeload.github.com/hyperledger-firefly/$repo/tar.gz/refs/tags/v$version" -o "$DEST/$repo-source.tar.gz"
    tar -xzf "$DEST/$repo-source.tar.gz" -C "$DEST"
  fi
  (cd "$DEST/$repo-$version" && CGO_ENABLED=1 go build -trimpath -o "$DEST/bin/$repo" -ldflags "-X main.buildVersion=v$version" .)
done
sha256sum "$DEST/bin/firefly" "$DEST/bin/fabconnect" > "$DEST/build-sha256.txt"
echo 'Pinned FireFly 1.5.0 and FabConnect 0.10.0 built.'
