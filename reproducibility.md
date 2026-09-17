# Reproducibility and troubleshooting

## Run identity

Use a human-readable prefix plus a machine-resolved manifest:

```text
<task-slug>__<method>__<reward-family>__<reward-variant>__<date>
```

Do not encode the entire configuration in a filename. Save the full resolved
configuration beside the run.

## Revision capture

Capture each independent checkout:

```bash
git -C /path/to/droid rev-parse HEAD
git -C /path/to/base-policy rev-parse HEAD
git -C /path/to/post-training rev-parse HEAD
git -C /path/to/reward-model rev-parse HEAD
```

Also save environment lockfiles, GPU/driver details, robot firmware, controller
version, camera calibration hashes, model revisions, and startup logs.

## Matched experiment rules

- One exact task prompt.
- One physical scene and reset distribution.
- One selected policy view.
- Same control rate, episode length, and executed chunk horizon.
- Same success rubric and evaluator.
- Separate run identity for every reward definition.
- Separate replay and checkpoints for sparse, Robometer, TopReward, zero-shot
  API, and few-shot API rewards.
- Candidate checkpoint selection performed without looking at final test
  episodes.

## Artifact validation

Automate checks that:

- camera videos have equal frame counts;
- traces have one row per executed action/frame;
- timestamps increase;
- states and actions are finite;
- policy-query and chunk indices are consistent;
- progress arrays match replay transition count;
- progress and success stay within declared ranges;
- task and reward identity agree across config, replay, checkpoint, and result;
- progress rows are append-only and episode IDs are unique.

## Common failures

### Robot moves correctly until the gripper command

Inspect the executed gripper trace before changing policy code. Confirm the
USB device path, container mapping, command convention, and whether a later
policy output reopened the gripper.

### Camera role mismatch

Map physical views to hardware serials from live images. Logical `left` and
`right` are configuration names; calibration remains keyed by serial. Stop if
the trainer and laptop disagree.

### Low control frequency

Separate policy-query time from action-execution time. If execution-only steps
are slow, inspect camera grabs, robot RPC, video encoding, and CPU contention.
Do not first blame the remote model.

### Reward server returns the wrong number of values

Verify frame sampler, policy-query count, maximum frames, image key, and whether
the backend emits per-frame, per-prefix, or episode-only output. Reject rather
than broadcasting or truncating silently.

### Reward looks good but policy degrades

Check reward scale, return composition, discount per replay transition,
terminal handling, Q-value scale, actor saturation, and reward hacking. Compare
raw human labels and raw reward curves.

### Restore produces worse or different actions

Run deterministic pre/post save action parity. Confirm acting references point
to loaded weights, target networks and normalizers were restored, and replay
identity passed validation.

### API reward stops mid-run

Treat quota, authentication, timeout, and provider errors as explicit relabel
failures. Preserve the episode and retry or apply the declared sparse fallback;
never store fabricated zeros.

## Minimum release evidence

A community release should include:

- clean-install transcript;
- preflight/self-check output;
- resolved manifests;
- zero-shot and deterministic result CSVs;
- representative videos and reward curves;
- checkpoint plus checksum;
- known failures and aborted episode counts;
- exact commands with only public placeholders.

## Reporting limitations

Small real-robot studies have high variance. State episode counts, scene-reset
procedure, human intervention, reward-model tuning data, and whether task
selection occurred after seeing results. “Best checkpoint” is not an unbiased
final result unless selection and test episodes are separated.
