#!/bin/zsh

# create-symlinks.sh
# Creates symlinks from the cape repository to a target directory.
#
# This script creates symbolic links from the cape repository to a target directory:
# - Agent files (.md): agents/claude-code -> .claude/agents, agents/opencode -> .opencode/agent  
# - Hook files: hooks/claude-code -> .claude/hooks
# - Command files: commands/claude-code -> .claude/commands
# - Documentation: ai_docs -> ai_docs
#
# Creates parent directories automatically and replaces existing symlinks.
# Preserves existing regular directories and files.

set -uo pipefail

# Colors and constants
readonly RED=$'\e[31m' GREEN=$'\e[32m' YELLOW=$'\e[33m' CYAN=$'\e[36m' NC=$'\e[0m'
readonly ENV_SAMPLE_FILE=".env.hooks.example"
readonly REQUIRED_DIRS=("agents" "hooks" "commands" "scripts")

# Global counters (zsh integers)
typeset -gi success_ops=0 total_ops=0

# Configurable symlink mappings: source_dir:target_dir:pattern:label:maxdepth
readonly -a SYMLINK_CONFIG=(
    "agents/claude-code:.claude/agents:*.md:Agents:1"
    "agents/opencode:.opencode/agent:*.md:Agents:1"
    "hooks/claude-code:.claude/hooks:*:Hooks:99"
    "commands/claude-code:.claude/commands:*:Commands:99"
    "ai_docs:ai_docs:*.md:AI docs:1"
)

usage() {
    cat << 'EOF'
Usage: create-symlinks.sh TARGET_DIR [OPTIONS]

Creates symlinks from the cape repository to a target directory.

Arguments:
    TARGET_DIR    Target directory path (supports ~ expansion)

Options:
    -f, --force   Skip confirmation prompts
    -h, --help    Show this help

Examples:
    ./scripts/create-symlinks.sh ~/my-project
    ./scripts/create-symlinks.sh /path/to/target --force
EOF
}

die() {
    echo -e "${RED}Error: $*${NC}" >&2
    exit 1
}

warn() {
    echo -e "${YELLOW}Warning: $*${NC}" >&2
}

info() {
    echo -e "${GREEN}$*${NC}"
}


# Creates a symbolic link from repo_root/source to target_dir/target
# Args: repo_root target_dir source target description
# Returns: 0 on success, 1 on failure
create_symlink() {
    local repo_root=$1 target_dir=$2 source=$3 target=$4 description=$5
    local source_path="$repo_root/$source"
    local target_path="$target_dir/$target"
    
    # Verify source exists
    [[ -e $source_path ]] || { warn "Source missing: $source_path"; return 1; }
    
    # Create parent directory
    mkdir -p "$(dirname "$target_path")"
    
    # Handle existing target (only warn for regular files/directories, not symlinks)
    if [[ -e $target_path && ! -L $target_path ]]; then
        if [[ -d $target_path ]]; then
            warn "Target directory exists, skipping: $target_path"
        else
            warn "Target file exists, skipping: $target_path"
        fi
        return 1
    fi
    
    # Create symlink (ln -sf handles replacing existing symlinks automatically)
    if ln -sf "$source_path" "$target_path"; then
        info "✓ $description"
        return 0
    else
        echo -e "${RED}✗ $description failed${NC}" >&2
        return 1
    fi
}

