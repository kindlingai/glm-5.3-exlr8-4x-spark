# For agents: boot GLM-5.3 on four DGX Sparks

You are booting this recipe for someone. Follow the steps in order and run each check. If a check fails, stop and
tell the person what failed. If this file and `compose.yaml` or `.env.example` disagree, follow those two files and
tell the person.

## 1. Check every box

- It is a DGX Spark or other GB10 box with 128 GB, and no other model runs on it: `docker ps` and `nvidia-smi` show
  none.
- Docker has the NVIDIA runtime: `docker info | grep -i nvidia`.
- Disk: about 90 GB for the model, 200 GB for the KV store (`KV_STORE` in `.env`):
  `df -h "$(docker info --format '{{.DockerRootDir}}')"`, or the `GR8_CACHE` directory if you set one.
- Hugging Face answers: `curl -sI https://huggingface.co`.
- Proactive memory compaction is off: `sysctl vm.compaction_proactiveness` prints 0. If not, as root:
  `sysctl -w vm.compaction_proactiveness=0`.
- TCP ports 7340 and 7341 are open between the boxes.
- The ConnectX ports are up: `ls /dev/infiniband` lists devices.

## 2. Write .env

Copy `.env.example` to `.env`. Set `PEERS` to the four LAN addresses, head first. Use the same `.env` on every box.
Ask the person before you change any other line.

## 3. Boot

On every box: `docker compose up -d`. The first boot fetches this box's part of the model (about 90 GB) and
converts the drafter. Follow it with `docker compose logs -f`.

## 4. Check

On the head:

- `docker compose exec gr8 /opt/gr8/gr8 glm53 health` exits 0.
- `docker compose exec gr8 /opt/gr8/gr8 glm53 smoke` passes 14 of 14.
- `curl -s localhost:8100/v1/models` shows `max_model_len` 513522.

## 5. Stop

On the head: `docker compose exec gr8 /opt/gr8/gr8 glm53 down`. Then `docker compose down` on every box.

## Rules for changes to this repo

- Every number in `README.md` and `kindling.json` comes from a measured run. Say the date, the box count and the
  engine build. Do not copy a number from another build without its date.
- `README.md`'s results and `kindling.json` say the same thing. A change to one changes the other, and
  `docs/card.png` is drawn again: `python3 bench/gif.py card kindling.json --out docs/card.png` from a gr8 checkout.
- The engine pin is one exact gr8 commit and one image digest. Never a moving tag alone, never a patched engine. An
  engine change goes to [kindlingai/gr8](https://github.com/kindlingai/gr8) as a pull request; this recipe then moves
  its pin to the merged commit or the next release.
- Run `python3 check.py` before you commit.
