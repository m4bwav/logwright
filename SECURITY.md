# Security

Report a vulnerability through GitHub's private vulnerability reporting on this repository (Security tab, "Report a vulnerability"). Please do not open a public issue.

logwright has no network code. `lgw.py` reads local files and writes only the markdown file you name with `--md`. The snippets write to local files or the engine's own log and send nothing.
