# Profiles

A **profile** is a reusable OLCRTC config template written in YAML. It's the core concept of the panel: you create a profile once, and every subscriber automatically gets their own container generated from it.

## What a profile is

Stored in the `profiles` table with three fields:

| Field | Meaning |
|-------|---------|
| `name` | Human-readable display name (e.g. "Germany — VP8") |
| `tag` | Short unique id used in container names and URLs (e.g. `de-vp8`). **Must be unique.** |
| `profile` | The OLCRTC YAML template itself |

You manage profiles in the panel's **Profiles** page: create, edit, delete, search. On create/edit the panel validates that the YAML parses (`yaml.safe_load`) but does not deeply check OLCRTC-specific fields — a malformed OLCRTC config will still save and only fail when a container tries to run it.

## Where profiles live

In PostgreSQL, not on disk. The YAML you paste is the *template*. The concrete per-user config that a container actually runs is generated on the fly and written inside that container at `/tmp/olcwave/config.yaml`.

## How a profile becomes a running config

When a subscription is requested for a user, for every profile the user doesn't already have a container for, the panel does this (`Subscriptions.profile_to_config`):

1. Parse the profile YAML.
2. **Generate `crypto.key`** — overwrites it with a fresh random 32-byte hex string (64 hex chars). You never set this yourself.
3. **Finish the room id** — takes `room.id`, splits it on `/`:
   - If it's a bare base URL like `https://jitsi.example.org` (three `/`-separated parts: `https:`, ``, `jitsi.example.org`), a random 16-byte hex room name is appended → `https://jitsi.example.org/<random>`.
   - If a room path is already present but empty, it's filled with a random name.
   - If a room name is already there, it's left alone.
4. Dump the result back to YAML.

Then it launches a container from this config (see below), and includes the location in the subscription bundle returned to the client.

### Container naming

Each container is named:

```
olcwave-<profile.tag>-<user.short_uuid>
```

for example `olcwave-de-vp8-rfWMHbDFsH_cPXRz`. This naming is not cosmetic — the traffic system parses it to find the owning user (`split("-")` must yield exactly three parts). **Don't put `-` inside a tag** or container ownership detection breaks.

## `crypto.key` — leave it empty

In your profile template, write:

```yaml
crypto:
  key: ""
```

Do **not** put a real key there. The panel generates a unique key per user per container at generation time. If you hard-code a key, everyone would share it — the panel overwrites it anyway, so there's no point.

## `provider: jitsi` and the room

When the auth provider is Jitsi, `room.id` is a Jitsi base URL. You only supply the server:

```yaml
auth:
  provider: jitsi
room:
  id: "https://jitsi.example.org"
```

The panel appends a random room name for each user, so every user gets an isolated room automatically. You don't create rooms by hand.

## Example profile

A minimal, valid-shaped OLCRTC profile (this mirrors the structure the panel reads and the fallback config it ships). Adjust to your real OLCRTC deployment:

```yaml
mode: cnc
auth:
  provider: jitsi
room:
  id: "https://jitsi.example.org"
crypto:
  key: ""
net:
  transport: datachannel
  dns: "0.0.0.0:53"
```

### With a non-datachannel transport

OLCRTC supports transports beyond `datachannel`. The panel recognizes `vp8channel`, `seichannel`, and `videochannel`, and reads a matching section for each. Example with VP8:

```yaml
mode: cnc
auth:
  provider: jitsi
room:
  id: "https://jitsi.example.org"
crypto:
  key: ""
net:
  transport: vp8channel
  dns: "0.0.0.0:53"
vp8:
  fps: 60
  batch: 64
```

## Fields the panel actually reads

When generating configs and subscription entries, the backend touches these keys. Anything else in your YAML is passed through untouched to OLCRTC.

| Key | Used for |
|-----|----------|
| `auth.provider` | Written into the subscription URI and OLCBox bundle (`auth_provider`) |
| `net.transport` | Selects the transport; must be one of `datachannel`, `vp8channel`, `seichannel`, `videochannel` |
| `room.id` | Room endpoint; auto-completed for Jitsi-style URLs |
| `crypto.key` | Overwritten with a fresh random key per user |
| `vp8.*` | If transport is `vp8channel`: `fps` (clamped 1–120) and `batch` (clamped 1–64) go into the bundle |
| `sei.*` | If transport is `seichannel`: `fps`, `batch_size`, `fragment_size`, `ack_timeout_ms` (used when building the compact URI) |
| `video.*` | If transport is `videochannel`: `width`, `height`, `fps`, `bitrate`, `hw`, `codec`, `qr_size`, `qr_recovery`, `tile_module`, `tile_rs` |

## Editing and deleting profiles

Both actions have side effects on running containers, on purpose:

- **Edit** a profile → all containers whose name contains that tag are **stopped**. They'll be regenerated with the new template the next time each user's subscription is fetched.
- **Delete** a profile → matching containers are **stopped and removed**.

So editing a profile is effectively "re-deploy this profile for everyone on their next subscription refresh."
