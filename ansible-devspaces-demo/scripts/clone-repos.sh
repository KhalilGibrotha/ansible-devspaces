#!/bin/bash

set -euo pipefail

SCRIPT_DIR=$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)
cd "$SCRIPT_DIR/.."

REPO_LIST="repos-to-clone.txt"
CLONE_ROOT=".workspace"

if [[ ! -f $REPO_LIST ]]; then
    echo "Repository list $REPO_LIST not found." >&2
    exit 1
fi

mkdir -p "$CLONE_ROOT"

trim() {
    local s="$1"
    s="${s%%#*}"
    s="${s#${s%%[![:space:]]*}}"
    s="${s%${s##*[![:space:]]}}"
    printf '%s' "$s"
}

while IFS= read -r line || [[ -n $line ]]; do
    line=$(trim "$line")
    [[ -z $line ]] && continue

    url=""
    dest=""
    read -r url dest <<< "$line"

    if [[ -z $url ]]; then
        echo "Skipping malformed line: $line" >&2
        continue
    fi

    if [[ $url == *"/tree/"* ]]; then
        base_repo="${url%%/tree/*}.git"
        branch_and_path="${url#*/tree/}"
        branch="${branch_and_path%%/*}"
        subpath="${branch_and_path#*/}"
        [[ $subpath == "$branch" ]] && subpath=""

        if [[ -z $subpath ]]; then
            echo "Sparse checkout requested without subpath for $url" >&2
            continue
        fi

        repo_name="${base_repo##*/}"
        repo_name="${repo_name%.git}"
        dest_dir="${dest:-${repo_name}-${subpath//\//-}}"
        dest_dir="$CLONE_ROOT/$dest_dir"

        if [[ -d $dest_dir ]]; then
            echo "Skipping $dest_dir (already present)."
            continue
        fi

        git clone --depth 1 --filter=blob:none --no-checkout -b "$branch" "$base_repo" "$dest_dir"
        pushd "$dest_dir" >/dev/null
        git sparse-checkout init --cone
        git sparse-checkout set "$subpath"
        git checkout "$branch"
        popd >/dev/null
    else
        repo_name="${url##*/}"
        repo_name="${repo_name%.git}"
        dest_dir="${dest:-$repo_name}"
        dest_dir="$CLONE_ROOT/$dest_dir"

        if [[ -d $dest_dir ]]; then
            echo "Skipping $dest_dir (already present)."
            continue
        fi

        git clone "$url" "$dest_dir"
    fi
done < "$REPO_LIST"

echo "All repositories processed."
