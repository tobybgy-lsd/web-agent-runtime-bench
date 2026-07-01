# Visual Agent Failure Types

v3.4 recognizes these safe visual runtime diagnosis subtypes:

- `visual_runtime_observation_lag`
- `stale_screenshot_action`
- `image_token_budget_exceeded`
- `screenshot_transport_overhead`
- `overcompressed_screenshot_loss`
- `underloaded_screenshot`
- `vlm_action_grounding_failure`
- `visual_element_misidentification`
- `coordinate_click_drift`
- `viewport_scroll_state_mismatch`
- `dpr_scaling_mismatch`
- `ocr_semantic_mismatch`
- `transient_ui_missed_between_frames`
- `visual_context_rot`
- `visual_dom_conflict`
- `pure_visual_insufficient_evidence`
- `visual_runtime_safety_blocked`

Each report includes evidence, confidence, safe next action, a local fix plan,
and a verification strategy.
