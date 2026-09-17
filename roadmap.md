# Method and embodiment roadmap

This page separates promising external code from what this DROID integration
actually supports.

## Status overview

### DSRL + Robometer
<span class="maturity maturity-validated">Validated here</span>

Current operational reference. Continue hardening tests, release packaging,
configuration portability, and multi-task evaluation.

### EXPO-FT
<span class="maturity maturity-planned">Integration planned</span>

Source: [pd-perry/expo-ft](https://github.com/pd-perry/expo-ft). The vendored
snapshot is `online_rl_code_base_defaults/expo-ft/`.

EXPO-FT applies sample-efficient RL fine-tuning to π0.5 with a residual actor
and pixel/state critics. It has a DROID-targeted client/server design and a
complete upstream pick-task example. It is **not runnable in this checkout**
without:

- cloning its modified OpenPI and DROID forks into expected paths;
- creating separate Python 3.11 server and robot-client environments;
- collecting demonstrations and producing LeRobot conversion artifacts;
- computing normalization statistics and an SFT checkpoint;
- replacing author-specific camera IDs, bounds, reset joints, and success
  detector;
- validating its Cartesian action convention on this robot;
- adding a learned-reward adapter if Robometer is desired.

Only the upstream pick workflow has a complete script set. The light task has
configuration and environment code but not equivalent launch scripts.

Promotion criteria:

1. dependency-locked server and client install;
2. zero-action and bounded-action hardware tests;
3. matched π0.5 zero-shot and SFT baselines;
4. one complete task with task-independent artifact layout;
5. checkpoint restore and deterministic evaluation;
6. explicit reward and safety contract.

## From-scratch real-world RL

<span class="maturity maturity-upstream">Upstream runnable</span>
externally; <span class="maturity maturity-planned">Integration planned</span>
here.

[RLinf's Franka guide](https://rlinf.readthedocs.io/en/latest/rst_source/examples/embodied/franka.html)
demonstrates a broader real-world RL stack with CNN policies and OpenPI π0.5,
SAC, Cross-Q, RLPD, PPO-style training, Ray orchestration, RealSense or ZED
cameras, and multiple grippers.

That guide is a design reference, not evidence of compatibility with this
DROID deployment. It assumes its own controller, ROS/libfranka matrix, Ray
cluster, observation/action schema, task rewards, and firmware constraints.

Two candidate paths:

**Adapt robometer-policy-learning**
: Its PyTorch SAC, IQL, BC, CNN, and transformer modules are already vendored.
  Simulation configs exist, but there is no first-class from-scratch real DROID
  policy runbook.

**Integrate RLinf**
: Reuse its real-world orchestration and RLPD/Cross-Q workflows, then implement
  a DROID-compatible controller adapter and artifact contract.

Required work:

- choose Cartesian or joint action convention and enforce limits;
- define reset and intervention semantics;
- map DROID observations into the learner schema;
- collect demonstrations for RLPD and define train/validation splits;
- implement human and learned reward wrappers;
- validate Ray/controller failure behavior;
- compare against the same zero-shot and demonstration-only baselines.

No from-scratch real-robot method should be marked supported until it has a
task-independent environment interface and at least one reproducible hardware
result.

## World-model RL

<span class="maturity maturity-roadmap">Research roadmap</span>

There is no world-model RL implementation in this repository. A future system
could learn visual dynamics from DROID demonstrations and robot rollouts,
improve or plan in imagination, and deploy a constrained policy back to the
real robot.

```{mermaid}
flowchart LR
    Offline[DROID demonstrations] --> WM[Latent world model]
    Online[Safe robot rollouts] --> WM
    WM --> Imagine[Imagined trajectories]
    Imagine --> Learn[Policy or planner improvement]
    Learn --> Shield[Action adapter and safety shield]
    Shield --> Robot[Real robot evaluation]
    Robot --> Online
```

Before selecting code, define:

- observation tokenization and multi-camera timing;
- action convention and model horizon;
- reward source and uncertainty representation;
- offline/online data mixture;
- out-of-distribution detection;
- constraint or safety-shield behavior;
- sim-to-real and imagination-to-real validation;
- replay, checkpoint, and deterministic evaluation formats.

Acceptance requires open-loop prediction tests, counterfactual action tests,
uncertainty calibration, offline policy evaluation, shadow-mode deployment,
bounded hardware evaluation, and a matched model-free baseline.

## YAM embodiment

<span class="maturity maturity-roadmap">Research roadmap</span>

DROID is the only supported embodiment today. YAM should be added through an
embodiment adapter rather than branching every algorithm.

The adapter must provide:

- timestamped observations and logical camera roles;
- canonical proprioception and action metadata;
- reset, home, stop, and health operations;
- action limits and control-rate guarantees;
- episode transaction and artifact APIs;
- calibration identity;
- safety and operator-label hooks.

Reward models can remain embodiment-agnostic when they consume task text and
named RGB views. Trainers can remain robot-agnostic when the adapter exposes
the declared action convention and state schema.

## Research contributions welcome

The best contribution is not a new algorithm name in navigation. It is an
adapter, locked environment, self-check, matched baseline, safe runbook, and
complete result artifact that satisfies the {doc}`integration contract
<integration-contract>`.