# Process files matching pattern in source directory and create symlinks
# Automatically updates global counters: total_ops (files found) and success_ops (links created)
# Args: repo_root target_dir source_dir target_base pattern label [maxdepth]
# Example: process_files "/repo" "/target" "agents/claude-code" ".claude/agents" "*.md" "Agents" 1
process_files() {
    local repo_root=$1 target_dir=$2 source_dir=$3 target_base=$4 pattern=${5:-"*"} label=$6 maxdepth=${7:-1}
    local source_path="$repo_root/$source_dir"
    
    [[ -d $source_path ]] || { warn "$label directory not found: $source_path"; return 0; }
    
    echo "Processing $label..." >&2
    
    # Use ZSH globbing for better performance and native handling
    local -a files
    if (( maxdepth == 1 )); then
        files=("$source_path"/${~pattern}(N.))
    else
        files=("$source_path"/**/${~pattern}(N.))
    fi
    
    for file in "${files[@]}"; do
        # Calculate relative path from source_path to maintain directory structure
        local relative_path=${file#$source_path/}
        ((total_ops++))
        if create_symlink "$repo_root" "$target_dir" "$source_dir/$relative_path" "$target_base/$relative_path" "$label: $relative_path"; then
            ((success_ops++))
        fi
    done
}

# Copy environment variables example file with user confirmation
# Args: repo_root target_dir force
handle_env_sample() {
    local repo_root=$1 target_dir=$2 force=$3
    local sample_file="$repo_root/$ENV_SAMPLE_FILE"
    local target_file="$target_dir/$ENV_SAMPLE_FILE"
    
    [[ -f $sample_file ]] || { warn "Environment sample not found: $sample_file"; return 1; }
    
    if [[ $force ]]; then
        info "Copying environment variables example..."
        copy_sample=true
    else
        read -rp "Copy environment variables example? (Y/n): " choice
        case ${(L)choice} in  # Convert to lowercase
            ''|y|yes) copy_sample=true ;;
            *) copy_sample=false ;;
        esac
    fi
    
    if [[ $copy_sample ]]; then
        if cp "$sample_file" "$target_file"; then
            info "✓ Copied: $ENV_SAMPLE_FILE"
            echo -e "${CYAN}  Edit this file and set your API keys.${NC}"
        else
            echo -e "${RED}✗ Failed to copy environment example${NC}" >&2
        fi
    else
        warn "Skipped environment example"
        echo -e "${CYAN}You can copy .env.hooks.example manually later.${NC}"
    fi
}

main() {
    local force=false target_dir copy_sample
    
    # Parse arguments
    while (( $# > 0 )); do
        case $1 in
            -f|--force) force=true ;;
            -h|--help) usage; exit 0 ;;
            -*) die "Unknown option: $1" ;;
            *) 
                [[ -z ${target_dir:-} ]] || die "Too many arguments"
                # ZSH handles tilde expansion automatically with :A modifier
                target_dir=${1:A}
                ;;
        esac
        shift
    done
    
    [[ -n ${target_dir:-} ]] || die "Target directory required"
    
    # Setup paths (ZSH-optimized)
    local script_path=${(%):-%x}
    local script_dir=${script_path:h:A}  # :h gets dirname, :A gets absolute path
    local repo_root=${script_dir:h}     # Parent directory
    
    # Verify this is the cape repository by checking for required directories
    local missing_dirs=()
    for dir in "${REQUIRED_DIRS[@]}"; do
        [[ -d "$repo_root/$dir" ]] || missing_dirs+=($dir)
    done
    (( ${#missing_dirs} == 0 )) || die "Must run from cape repository root (missing directories: ${(j:, :)missing_dirs})"
    [[ $target_dir == /* ]] || die "Target must be absolute path: $target_dir"
    
    # Validate target directory access
    if [[ ! -d $(dirname "$target_dir") ]]; then
        die "Parent directory of target does not exist: $(dirname "$target_dir")"
    fi
    if [[ ! -w $(dirname "$target_dir") ]]; then
        die "No write permission to create target directory: $(dirname "$target_dir")"
    fi
    
    echo "Repository: $repo_root"
    echo "Target: $target_dir"
    echo "=============================="
    
    local hooks_created=false
    local initial_success=$success_ops
    
    # Process all configured symlink mappings
    for config in "${SYMLINK_CONFIG[@]}"; do
        # Parse configuration: source_dir:target_dir:pattern:label:maxdepth
        local -a parts=(${(s.:.)config})
        local source_dir=$parts[1]
        local target_base=$parts[2]
        local pattern=$parts[3]
        local label=$parts[4]
        local maxdepth=$parts[5]
        
        local success_before=$success_ops
        process_files "$repo_root" "$target_dir" "$source_dir" "$target_base" "$pattern" "$label" "$maxdepth"
        
        # Check if hooks were created (for environment file handling)
        [[ $source_dir == "hooks/claude-code" && $success_ops > $success_before ]] && hooks_created=true
    done
    
    # Summary
    echo "=============================="
    echo "Symlink creation complete!"
    if (( success_ops == total_ops )); then
        info "Success: $success_ops/$total_ops operations"
    else
        echo -e "${YELLOW}Partial success: $success_ops/$total_ops operations${NC}"
    fi
    
    # Handle environment sample if hooks were created
    if [[ $hooks_created ]]; then
        echo
        echo -e "${CYAN}📋 Note: Claude Code hooks require API keys in environment variables.${NC}"
        handle_env_sample "$repo_root" "$target_dir" "$force"
    fi
    
    (( total_ops > 0 )) || info "No operations needed."
}

main "$@"