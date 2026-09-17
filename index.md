<div class="hero">

# Gokul's DROID Post-Training Setup

<p class="tagline">A public engineering guide for taking a pretrained robot
policy from zero-shot deployment to reward-guided online improvement on DROID.</p>

**Current platform:** DROID + Franka. **Next embodiment:** YAM.

</div>

```{warning}
Online reinforcement learning moves a physical robot while updating the policy
that controls it. Keep a trained operator and emergency stop at the robot.
Start with zero-action and zero-shot baselines; never use this guide as a
substitute for your robot manufacturer's safety process.
```

## What is here now

::::{grid} 1 2 2 2
:gutter: 2

:::{grid-item-card} DROID platform
<span class="maturity maturity-validated">Validated here</span>

Three-machine hardware split, cameras, control conventions, calibration
boundaries, data collection, and deployment prerequisites.

{doc}`Start with the system map <getting-started>`
:::

:::{grid-item-card} Reward models
<span class="maturity maturity-validated">Validated here</span>

Robometer-4B trajectory scoring and reward hosting, plus reproducible
comparisons with supported reward baselines.

{doc}`Choose a reward signal <reward-models/index>`
:::

:::{grid-item-card} DSRL post-training
<span class="maturity maturity-validated">Validated here</span>

SAC learns flow-noise actions around a frozen π0-DROID policy while Robometer
relabels completed trajectories.

{doc}`Understand the training topology <post-training/index>`
:::

:::{grid-item-card} Future methods
<span class="maturity maturity-planned">Integration planned</span>

EXPO-FT, from-scratch real-world RL, YAM, and world-model RL are documented
with explicit gaps instead of being presented as supported.

{doc}`Read the roadmap <roadmap>`
:::

::::

## Maturity is part of the interface

- <span class="maturity maturity-validated">Validated here</span> has been
  exercised on this DROID integration and has an operational runbook.
- <span class="maturity maturity-upstream">Upstream runnable</span> has a
  credible upstream implementation, but this integration has not completed
  its own hardware acceptance tests.
- <span class="maturity maturity-planned">Integration planned</span> has an
  identified codebase and concrete missing work.
- <span class="maturity maturity-roadmap">Research roadmap</span> is a design
  target. This repository does not claim an implementation.

## Recommended path

```{mermaid}
flowchart LR
    Bringup[DROID bring-up] --> Baseline[Matched zero-shot baseline]
    Baseline --> Reward[Validate reward model]
    Reward --> Train[DSRL online training]
    Train --> Eval[Deterministic evaluation]
    Eval --> Compare[Report matched results]
```

1. Establish safe DROID operation and a fixed task definition.
2. Record a matched zero-shot baseline with the exact prompt, camera, episode
   limit, action convention, and chunk horizon used for training.
3. Validate the reward model against held-out successes and diverse failures.
4. Run DSRL with isolated checkpoints and replay buffers per reward definition.
5. Evaluate the deterministic actor and publish complete experiment metadata.

```{toctree}
:maxdepth: 2
:caption: Foundation

getting-started
```

```{toctree}
:maxdepth: 2
:caption: Reward models

reward-models/index
reward-models/robometer
reward-models/baselines
reward-models/adapters
```

```{toctree}
:maxdepth: 2
:caption: Post-training

post-training/index
post-training/dsrl-topology
post-training/training-evaluation
```

```{toctree}
:maxdepth: 2
:caption: Community

roadmap
integration-contract
reproducibility
hosting
```
