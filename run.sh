#!/usr/bin/env bash
set -euo pipefail

# Build the devcontainer image and tag it as ros2-humble-base:dev
# (the tag docker-compose.yaml and devcontainer.json expect).

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
CONTEXT="${SCRIPT_DIR}"
DOCKERFILE="${SCRIPT_DIR}/.devcontainer/Dockerfile"
IMAGE="ros2-humble-base:dev"

echo ">>> Building ${IMAGE}"
echo "    context:    ${CONTEXT}"
echo "    dockerfile: ${DOCKERFILE}"

docker build \
    -t "${IMAGE}" \
    -f "${DOCKERFILE}" \
    "${CONTEXT}"

echo ">>> Done. Tagged: ${IMAGE}"
docker image inspect "${IMAGE}" --format '    id:      {{.Id}}
    size:    {{.Size}} bytes
    created: {{.Created}}'
