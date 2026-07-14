#!/bin/bash

set -euo pipefail

SCRIPT_DIR=$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)
cd "$SCRIPT_DIR/.."

REPO_LIST="repos-to-clone.txt"
CLONE_ROOT="${CLONE_ROOT:-../workspace-repos}"

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
    branch_override=""
    read -r url dest branch_override <<< "$line"

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

        repo_name="${base_repo##*/}"
        repo_name="${repo_name%.git}"
        if [[ -z $subpath ]]; then
            dest_dir="${dest:-$repo_name}"
        else
            dest_dir="${dest:-${repo_name}-${subpath//\//-}}"
        fi
        dest_dir="$CLONE_ROOT/$dest_dir"

        if [[ -d $dest_dir ]]; then
            echo "Skipping $dest_dir (already present)."
            continue
        fi

        git clone --depth 1 --filter=blob:none --no-checkout -b "$branch" "$base_repo" "$dest_dir"
        if [[ -n $subpath ]]; then
            pushd "$dest_dir" >/dev/null
            git sparse-checkout init --cone
            git sparse-checkout set "$subpath"
            git checkout "$branch"
            popd >/dev/null
        fi
    else
        repo_name="${url##*/}"
        repo_name="${repo_name%.git}"
        dest_dir="${dest:-$repo_name}"
        dest_dir="$CLONE_ROOT/$dest_dir"

        if [[ -d $dest_dir ]]; then
            echo "Skipping $dest_dir (already present)."
            continue
        fi

        if [[ -n $branch_override ]]; then
            git clone --branch "$branch_override" "$url" "$dest_dir"
        else
            git clone "$url" "$dest_dir"
        fi
    fi
done < "$REPO_LIST"

echo "All repositories processed."
echo "Repositories available under $CLONE_ROOT/"
