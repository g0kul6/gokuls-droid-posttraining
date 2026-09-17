# Reward models

A reward model turns an episode or trajectory prefix into a learning signal.
It does not replace the robot policy, safety system, or evaluation protocol.

## Current recommendation

<div class="method-card">
<span class="maturity maturity-validated">Validated here</span>

**Robometer-4B progress relabeling** is the reference learned reward for the
current DSRL stack. Human labels remain the source of terminal success.
</div>

Robometer scores visual progress over prefixes of the selected exterior-camera
trajectory. At episode end, the trainer receives a progress sequence in
`[0, 1]`, aligns it with policy-query transitions, and combines it with the
sparse environment reward.

```{mermaid}
sequenceDiagram
    participant R as Rollout
    participant T as Trainer
    participant M as RewardServer
    R->>T: episode frames and human label
    T->>M: task plus trajectory prefixes
    M-->>T: per-prefix progress and optional success
    T->>T: validate, align, relabel replay
    T-->>R: episode accepted and next reset allowed
```

## Reward contract

Every reward backend should declare:

- **input:** task string, ordered RGB frames, view identity, and timestamps;
- **output:** one finite scalar per requested transition, with a documented
  range and temporal meaning;
- **causality:** whether step `t` uses only frames up to `t`;
- **success:** whether success is predicted, and whether it is advisory or
  authoritative;
- **failure behavior:** fail closed, use sparse reward, or discard the episode;
- **identity:** model checkpoint, prompt/version, frame sampler, and calibration;
- **latency:** expected and maximum relabel time;
- **evidence:** held-out alignment and human-agreement results.

## Supported families

### Robometer
<span class="maturity maturity-validated">Validated here</span>

The primary path. It provides progress, preference, and optional success heads,
an HTTP evaluation server, and a gRPC relabel integration in
`robometer-policy-learning`.

### TopReward
<span class="maturity maturity-validated">Validated here</span>

A Qwen-VL token-probability baseline adapted to emit causal prefix rewards.
Margin scoring is preferred over per-episode min/max normalization because the
latter changes the meaning of a value based on future frames.

### API reasoning reward
<span class="maturity maturity-validated">Validated here</span>

A task-conditioned remote reasoning model can score zero-shot or human-annotated
few-shot trajectories. It is useful for research comparisons but has API cost,
quota, latency, privacy, and reproducibility constraints.

### Published baselines
<span class="maturity maturity-upstream">Upstream runnable</span>

GVL, RL-VLM-F, VLAC, RoboReward, Robo-Dopamine, ReWiND, and TopReward are
available in the Robometer evaluation framework. Their dependency and output
contracts differ; they are not drop-in online rewards without an adapter.

## Evaluation before training

At minimum, evaluate one held-out success and three failures with diverse
lengths. Inspect:

1. temporal progress curves rather than only final values;
2. final success/failure separation;
3. monotonicity where the task warrants it;
4. response to regressions, retries, and suboptimal successful behavior;
5. stability under frame subsampling;
6. agreement with human labels;
7. latency at the trajectory lengths used online.

Do not tune a prompt or threshold on the same trajectories used to report the
final comparison.
