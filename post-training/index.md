# Post-training methods

Post-training improves a pretrained policy using task-specific interaction.
The current reference method is DSRL; other methods remain in the roadmap.

## DSRL in one sentence

<div class="method-card">
<span class="maturity maturity-validated">Validated here</span>

Keep π0-DROID frozen and train a small SAC actor to choose the flow-matching
noise that produces better action chunks.
</div>

The SAC action is not a robot command. It is an `(8, 32)` noise block expanded
to the base policy's ten denoising steps. π0 converts that noise and the current
observation into robot actions; eight actions are executed before the next
query.

## Why this design

- The pretrained policy retains broad visual and language behavior.
- Online learning updates a much smaller policy than full VLA fine-tuning.
- A transformer actor and critics can consume frozen visual and policy-prefix
  features.
- Learned rewards can relabel complete trajectories without entering the
  real-time control loop.
- Zero-shot and deterministic post-trained policies can be compared under the
  same rollout geometry.

## Reference algorithm geometry

- Base policy: `pi0_droid`, action horizon 10.
- SAC noise action: 8 rows × 32 dimensions.
- Noise expansion: cyclic fill from 8 to 10 flow steps.
- Robot execution: first 8 base-policy actions per query.
- Critics: four; two sampled for each target.
- Update ratio: four critic updates per actor update.
- Encoder: six-layer transformer.
- Warmup: 1,200 robot control steps with the configured exploration prior.
- Success: human terminal label by default.
- Reward: sparse terminal signal plus versioned trajectory progress.

These values define an experiment. Change them only under a new run identity.

## Two real-robot topologies

### Validated Topology C
<span class="maturity maturity-validated">Validated here</span>

The laptop runs the robot loop and one HTTP trainer endpoint coordinates the
policy, reward model, SAC, replay, and checkpointing on the GPU host. This is
the recommended reference deployment in this guide.

### Upstream serial remote-robot topology
<span class="maturity maturity-upstream">Upstream runnable</span>

`robometer-policy-learning` also provides `train_dsrl.py`, a TCP remote robot
server, and an async reward-relabel wrapper. It is a credible upstream route,
but it is not configuration-identical to Topology C.

## DSRL is not EXPO-FT

DSRL steers a frozen policy through noise. EXPO-FT learns residual action edits
and fine-tunes a π0.5-based stack. Their actions, replay schemas, checkpoints,
and training processes are not interchangeable.

## Source map

- Current integration: `dsrl_pi0/`
- Validated topology runbook:
  `dsrl_pi0/docs/robometer_pi0_topology_c.md`
- Upstream framework:
  `online_rl_code_base_defaults/robometer-policy-learning/`
- Upstream DSRL reference:
  `online_rl_code_base_defaults/dsrl_pi0_original/`
- Reward model:
  `online_rl_code_base_defaults/robometer/`
