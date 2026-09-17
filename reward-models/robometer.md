# Robometer hosting and relabeling

<span class="maturity maturity-validated">Validated here</span>

Source:
[robometer/robometer](https://github.com/robometer/robometer) and
[robometer-policy-learning](https://github.com/robometer/robometer-policy-learning).
The vendored reference trees in this repository are
`online_rl_code_base_defaults/robometer/` and
`online_rl_code_base_defaults/robometer-policy-learning/`.

## Install in an isolated environment

Robometer and the policy/trainer stack have large, sometimes conflicting ML
dependencies. Do not install them into the robot laptop's DROID environment.

```bash
git clone https://github.com/robometer/robometer.git
cd robometer
uv sync
uv pip install -e ".[robometer]"
```

Published checkpoint:
[`robometer/Robometer-4B`](https://huggingface.co/robometer/Robometer-4B).
Record the exact revision in experiment metadata rather than relying on a
moving model identifier.

## HTTP evaluation server

Use the HTTP server for offline scoring, visualization, and integration tests:

```bash
uv run python robometer/evals/eval_server.py \
  model_path=robometer/Robometer-4B \
  server_url=127.0.0.1 \
  server_port="${ROBOMETER_HTTP_PORT}" \
  batch_size=16 \
  num_gpus=1
```

Important endpoints:

- `GET /health`: process readiness;
- `GET /model_info`: loaded model and configuration;
- `GET /gpu_status`: worker-pool status;
- `POST /evaluate_batch`: JSON batch inference;
- `POST /evaluate_batch_npy`: multipart NumPy payloads.

Minimal client:

```bash
uv run python scripts/example_inference.py \
  --eval-server-url "http://127.0.0.1:${ROBOMETER_HTTP_PORT}" \
  --video /path/to/episode.mp4 \
  --task "put the object in the container" \
  --fps 3
```

The HTTP server is not the same protocol as the DSRL relabel server.

## gRPC reward relabel server

The current DSRL integration uses the reward server from
`robometer-policy-learning`:

```bash
uv run python scripts/start_reward_relabel_server.py \
  reward_model=robometer \
  reward_model.model_path="robometer/Robometer-4B" \
  server.host=127.0.0.1 \
  server.port="${REWARD_GRPC_PORT}" \
  device=cuda \
  server.image_keys='["observation/exterior_image_1_left"]'
```

Run it on the GPU host beside the trainer. Keep the gRPC port private; only the
trainer needs it. Probe with the repository's
`scripts/test_reward_relabel_server.py` before connecting the robot.

```bash
uv run python scripts/test_reward_relabel_server.py \
  --server-address "127.0.0.1:${REWARD_GRPC_PORT}" \
  --num-steps 5
```

## Online relabel sequence

1. The rollout client executes an episode and stores policy-query frames.
2. The human supplies success/failure.
3. The trainer sends the task and ordered exterior frames to the reward server.
4. The server returns a finite progress value for every requested prefix.
5. The trainer verifies output count and range.
6. Progress is combined with the sparse reward and written into replay.
7. Only relabeled transitions become eligible for SAC sampling.

The reference configuration uses human terminal success. Robometer's success
head should remain diagnostic until its task-specific false-positive rate has
been measured.

## Configuration that must be recorded

```yaml
reward:
  family: robometer
  model_id: robometer/Robometer-4B
  model_revision: "<immutable-revision>"
  image_key: observation/exterior_image_1_left
  frame_sampler: policy_query_frames
  output: progress
  composition: sparse_plus_progress
  success_source: human
```

A change to any value above defines a different reward function and requires a
new replay buffer and checkpoint namespace.

## Failure policy

For physical training, select one policy explicitly:

- **fail closed:** discard the episode if relabeling fails;
- **sparse fallback:** retain only the human sparse reward and tag transitions;
- **retry:** block scene reset until bounded retries complete.

Silent zero-filled reward arrays are not acceptable. They look valid to SAC
while changing the experiment.

## Known constraints

- The upstream package is early-stage research software and has little unit
  test coverage around the reward server.
- Full training requires substantial GPU memory and processed datasets.
- VLAC and Robo-Dopamine need separate environments from primary Robometer.
- gRPC/protobuf versions are sensitive; pin the working environment.
- Prefix inference can dominate time between episodes. Measure it before
  choosing batch size and frame count.
