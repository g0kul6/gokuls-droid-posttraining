# DROID system map and setup

<span class="maturity maturity-validated">Validated here</span>

This site begins after the mechanical installation described by the official
[DROID documentation](https://droid-dataset.github.io/droid/). It focuses on
the additional contracts needed for post-training.

## Reference deployment

Use roles, not hard-coded machine names:

```{mermaid}
flowchart LR
    subgraph robotCell [Robot cell]
        FR3[Franka FR3]
        NUC[Real-time robot host]
        FR3 <-->|FCI and gripper| NUC
    end
    subgraph operatorNode [Robot laptop]
        Cameras[Exterior and wrist cameras]
        Rollout[15 Hz rollout process]
        Cameras --> Rollout
    end
    subgraph gpuNode [GPU host]
        Policy[Base policy server]
        Trainer[Post-training server]
        Reward[Reward server]
        Trainer --> Policy
        Trainer --> Reward
    end
    Rollout <-->|robot RPC| NUC
    Rollout <-->|one request per action chunk| Trainer
```

The robot host owns deterministic low-level control. The laptop owns cameras,
wall-clock control timing, operator labels, and rollout artifacts. The GPU host
owns model inference, replay, optimization, and learned reward inference.

## Required hardware and software

### Robot cell
- A supported Franka arm with a firmware/libfranka pairing verified against
  the manufacturer's compatibility matrix.
- A configured gripper with a stable device path.
- A real-time robot host connected directly to the arm.
- A physical emergency stop and an operator with an unobstructed view.

### Robot laptop
- DROID installed and able to reset and command the robot without an ML model.
- One calibrated exterior camera and one calibrated wrist camera at minimum.
- A second exterior camera is useful for audit video but is not automatically
  a policy input.
- Stable network routes to the robot host and GPU host.

### GPU host
- Independent environments for the base policy, reward model, and trainer.
- Enough GPU memory to avoid unsafe inference stalls or out-of-memory restarts.
- Persistent storage for checkpoints, replay buffers, videos, and metadata.
- Optional W&B or another experiment tracker.

## Configuration template

Create a private environment file outside version control:

```bash
export ROBOT_RPC_HOST="<robot-host>"
export ROBOT_RPC_PORT="<robot-port>"
export POLICY_HOST="127.0.0.1"
export POLICY_PORT="<policy-port>"
export TRAINER_PORT="<trainer-port>"
export REWARD_ADDRESS="127.0.0.1:<reward-port>"

export TASK="Describe one observable task outcome"
export EXTERNAL_CAMERA="left"
export LEFT_CAMERA_ID="<left-camera-serial>"
export RIGHT_CAMERA_ID="<right-camera-serial-or-empty>"
export WRIST_CAMERA_ID="<wrist-camera-serial>"

export MAX_TIMESTEPS="400"
export OPEN_LOOP_HORIZON="8"
export ENV_STEP_BUDGET="10000"
```

Never commit credentials, tunnel URLs, robot addresses, serial numbers, API
keys, or experiment-tracker tokens to a public repository.

## Bring-up gates

Complete each gate before the next:

1. **Robot-only:** home, read state, command a bounded motion, and test gripper.
2. **Camera-only:** identify serials, verify physical view names, and check
   calibration after any camera motion.
3. **Zero-action:** run the complete network path while commanding no movement.
4. **Zero-shot:** collect a fixed evaluation set from the unmodified base policy.
5. **Reward audit:** score held-out videos and inspect temporal progress.
6. **Trainer self-check:** construct actor, critics, replay buffer, save/restore,
   and take a synthetic gradient step without the robot.
7. **Online training:** begin with reduced bounds and direct supervision.

## Safety invariants

- Human success remains authoritative until a reward model has task-specific
  evidence strong enough to justify automatic termination.
- A network timeout must stop or hold; it must never replay stale actions.
- The action convention must be explicit at every boundary. π0-DROID commonly
  executes normalized joint-velocity commands, while MolmoAct2-DROID emits
  absolute joint targets.
- A failed or interrupted robot step is not added to replay.
- Scene reset occurs while no policy action can reach the robot.
- Checkpoint restore must verify task, reward identity, action geometry,
  observation layout, and feature dimensions.

## What belongs elsewhere

The local operator handbook may contain site-specific camera serials, network
addresses, and browser terminals. This public guide intentionally does not.
Deploying a static copy of this site cannot open terminals or control a robot.
