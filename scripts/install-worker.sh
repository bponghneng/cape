#!/usr/bin/env bash
#
# CAPE Worker Installation Script
#
# This script installs and configures the CAPE issue worker daemon
# for both macOS (launchd) and Linux (systemd) platforms.
#
# Usage:
#   ./install-worker.sh <worker-id>
#
# Example:
#   ./install-worker.sh alleycat-1
#

set -euo pipefail

# Configuration
WORKER_ID="${1:-}"
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
CAPE_ROOT="$(cd "${SCRIPT_DIR}/.." && pwd)"
WORKER_SCRIPT="${CAPE_ROOT}/worker.py"
LOGS_DIR="${CAPE_ROOT}/logs"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Functions
log_info() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

log_warn() {
    echo -e "${YELLOW}[WARN]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

usage() {
    cat << EOF
Usage: $0 <worker-id>

Install and configure the CAPE issue worker daemon.

Arguments:
  worker-id    Unique identifier for this worker instance
               (e.g., 'alleycat-1', 'tyderium-1')

Examples:
  $0 alleycat-1
  $0 tyderium-1

The worker will be configured to:
  - Poll for pending issues every 10 seconds
  - Log to ${LOGS_DIR}/worker_<worker-id>.log
  - Auto-restart on failure
  - Run at system startup

EOF
    exit 1
}

check_worker_id() {
    if [[ -z "${WORKER_ID}" ]]; then
        log_error "Worker ID is required"
        usage
    fi

    # Validate worker ID format (alphanumeric and hyphens only)
    if ! [[ "${WORKER_ID}" =~ ^[a-zA-Z0-9-]+$ ]]; then
        log_error "Invalid worker ID format. Use only letters, numbers, and hyphens."
        exit 1
    fi
}

check_dependencies() {
    log_info "Checking dependencies..."

    if [[ ! -f "${WORKER_SCRIPT}" ]]; then
        log_error "Worker script not found: ${WORKER_SCRIPT}"
        exit 1
    fi

    # Check for Python
    if ! command -v python3 &> /dev/null; then
        log_error "Python 3 is required but not installed"
        exit 1
    fi

    # Check for uv
    if ! command -v uv &> /dev/null; then
        log_error "uv is required but not installed"
        log_error "Install it from: https://docs.astral.sh/uv/getting-started/installation/"
        exit 1
    fi

    log_info "All dependencies found"
}

setup_logs_directory() {
    log_info "Setting up logs directory..."

    mkdir -p "${LOGS_DIR}"
    chmod 755 "${LOGS_DIR}"

    log_info "Logs directory created: ${LOGS_DIR}"
}

install_macos() {
    log_info "Installing worker for macOS (launchd)..."

    local PLIST_TEMPLATE="${CAPE_ROOT}/daemons/com.cape.worker.plist"
    local PLIST_NAME="com.cape.worker.${WORKER_ID}.plist"
    local PLIST_DEST="${HOME}/Library/LaunchAgents/${PLIST_NAME}"
    local PYTHON_PATH="$(which python3)"

    # Check if plist template exists
    if [[ ! -f "${PLIST_TEMPLATE}" ]]; then
        log_error "Plist template not found: ${PLIST_TEMPLATE}"
        exit 1
    fi

    # Create LaunchAgents directory if it doesn't exist
    mkdir -p "${HOME}/Library/LaunchAgents"

    # Generate plist file from template
    log_info "Generating plist file: ${PLIST_DEST}"

    sed -e "s|WORKER_ID|${WORKER_ID}|g" \
        -e "s|PYTHON_PATH|${PYTHON_PATH}|g" \
        -e "s|WORKER_SCRIPT_PATH|${WORKER_SCRIPT}|g" \
        -e "s|CAPE_ROOT_PATH|${CAPE_ROOT}|g" \
        "${PLIST_TEMPLATE}" > "${PLIST_DEST}"

    # Set proper permissions
    chmod 644 "${PLIST_DEST}"

    # Unload if already loaded (ignore errors)
    launchctl unload "${PLIST_DEST}" 2>/dev/null || true

    # Load the service
    log_info "Loading worker service..."
    launchctl load "${PLIST_DEST}"

    # Start the service
    log_info "Starting worker service..."
    launchctl start "com.cape.worker.${WORKER_ID}"

    log_info "Worker installed and started successfully!"
    log_info ""
    log_info "Management commands:"
    log_info "  Start:   launchctl start com.cape.worker.${WORKER_ID}"
    log_info "  Stop:    launchctl stop com.cape.worker.${WORKER_ID}"
    log_info "  Restart: launchctl stop com.cape.worker.${WORKER_ID} && launchctl start com.cape.worker.${WORKER_ID}"
    log_info "  Status:  launchctl list | grep com.cape.worker.${WORKER_ID}"
    log_info "  Unload:  launchctl unload ${PLIST_DEST}"
    log_info ""
    log_info "Logs:"
    log_info "  Application: ${LOGS_DIR}/worker_${WORKER_ID}.log"
    log_info "  Stdout:      ${LOGS_DIR}/worker_${WORKER_ID}_stdout.log"
    log_info "  Stderr:      ${LOGS_DIR}/worker_${WORKER_ID}_stderr.log"
}

install_linux() {
    log_info "Installing worker for Linux (systemd)..."

    local SERVICE_TEMPLATE="${CAPE_ROOT}/daemons/cape-worker.service"
    local SERVICE_NAME="cape-worker-${WORKER_ID}.service"
    local SERVICE_DEST="/etc/systemd/system/${SERVICE_NAME}"
    local PYTHON_PATH="$(which python3)"
    local USER_NAME="$(whoami)"
    local USER_GROUP="$(id -gn)"

    # Check if service template exists
    if [[ ! -f "${SERVICE_TEMPLATE}" ]]; then
        log_error "Service template not found: ${SERVICE_TEMPLATE}"
        exit 1
    fi

    # Check if running with sudo
    if [[ $EUID -ne 0 ]]; then
        log_error "This script must be run with sudo on Linux"
        log_error "Try: sudo $0 ${WORKER_ID}"
        exit 1
    fi

    # Generate service file from template
    log_info "Generating service file: ${SERVICE_DEST}"

    sed -e "s|WORKER_ID|${WORKER_ID}|g" \
        -e "s|PYTHON_PATH|${PYTHON_PATH}|g" \
        -e "s|WORKER_SCRIPT_PATH|${WORKER_SCRIPT}|g" \
        -e "s|CAPE_ROOT_PATH|${CAPE_ROOT}|g" \
        -e "s|USER_NAME|${USER_NAME}|g" \
        -e "s|USER_GROUP|${USER_GROUP}|g" \
        "${SERVICE_TEMPLATE}" > "${SERVICE_DEST}"

    # Set proper permissions
    chmod 644 "${SERVICE_DEST}"

    # Reload systemd
    log_info "Reloading systemd daemon..."
    systemctl daemon-reload

    # Enable the service
    log_info "Enabling worker service..."
    systemctl enable "${SERVICE_NAME}"

    # Start the service
    log_info "Starting worker service..."
    systemctl start "${SERVICE_NAME}"

    log_info "Worker installed and started successfully!"
    log_info ""
    log_info "Management commands:"
    log_info "  Start:   sudo systemctl start ${SERVICE_NAME}"
    log_info "  Stop:    sudo systemctl stop ${SERVICE_NAME}"
    log_info "  Restart: sudo systemctl restart ${SERVICE_NAME}"
    log_info "  Status:  sudo systemctl status ${SERVICE_NAME}"
    log_info "  Logs:    sudo journalctl -u ${SERVICE_NAME} -f"
    log_info "  Disable: sudo systemctl disable ${SERVICE_NAME}"
    log_info ""
    log_info "Logs:"
    log_info "  Application: ${LOGS_DIR}/worker_${WORKER_ID}.log"
    log_info "  Stdout:      ${LOGS_DIR}/worker_${WORKER_ID}_stdout.log"
    log_info "  Stderr:      ${LOGS_DIR}/worker_${WORKER_ID}_stderr.log"
}

# Main execution
main() {
    log_info "CAPE Worker Installation Script"
    log_info "================================"
    log_info ""

    check_worker_id
    check_dependencies
    setup_logs_directory

    # Detect platform and install
    if [[ "$OSTYPE" == "darwin"* ]]; then
        install_macos
    elif [[ "$OSTYPE" == "linux-gnu"* ]]; then
        install_linux
    else
        log_error "Unsupported operating system: $OSTYPE"
        log_error "This script only supports macOS and Linux"
        exit 1
    fi
}

main "$@"
