# DSRL + Robometer topology

## Validated Topology C

<span class="maturity maturity-validated">Validated here</span>

```{mermaid}
flowchart LR
    subgraph cell [Robot cell]
        Robot[Franka]
        RobotHost[Robot RPC host]
        Robot <--> RobotHost
    end
    subgraph laptop [Robot laptop]
        ZED[ZED cameras]
        Rollout[Rollout client at 15 Hz]
        ZED --> Rollout
    end
    subgraph gpu [GPU host]
        Trainer[HTTP DSRL trainer]
        Pi0[Patched pi0_droid]
        SAC[Transformer SAC and replay]
        RM[Robometer reward server]
        Trainer --> Pi0
        Trainer --> SAC
        Trainer --> RM
    end
    Rollout <--> RobotHost
    Rollout <-->|one round trip per 8 actions| Trainer
```

The laptop owns the control clock. It captures camera and proprioceptive state,
requests an action chunk, executes actions locally, and sends completed episode
data plus the human label to the trainer. Network inference is outside the
eight executed control steps, so those steps do not each incur a remote call.

## Generic process map

Use environment variables rather than copying site-specific GPU IDs or hosts:

```bash
# GPU host: patched π0-DROID server
cd /path/to/openpi
CUDA_VISIBLE_DEVICES="${POLICY_GPU}" \
uv run scripts/serve_policy.py --port "${POLICY_PORT}" \
  policy:checkpoint \
  --policy.config=pi0_droid \
  --policy.dir=gs://openpi-assets/checkpoints/pi0_droid
```

The server must expose DSRL noise injection and prefix features. Startup
metadata must report action horizon 10.

```bash
# GPU host: Robometer relabel server
cd /path/to/robometer-policy-learning
PYTHONPATH="/path/to/robometer-policy-learning:/path/to/robometer" \
CUDA_VISIBLE_DEVICES="${REWARD_GPU}" \
/path/to/robometer-python \
  scripts/start_reward_relabel_server.py \
  reward_model=robometer \
  reward_model.model_path="robometer/Robometer-4B" \
  server.host=127.0.0.1 \
  server.port="${REWARD_GRPC_PORT}" \
  device=cuda \
  server.image_keys='["observation/exterior_image_1_left"]'
```

```bash
# GPU host: DSRL trainer
cd /path/to/dsrl_pi0
INSTRUCTION="${TASK}" \
WANDB_ENTITY="${WANDB_ENTITY}" \
DEVICE_ID="${TRAINER_GPU}" \
DSRL_ROBOMETER_PORT="${TRAINER_PORT}" \
REWARD_RELABEL_ADDRESS="127.0.0.1:${REWARD_GRPC_PORT}" \
bash examples/scripts/run_train_server_robometer_reward.sh
```

```bash
# Robot laptop: tunnel and rollout
ssh -N -o ServerAliveInterval=15 \
  -L "${TRAINER_PORT}:127.0.0.1:${TRAINER_PORT}" \
  "${GPU_SSH_TARGET}"

cd /path/to/dsrl_pi0
bash examples/scripts/run_rollout_laptop_robometer_reward.sh
```

The trainer health response is the authority for task, camera selection,
maximum timesteps, action geometry, and reward identity. The laptop should
refuse to move when its local hardware mapping disagrees.

## One episode

For a 400-step task with eight actions per query:

1. The operator resets the scene and confirms readiness.
2. The first 1,200 control steps across the run use warmup exploration.
3. Every query sends the current policy observation to the trainer.
4. SAC selects eight 32-dimensional noise rows.
5. The trainer cyclically fills the ten-step π0 flow horizon.
6. π0 returns a ten-action robot chunk; the laptop executes eight.
7. Fifty query transitions are retained for a complete 400-step episode.
8. The operator labels success or failure.
9. Robometer scores the ordered exterior-camera prefixes.
10. The trainer composes reward, updates replay, and performs scheduled
    gradient steps before admitting the next episode.

Scene reset and training can overlap conceptually, but robot motion remains
gated until the trainer has committed the previous episode.

## Reward and transition semantics

```text
transition reward = sparse environment reward + progress reward
```

The exact sparse convention must be recorded. Some implementations use `-1`
per nonterminal transition and `0` on success; others use `0` and a positive
terminal success. Do not compare returns until the convention is verified.

`gamma` applies to one replay transition, not necessarily one 15 Hz robot
action. If one transition represents eight executed actions, document whether
the implementation uses `gamma`, `gamma^8`, or another effective discount.

## Upstream serial topology

<span class="maturity maturity-upstream">Upstream runnable</span>

The upstream
[real-robot guide](https://github.com/robometer/robometer-policy-learning/blob/main/docs/REAL_ROBOT_README.md)
uses:

- `droid_remote_server.py` on the robot machine;
- a length-prefixed TCP/pickle robot protocol;
- `train_dsrl.py --config-name dsrl_remote_robot_async_relabel_config`;
- in-process π0 and SAC on the training machine;
- a localhost gRPC Robometer server;
- an async wrapper that retroactively updates replay.

This path is useful to community adopters who want upstream structure, but its
Hydra defaults differ from the validated topology. In particular, verify
critic count, noise bounds, discounting, observation encoders, and checkpoint
format before claiming parity.

## Preflight

Before connecting the robot:

```bash
cd /path/to/dsrl_pi0
bash -c \
  '. examples/scripts/_env_robometer.sh && python examples/check_robometer_parity.py --verbose'

python examples/selfcheck_robometer.py --feature-dim 2048
```

The parity check compares the configured integration against its reference.
The self-check builds the real networks and replay buffer, takes a synthetic
gradient step, and verifies save/restore rebinding.

## Port policy

Assign separate ports for:

- base-policy inference;
- reward gRPC;
- DSRL trainer HTTP;
- optional sparse and alternative-reward trainers.

Only the trainer endpoint needs to cross from GPU host to robot laptop. Keep
policy and reward ports bound to loopback where the topology allows it.
