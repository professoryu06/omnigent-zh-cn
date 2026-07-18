"""Modal deploy glue for the Omnigent server.

Runs the standard server image (``ghcr.io/omnigent-ai/omnigent-server``)
as a single always-on Modal web server, proxying HTTP / SSE / WebSocket
traffic to the same Docker entrypoint every other container platform
uses (``deploy/docker/entrypoint.py``). See README.md for the
walkthrough.
"""

import subprocess

import modal

# The CI-built server image — ships the gitignored web UI bundle that a
# source build can't produce (same reason every other platform pulls it;
# see deploy/docker/Dockerfile.prebuilt). Modal injects its client
# runtime into the image's Python at image-build time.
SERVER_IMAGE = "ghcr.io/omnigent-ai/omnigent-server:latest"
# The image's uvicorn port (deploy/docker/Dockerfile: EXPOSE 8000).
SERVER_PORT = 8000
# First boot runs DB migrations over the network (~1 minute on Neon);
# 300 s leaves comfortable headroom before Modal declares startup failed.
STARTUP_TIMEOUT_S = 300

app = modal.App("omnigent")

# Persists uploaded agent bundles / artifacts across container restarts
# and redeploys — unlike Heroku / Cloudflare Containers, the artifact
# store is durable here.
artifacts = modal.Volume.from_name("omnigent-artifacts", create_if_missing=True)


@app.function(
    image=modal.Image.from_registry(SERVER_IMAGE),
    # DATABASE_URL, OMNIGENT_ACCOUNTS_COOKIE_SECRET, and
    # OMNIGENT_ACCOUNTS_BASE_URL — created in the README's step 1.
    secrets=[modal.Secret.from_name("omnigent-deploy")],
    volumes={"/data/artifacts": artifacts},
    # One always-on container: the runner registry lives in server
    # memory, so traffic must not be spread across containers
    # (max_containers), and scale-to-zero would tear down live runner
    # tunnels (min_containers).
    min_containers=1,
    max_containers=1,
    # The server's working-set floor (~512 MB–1 GB; see deploy/README.md's
    # memory-floor note) — Modal's defaults sit below it.
    cpu=1.0,
    memory=1024,
    # Each proxied request / WebSocket holds one Modal "input" for its
    # lifetime, and an input ends when this timeout lapses — so use the
    # platform maximum (24 h). Runners auto-reconnect after the cut.
    timeout=24 * 60 * 60,
)
# Every in-flight request / SSE stream / WebSocket holds one input on the
# single container, so this is the simultaneous-connection budget; 1000
# comfortably covers a small team's runners + browser tabs + terminals.
@modal.concurrent(max_inputs=1000)
@modal.web_server(port=SERVER_PORT, startup_timeout=STARTUP_TIMEOUT_S)
def server() -> None:
    """
    Launch the standard Docker entrypoint and let Modal proxy to it.

    ``@modal.web_server`` forwards HTTP / SSE / WebSocket traffic to
    ``SERVER_PORT`` once the process starts listening. Running the
    entrypoint as a subprocess (rather than importing the FastAPI app
    into Modal's own ASGI runner) keeps this deploy on the exact same
    code path as every other container platform: migrations, store
    wiring, auth defaults, and uvicorn flags like the runner tunnel's
    ``ws_max_size`` all come from ``deploy/docker/entrypoint.py``.
    """
    subprocess.Popen(["python", "/app/entrypoint.py"])
