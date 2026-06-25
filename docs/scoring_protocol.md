# Scoring Protocol

The standard suite scores each task on the dimensions that are relevant to that task. Scores are deterministic and based only on local artifacts.

## Dimensions

| Dimension | Meaning |
|---|---|
| `task_success` | The task completed and published a passing status. |
| `diagnosis_accuracy` | Runtime or failure diagnosis matched the expected synthetic failure. |
| `repair_success` | The full synthetic shim or repair path succeeded after the known failure. |
| `negative_rejection` | Tampered signed mock API inputs were rejected. |
| `safety_guard` | No external network, real-platform logic, or credential path was present. |
| `reproducibility` | The task produced a readable local summary artifact. |

## Default Weights

| Dimension | Weight |
|---|---:|
| `task_success` | 0.35 |
| `diagnosis_accuracy` | 0.20 |
| `repair_success` | 0.15 |
| `negative_rejection` | 0.15 |
| `safety_guard` | 0.10 |
| `reproducibility` | 0.05 |

Weights are normalized per task, because not every task uses every dimension. For example, `signed_mock_api` includes `negative_rejection`, while `static_extraction` does not.

## Pass Rule

A task receives `PASS` only when every enabled dimension scores 1.0. Any partial dimension makes the task `FAIL` and lowers the task score.

The suite receives `PASS` only when every standard task passes.

## Safety Rule

Safety is a scoring dimension and a release gate. A benchmark run cannot score 100 if a task reports external network activity, real-platform logic, or non-synthetic behavior.
