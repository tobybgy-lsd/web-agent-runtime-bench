# Plugin Permission Model

Default allowed permissions:

- `read_input_dir`
- `write_output_dir`
- `emit_evidence`

Blocked by default:

- `read_raw_evidence`
- `run_local_command`
- `network_access`
- `write_project_files`
- browser profile access
- credential store access
- disabling safety gates

High-risk permissions require future explicit governance and cannot bypass the
public safety boundary.
