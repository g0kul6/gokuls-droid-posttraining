# Reward baselines and comparisons

<span class="maturity maturity-upstream">Upstream runnable</span>

The baseline implementations live in
`online_rl_code_base_defaults/robometer/robometer/evals/baselines/`.
They share an evaluation harness, not a uniform online-training contract.

## Baseline catalog

**Robometer / ReWiND**
: Progress and preference models with local checkpoints. These are the only
  families in this set that support the quality-preference evaluation path.

**GVL**
: API-backed visual-language progress scoring. Requires either a Gemini or
  OpenAI credential.

**RL-VLM-F**
: API-backed pairwise preference scoring. Its output is not naturally a dense
  per-step reward.

**VLAC**
: Local InternRobotics/VLAC progress model. Its package requirements conflict
  with the primary Robometer environment.

**RoboReward**
: Local discrete progress scoring, commonly on a one-to-five scale. An online
  adapter must document normalization.

**Robo-Dopamine**
: Generative reward model served through vLLM. It requires its own environment
  and has different torch/vLLM constraints.

**TopReward**
: Qwen-VL zero-shot progress derived from answer-token probabilities. Online
  use requires a causal prefix sampler and stable calibration.

## Supported benchmark types

- **Reward alignment:** compare temporal model scores with reference rewards.
- **Policy ranking:** test whether aggregate reward orders policies correctly.
- **Confusion matrix:** evaluate a chosen terminal threshold.
- **Quality preference:** available for RL-VLM-F, Robometer, and ReWiND.

Example Robometer benchmark:

```bash
uv run python robometer/evals/run_baseline_eval.py \
  reward_model=rbm \
  model_path=robometer/Robometer-4B \
  custom_eval.eval_types='[reward_alignment]' \
  custom_eval.use_frame_steps=true \
  custom_eval.subsample_n_frames=5 \
  custom_eval.reward_alignment_max_trajectories=30 \
  max_frames=8 \
  model_config.batch_size=32
```

Use the exact dataset splits and random seed for every model. A comparison that
changes frame count, view, task wording, or success labels between models is
not controlled.

## Environment isolation

Create separate lockfiles or virtual environments for incompatible models.
For example:

```bash
# VLAC environment
uv venv .venv-vlac
uv pip install -e ".[vlac]" --python .venv-vlac/bin/python

# Robo-Dopamine environment
uv venv .venv-robodopamine
uv pip install vllm --python .venv-robodopamine/bin/python
uv pip install -r requirements-robodopamine.txt \
  --python .venv-robodopamine/bin/python
uv pip install -e . --no-deps \
  --python .venv-robodopamine/bin/python
```

Do not resolve one global environment by repeatedly upgrading torch,
transformers, protobuf, or OpenCV. That makes previously reported results
non-reproducible.

## Fair comparison checklist

- Same source videos, task strings, view, and frame timestamps.
- Same success/failure labels and held-out split.
- Same maximum frame budget or a disclosed model-native exception.
- Raw model output retained before calibration.
- Calibration fitted only on a designated calibration split.
- Latency, GPU memory, API cost, and failure rate reported.
- Per-step curves and episode aggregates both saved.
- Human agreement reported independently from return.

## Promotion to an online reward

A baseline is ready for online DSRL only after an adapter provides:

1. deterministic ordering and shape validation;
2. causal scores at policy-query transitions;
3. a bounded, versioned numeric scale;
4. explicit timeout and retry behavior;
5. reward identity embedded in checkpoints and replay;
6. a held-out task audit;
7. a synthetic trainer integration test.

Without these, keep it in offline evaluation.
