#compdef oju oju-backup oju-calendar oju-contacts oju-cookbook oju-docs oju-gallery oju-mail oju-mcp oju-memory oju-notes oju-personal oju-preset oju-research oju-sessions oju-signature oju-skills oju-tasks oju-theme oju-webhook
# Zsh tab-completion for the oju umbrella + sub-CLIs.
#
# Drop in any directory on $fpath, e.g.:
#     fpath=(/path/to/oju-ui/scripts/_completion $fpath)
#     autoload -U compinit; compinit
#
# Then `oju <tab>` completes subcommands; `oju mail <tab>`
# completes mail subcommands; `oju-mail <tab>` works the same.

_oju_scripts_dir() {
    local self="${(%):-%x}"
    while [[ -L "$self" ]]; do self="$(readlink "$self")"; done
    cd "${self:h}/.." && pwd
}

typeset -gA _oju_subs

_oju_refresh() {
    _oju_subs=()
    local dir="$(_oju_scripts_dir)"
    local py="$dir/../venv/bin/python"
    [[ -x "$py" ]] || py="$(command -v python3)"
    local f sub help_out commands
    for f in "$dir"/oju-*; do
        [[ -x "$f" ]] || continue
        case "$f" in
            *.bak|*.pyc|*.pre-*) continue ;;
        esac
        sub="${${f:t}#oju-}"
        help_out=$("$py" "$f" --help 2>/dev/null) || continue
        commands=$(echo "$help_out" | grep -oE '\{[a-z0-9_,-]+\}' | head -1 \
            | tr -d '{}' | tr ',' ' ')
        _oju_subs[$sub]="$commands"
    done
}

_oju() {
    [[ ${#_oju_subs} -eq 0 ]] && _oju_refresh

    local cmd="${words[1]}"

    if [[ "$cmd" == "oju" ]]; then
        if (( CURRENT == 2 )); then
            local -a subs=(${(k)_oju_subs} help)
            _describe 'subcommand' subs
            return
        fi
        local sub="${words[2]}"
        if [[ "$sub" == "help" ]] && (( CURRENT == 3 )); then
            local -a subs=(${(k)_oju_subs})
            _describe 'subcommand' subs
            return
        fi
        if (( CURRENT == 3 )); then
            local -a sc=(${(s/ /)_oju_subs[$sub]})
            _describe 'command' sc
            return
        fi
        return
    fi

    # oju-foo <tab>
    local sub="${cmd#oju-}"
    if (( CURRENT == 2 )); then
        local -a sc=(${(s/ /)_oju_subs[$sub]})
        _describe 'command' sc
        return
    fi
}

_oju "$@"
