# kraken-order-action-ref-anchor

A worked example that derives an **`action_ref`** — a deterministic,
content-addressed identifier for an agent action
([`action-ref-v1`](https://github.com/giskard09/argentum-core/blob/master/docs/spec/action-ref.md)) —
for a synthetic `kraken order buy` spot limit order (as documented in
[`krakenfx/kraken-cli`](https://github.com/krakenfx/kraken-cli), "the
first AI-native CLI for trading crypto, stocks, forex, and derivatives"),
and anchors it permissionlessly on-chain, giving it a property the order
does not have on its own: an **externally verifiable, third-party-checkable
record of what was requested and returned**, independent of the account
holder's own order history.

The timestamp of the anchor is the point. This is not outreach and not a
claim of adoption — it is a worked example, byte-exact against the public
spec and `kraken-cli`'s own public source (`src/commands/trade.rs`).

> **Provenance, up front (read `PROVENANCE.md` for the full statement).**
> The `action_ref` here is derived exactly per `action-ref-v1` and
> cross-checked against argentum-core's own reference implementation. The
> request / result shapes are modeled on `kraken-cli`'s **public source**
> — but it was **NOT produced by a live agent session or a real Kraken
> account**: no real order, no real fill, no real funds moved. The order
> ID and fill details are obviously-synthetic placeholders mirroring
> kraken-cli's own test-fixture naming convention. Nothing here — on-chain
> or in this repo — implies that `kraken-cli` or Kraken integrated,
> endorsed, or participated. It is our worked example applying a public
> spec to their public source.

## Why now

`kraken-cli` documents real execution-time controls for AI agents —
paper/live parity, an `acknowledged=true` gate on dangerous tools,
`cancel-after` as a dead-man's switch, least-privilege key guidance. A
live issue on the repo itself
([#42](https://github.com/krakenfx/kraken-cli/issues/42), filed
2026-08-10, closed without maintainer reply) raises a related but
earlier-stage question: verifiable *pre-trade* delegation — who
authorized the agent, within what limits. This repo is about a
different, later-stage gap: once an order fills, the venue's own
response (`txid`, `descr`) is the sole record of what happened — nothing
about the CLI's envelope format makes that record independently
checkable by a third party without trusting the account holder's own
report of it. `action_ref` does not verify the fill itself — it answers
a narrower, adjacent question: given a declared request/result pair, can
a third party recompute a content-addressed identifier for it and
confirm an independent, operator-external timestamp of when it was
anchored?

## The idea

The `order buy` request's own documented interface
(`src/commands/trade.rs`) declares fields (`pair`, `type`, `ordertype`,
`volume`, `price`) and, once filled, the venue's own response (`descr`,
`txid`) — plus kraken-cli's own unified envelope (`mode`, `status`,
`order_id`) — lives only in the account's own order history.
`action_ref` closes part of that gap: a content-addressed identifier any
party can recompute from four declared fields (`agent_id`,
`action_type`, `scope`, `timestamp`) — no trust in the emitting system
required. This repo extends that with an **envelope** carrying
`params_digest` (the declared request) and `result_digest` (the declared
response) — hashes of the exact context a verifier would need to confirm
what was requested and returned, independently recomputable from the
declared JSON.

```
   kraken order buy (AddOrder)               public chain (Base)
   ┌───────────────────────────┐            ┌────────────────────────┐
   │ agent_id, action_type,     │  JCS+SHA256│ AnchorRegistry         │
   │ scope, timestamp           │───────────▶│  anchor(bytes32 ref)   │
   │ + params/result digests    │  action_ref│  Anchored(ref,by,time) │
   │   (envelope)                │            └────────────────────────┘
   └───────────────────────────┘             operator-independent
        no external record                   timestamp / finality
```

## Doctrine: spec-agnostic to Kraken's format

We derive `action_ref` from the four canonical fields only. We do **not**
ask Kraken or `kraken-cli` to adopt any anchoring infrastructure, change
their API, or emit any new fields. The integration lives entirely in how
an `order buy` call *could* be shaped and anchored; the CLI's documented
source is the input, the anchor is the added property.

## What's here

| Path | What it is |
|------|-----------|
| `scripts/produce.py` | Derives `action_ref` per `action-ref-v1` (JCS RFC 8785 + SHA-256) for a synthetic `order buy` call, plus the `params_digest`/`result_digest` envelope. |
| `verifier/verify.py` | Independent (stdlib-only) verifier: recomputes both digests from the declared JSON and confirms the matching `Anchored` event on Base mainnet. |
| `artifacts/` | The canonical instance: `manifest.json` (preimage, digests, envelope) and `anchor.json` (tx/block, once anchored). |
| `scripts/anchor.sh` | The exact `cast`-equivalent call used to anchor `action_ref`. |
| `PROVENANCE.md` | Exactly what is and isn't real about this artifact. Read it. |

## Reproduce

```bash
# 1. derive action_ref + the envelope digests
python3 scripts/produce.py artifacts

# 2. anchor action_ref on Base mainnet (see scripts/anchor.sh)

# 3. independently verify the derivation and the on-chain anchor
python3 verifier/verify.py
```

## The anchor

- **Registry:** `0x49fEcA52bC634a9Ab773226D16619deC547794aa` (same CREATE2
  address on Base 8453, Arbitrum One 42161, Ink 57073).
- **Function:** `anchor(bytes32 ref)` — permissionless, no owner/roles/funds.
- **Event:** `Anchored(bytes32 indexed ref, address indexed anchoredBy, uint256 timestamp)`.
- Tx `<TX_HASH>`, block `<BLOCK>`, Base mainnet. `artifacts/anchor.json`
  has the full record; `verifier/verify.py` confirms it independently
  against public RPC.

## Related worked examples

Same pattern, other formats: [`binance-onchain-pay-action-ref-anchor`](https://github.com/giskard09/binance-onchain-pay-action-ref-anchor)
(Binance), [`okx-agent-payments-action-ref-anchor`](https://github.com/giskard09/okx-agent-payments-action-ref-anchor)
(OKX), [`turnkey-action-ref-anchor`](https://github.com/giskard09/turnkey-action-ref-anchor)
(Turnkey), [`keycard-action-ref-anchor`](https://github.com/giskard09/keycard-action-ref-anchor)
(Keycard), [`dapr-history-anchor`](https://github.com/giskard09/dapr-history-anchor)
(Dapr Verifiable Execution), [`scitt-capsule-anchor`](https://github.com/giskard09/scitt-capsule-anchor)
(SCITT Agent Action Capsule), [`pay-kit-action-ref-anchor`](https://github.com/giskard09/pay-kit-action-ref-anchor)
(Solana Foundation pay-kit).

## License

MIT.
