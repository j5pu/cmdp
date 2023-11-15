#!/bin/bash

set -eu
cd "$(dirname "$0")"
TOP="$(dirname "${PWD}")"

#######################################
# description
# Globals:
#   GIT
#   TOP
#   deps
#   platform
#   project
#   tag
#   version
#   version_platform
# Arguments:
#  None
#######################################
publish() {
  local deps platform project tag version_platform
  project="$(basename "${TOP}")"
  # j5pu/3.11, j5pu/3.12, j5pu/3.11-slim, j5pu/3.12-slim
  # 3.11-nodeps-deps, 3.12-nodeps-deps, 3.11-slim-nodeps-deps-slim, 3.12-slim-nodeps-deps
  for version in 3.11 3.12; do
    for platform in alpine slim; do
      version_platform="${version}-${platform}"
      [ "${platform}" = "slim" ] || version_platform="${version}"
      tag="${GIT}/${version_platform}"
      docker build --target "${platform}" --quiet --build-arg="PY_VERSION=${version}" -t "${tag}" .
      docker push --quiet "${tag}"

      deps="${version_platform}-${project}-deps"
      echo docker build -f deps.dockerfile --quiet --build-arg="IMAGE=${tag}" -t "${GIT}/${deps}" "${TOP}"
      docker build -f deps.dockerfile --quiet --build-arg="IMAGE=${tag}" -t "${GIT}/${deps}" "${TOP}"
      docker push --quiet "${GIT}/${deps}"
    done
  done
  exit
}

#######################################
# description
# Globals:
#   TOKEN
#   a
#   version
# Arguments:
#  None
#######################################
run() {
  local command=(pytest) it=(-it) slim
  case "$1" in
    *bash*) command=(bash -li);;
    *slim*) slim="-slim" ;;
  esac
  version="${1/-*/}"
  [ "${command[0]}" != "pytest" ] || it=(-i)
  echo docker run --env TOKEN="${TOKEN}" "${it[@]}" -v "${TOP}":/nodeps -v \
~/.ssh:/root/.ssh --rm "${GIT}/${version}-${TOP##*/}-deps" "${command[@]}"
  docker run --env TOKEN="${TOKEN}" "${it[@]}" -v "${TOP}":/nodeps -v ~/.ssh:/root/.ssh \
    --rm "${GIT}/${version}-${TOP##*/}-deps" "${command[@]}"
  exit
}

#######################################
# description
# Arguments:
#   1
#######################################
main() {
  [ "$1" = "publish" ] || run "$1"
  publish
}

main "$@"
