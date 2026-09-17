# Training, checkpoints, and evaluation

## Freeze the experiment identity

Before collecting the first episode, save:

```yaml
task: "exact language instruction"
base_policy:
  family: pi0_droid
  checkpoint: "<immutable-checkpoint>"
camera:
  policy_exterior: left
  wrist_required: true
control:
  hz: 15
  max_timesteps: 400
  open_loop_horizon: 8
dsrl:
  noise_shape: [8, 32]
  flow_horizon: 10
  warmup_steps: 1200
reward:
  backend: robometer
  variant: "<immutable-reward-identity>"
  success_source: human
```

Changing any of these fields requires a distinct run directory, replay buffer,
checkpoint namespace, and tracker project or group.

## Matched zero-shot baseline

Run the frozen base policy before training:

```bash
python scripts/run_eval.py \
  --task "${TASK}" \
  --num-episodes "${EVAL_EPISODES}" \
  --max-timesteps "${MAX_TIMESTEPS}" \
  --open-loop-horizon "${OPEN_LOOP_HORIZON}" \
  --remote-host 127.0.0.1 \
  --remote-port "${POLICY_PORT}" \
  --external-camera "${EXTERNAL_CAMERA}" \
  --left-camera-id "${LEFT_CAMERA_ID}" \
  --right-camera-id "${RIGHT_CAMERA_ID}" \
  --wrist-camera-id "${WRIST_CAMERA_ID}"
```

The prompt must match training character-for-character. Use the same camera,
scene distribution, episode limit, chunk execution, robot controller, and
success rubric.

Warmup trajectories are not automatically a zero-shot baseline. Their noise
distribution may differ from the base policy prior.

## Training lifecycle

1. Start the robot service and test bounded motion.
2. Start and validate the patched base-policy server.
3. Start and probe the reward server.
4. Run trainer parity and synthetic self-checks.
5. Start the trainer and inspect its complete startup identity.
6. Open the trainer tunnel from the laptop.
7. Start rollout; confirm trainer/laptop agreement before motion.
8. Label every episode and inspect reward progress.
9. Force a checkpoint before planned shutdown.
10. Evaluate a deterministic actor at declared environment-step counts.

## Checkpoints

A complete checkpoint should contain:

- actor, target actor if used, critics, target critics, and temperature;
- optimizer states and update counters;
- replay buffer including reward/relabel metadata;
- total robot control steps and query-transition count;
- task and camera identity;
- base-policy checkpoint and action geometry;
- reward backend and immutable variant;
- feature dimensions and normalizer state;
- software revisions.

Save atomically to a temporary directory and rename only after validation.
Restore must fail on identity mismatch.

Before terminating a live trainer, use its explicit checkpoint endpoint or
command and wait for confirmation. Extending a still-running trainer is safer
than restarting because in-memory replay and optimizer state remain intact.

## Deterministic evaluation

Training success rate mixes warmup and stochastic actor samples. The final
result should use the actor's deterministic mean noise:

```bash
bash examples/scripts/run_rollout_laptop_robometer_reward.sh \
  --eval "${EVAL_EPISODES}"
```

Evaluation mode must:

- disable replay writes and gradient steps;
- avoid advancing training environment-step counters;
- use a separate output directory;
- restore training mode after normal exit or interruption;
- log the checkpoint/environment-step identity.

Compare deterministic DSRL and zero-shot results with the same number of
episodes and the same success rubric. Report confidence intervals for small
sample counts rather than only a point estimate.

## Required artifacts

For each episode:

- individual camera videos and a view-ordered mosaic;
- frame-aligned robot state and executed actions;
- raw policy action or SAC noise;
- policy-query and chunk indices;
- timestamps;
- human success;
- raw and composed reward curves;
- reward-model metadata;
- prompt and run identity.

For the run:

- append-only `progress.csv`;
- resolved configuration;
- environment and package lockfiles;
- checkpoints and replay snapshots;
- W&B or equivalent logs;
- zero-shot and deterministic evaluation summaries.

## Monitoring

Watch both learning and data quality:

- episode return and human success;
- reward-model final progress and agreement with human labels;
- reward relabel latency and failures;
- replay size and relabeled ratio;
- critic, actor, and temperature losses;
- Q-value scale and divergence;
- control-loop frequency and policy-query latency;
- action saturation, collision aborts, and discarded episodes.

Stop the run if reward/human agreement collapses, Q-values diverge, control
frequency becomes unsafe, camera identity changes, or restored behavior does
not match pre-shutdown behavior.

## Troubleshooting order

1. Robot and gripper path.
2. Camera serial/view identity.
3. Base-policy input and action convention.
4. Trainer health identity.
5. Reward server shape, range, and frame key.
6. Replay contents and relabel status.
7. Actor/critic restore binding.
8. Optimization metrics.

This order prevents an upstream hardware fault from being misdiagnosed as an
RL algorithm failure.
