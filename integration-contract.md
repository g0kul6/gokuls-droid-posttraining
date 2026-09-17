# Community method integration contract

A method appears as **validated here** only when every required section below
is implemented, tested, and documented.

## Method manifest

Add a machine-readable manifest:

```yaml
schema_version: 1
method:
  name: example_method
  family: noise_steering
  maturity: integration_planned
  source_revision: "<git-sha>"
base_policy:
  family: pi0_droid
  checkpoint: "<immutable-id>"
observation:
  required_views: [exterior, wrist]
  state_layout: "<documented-layout>"
action:
  space: normalized_joint_velocity
  shape: [8]
  control_hz: 15
  chunk_horizon: 8
reward:
  backend: robometer
  variant: "<immutable-id>"
  success_source: human
artifacts:
  replay_schema: 1
  checkpoint_schema: 1
  episode_schema: 1
```

## Embodiment adapter

The robot boundary must provide:

- `health`: robot, gripper, controller, and calibration identity;
- `reset` and `home`: bounded, observable state transitions;
- `observe`: timestamped images and finite state arrays;
- `step`: one declared action convention with limits;
- `stop`: a safe hold or stop independent of the learner;
- episode begin/commit/abort semantics;
- stable logical camera names separate from hardware serials.

Hardware addresses and credentials belong in runtime configuration, never the
manifest.

## Policy adapter

Declare transport, request fields, response shape, chunk length, action units,
gripper meaning, timeout, and stale-response behavior. Save the raw response
before clipping or smoothing.

For a VLA, the exact task string and image preprocessing are model inputs and
part of experiment identity.

## Reward adapter

Meet the {doc}`reward contract <reward-models/index>` and provide:

- offline scorer;
- server health and model-info endpoints;
- deterministic sample fixture;
- online relabel client;
- shape/range/finiteness checks;
- explicit failure policy;
- immutable reward variant.

## Replay schema

Every transition needs:

- episode, frame, query, and chunk indices;
- pre-action state and timestamps;
- raw policy output;
- executed action;
- terminal/truncation reason;
- raw environment and learned rewards;
- relabel status and reward identity;
- observation references or embedded features;
- feature/model revisions.

Replay mutation must be transactional. A transition cannot be sampled as
relabelled before all reward fields are committed.

## Checkpoint schema

Checkpoint actor and critic weights are insufficient. Include optimizer states,
target networks, temperature, counters, replay, normalization, method manifest,
software revisions, and data schema versions.

Implement:

1. save to temporary path;
2. structural validation;
3. atomic publication;
4. load into a fresh process;
5. deterministic action parity before and after restore.

## Safety evidence

Before physical online learning:

- unit tests for adapters and limits;
- simulated or dummy-environment episode;
- zero-action full-stack test;
- bounded action test;
- emergency-stop drill;
- network-drop and model-timeout tests;
- interrupted-step replay test;
- checkpoint restore test;
- operator review of workspace and reset sequence.

## Baseline and evaluation

Every result includes:

- matched zero-shot base policy;
- demonstration-only or SFT baseline when relevant;
- deterministic post-trained evaluation;
- task definition and success rubric;
- episode-level outcomes and videos;
- seeds and confidence intervals;
- all excluded/aborted episodes with reasons;
- hardware and software fingerprint.

## Maturity promotion

**Research roadmap → integration planned**
: A source codebase and interface design are selected; missing work is listed.

**Integration planned → upstream runnable**
: Upstream install and example run are reproducible outside this DROID stack.

**Upstream runnable → validated here**
: The DROID adapter, safety tests, matched baseline, training run, restore, and
  deterministic evaluation all pass from a clean setup.

Maturity can be downgraded when a dependency, firmware, or checkpoint revision
invalidates that evidence.
