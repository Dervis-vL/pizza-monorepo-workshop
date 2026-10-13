# Standard toolkit variables for just recipes
# PEP 723 scripts run in their own environment: `just` keeps working even when the workspace does not resolve.
_uv := require('uv')
_just := quote(just_executable())
_scripts    := quote(_uv) + ' run --script ' + quote(justfile_directory() / '.just/scripts')
_workspaces := _scripts / 'workspaces.py' + ' ' + quote(justfile_directory())
_members     := shell(_workspaces + ' members')
_modules     := shell(_workspaces + ' modules')
_deployables := shell(_workspaces + ' deployables')
uv := quote(_uv)
run := uv + ' run'
green := style('bold') + style('green')
yellow := style('yellow')
blue := style('blue')
red := style('red')
nc   := NORMAL
# Container engine: podman or docker
container := env_var_or_default("CONTAINER_ENGINE", "docker")
# Image registry, e.g. ghcr.io/you. Empty means local only: images are named <name>:<tag>.
_registry := env_var_or_default("REGISTRY", "")
_image_prefix := if _registry == "" { "" } else { _registry + "/" }
# uv audit is in preview
_uv_audit := "uv audit --locked --preview-features audit"
# Where per-member coverage data lands before it is combined
_cov_data := justfile_directory() / ".coverage-data"
# Define the name of the release scope env variable
_release_scope := "RELEASE"
