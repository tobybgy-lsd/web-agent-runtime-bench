# Counterfactual Diagnosis

Counterfactual diagnosis checks whether the engine changes the primary diagnosis when exactly one causal factor changes. This helps prevent downstream symptoms from masking the root cause.

The P98 validation runner is:

```powershell
python -m tools.validation.run_composite_counterfactual_p98_validation
```

The runner writes `validation/composite_counterfactual_p98_validation.json`.
