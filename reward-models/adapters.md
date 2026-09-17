# TopReward and API reward adapters

These adapters extend the same DSRL relabel contract while keeping distinct
reward identities and output directories.

## TopReward

<span class="maturity maturity-validated">Validated here</span>

Repository paths:

- `online_rl_code_base_defaults/topreward.py`
- `online_rl_code_base_defaults/baseline_reward_relabel_server.py`
- `dsrl_pi0/server/baseline_reward_relabel_server.py`

The online-safe default scores each prefix with:

```text
sigmoid(log p(True) - log p(False))
```

This **margin** has a stable cross-episode meaning. Avoid per-episode min/max
normalization during RL because a score at time `t` then depends on the
episode's future extrema.

Generic server shape:

```bash
python server/baseline_reward_relabel_server.py \
  --backend topreward \
  --model-path "<qwen-vl-checkpoint>" \
  --host 127.0.0.1 \
  --port "${TOPREWARD_GRPC_PORT}" \
  --image-key observation/exterior_image_1_left \
  --max-frames 64 \
  --num-prefix-samples 15 \
  --reward-mode margin
```

Optional few-shot demonstrations must contain frames, the exact task string,
and a success label. Freeze the demo manifest and seed. A controlled reference
set uses one success and three failures selected for diverse episode lengths.

## API reasoning reward

<span class="maturity maturity-validated">Validated here</span>

Repository paths:

- `dsrl_pi0/server/api_reasoning_reward.py`
- `dsrl_pi0/examples/api_reasoning_reward_ui.py`
- `dsrl_pi0/examples/api_reasoning_fewshot_annotation_ui.py`
- `dsrl_pi0/examples/compare_api_reasoning_fewshot.py`

Use an environment variable, never a committed key:

```bash
read -rsp "API key: " OPENAI_API_KEY
echo
export OPENAI_API_KEY
```

The adapter supports:

- zero-shot single-episode progress scoring;
- few-shot prompts from human-smoothed, per-frame annotations;
- parallel offline scoring for comparisons;
- a gRPC boundary compatible with DSRL relabeling.

Store a reward variant that hashes or otherwise identifies the model, prompt
version, sampling mode, demonstrations, and scorer configuration. Zero-shot
and few-shot results must never share a replay buffer or checkpoint directory.

## Few-shot annotation rules

1. Select demonstrations from baseline rollouts, not the DSRL evaluation set.
2. Include one successful and three diverse-length failure trajectories.
3. Subsample frames for manageable annotation, but preserve source timestamps.
4. Let annotators move key points freely; successful episodes may regress or
   contain suboptimal intermediate behavior.
5. Interpolate with a shape-preserving method and save both key points and the
   expanded curve.
6. Record source hashes so stale or replaced videos cannot silently reuse an
   annotation.

## API-specific operational risks

- Quota exhaustion and rate limits can halt relabeling.
- Concurrent calls reduce wall time but can increase throttling.
- Remote APIs may retain data; check policy before uploading robot video.
- Provider/model revisions can change output without local code changes.
- Network latency is too variable for a per-control-step synchronous reward.
  Relabel complete episodes off the control path.

## Adapter parity

All reward choices should expose the same logical result:

```json
{
  "progress": [0.0, 0.14, 0.31, 0.55, 0.82],
  "success": false,
  "metadata": {
    "backend": "versioned-backend-name",
    "variant": "immutable-variant-id",
    "frame_count": 5
  }
}
```

The trainer validates lengths, finiteness, range, task identity, and backend
identity before mutating replay.
