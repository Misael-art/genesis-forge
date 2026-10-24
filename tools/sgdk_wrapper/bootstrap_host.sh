#!/usr/bin/env bash
# First entry on a blank supported Linux host: bash (no pwsh/python required).
set -euo pipefail
script_dir="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"
apply=false
system_packages=true
for arg in "$@"; do
    [[ "$arg" != --apply ]] || apply=true
    [[ "$arg" != --skip-system-packages ]] || system_packages=false
done
if [[ "$(uname -s)" != Linux || "$(uname -m)" != x86_64 ]]; then
    echo 'bootstrap_status=blocked reason=requires_linux_x86_64' >&2; exit 2
fi
if $apply && $system_packages; then
    # Distribution package manager authenticates packages. No curl|sh, extra
    # repository, global pip install or host-wide environment mutation.
    source /etc/os-release
    if ! { [[ "$ID" == ubuntu && "$VERSION_ID" == 24.04 ]] ||
           [[ "$ID" == debian && ( "$VERSION_ID" == 12 || "$VERSION_ID" == 13 ) ]]; }; then
        echo 'bootstrap_status=blocked reason=apt_distribution_not_qualified use_skip_system_packages_after_manual_setup' >&2; exit 2
    fi
    if [[ "$EUID" == 0 ]]; then
        echo 'bootstrap_status=blocked reason=run_as_developer_not_root_flatpak_is_user_scoped' >&2; exit 2
    fi
    command -v sudo >/dev/null || { echo 'bootstrap_status=blocked reason=sudo_missing' >&2; exit 2; }
    sudo apt-get update
    # The JSON is canonical, but a blank host may not have Python yet.
    sudo apt-get install -y --no-install-recommends python3 python3-venv ca-certificates
    mapfile -t packages < <(python3 -c 'import json,sys; print("\n".join(json.load(open(sys.argv[1]))["apt_packages"]))' "$script_dir/bootstrap_host.json")
    sudo apt-get install -y --no-install-recommends "${packages[@]}"
fi
command -v python3 >/dev/null || { echo 'bootstrap_status=blocked reason=python3_missing run_with_apply_on_supported_apt_host' >&2; exit 2; }
args=()
for arg in "$@"; do [[ "$arg" == --skip-system-packages ]] || args+=("$arg"); done
exec python3 "$script_dir/bootstrap_host.py" "${args[@]}"
