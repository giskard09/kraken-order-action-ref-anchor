# Provenance — read this before drawing any conclusion

This document states exactly what is real and what is synthetic in this
worked example. Hard honesty is the point: the artifact is worthless if its
provenance is fuzzy.

## What is real

- `action_ref` is derived exactly per `action-ref-v1`
  ([argentum-core/docs/spec/action-ref.md](https://github.com/giskard09/argentum-core/blob/master/docs/spec/action-ref.md)):
  SHA-256 of the RFC 8785 JCS canonicalization of the four preimage fields
  (`agent_id`, `action_type`, `scope`, `timestamp`). The value in
  `artifacts/manifest.json` was independently cross-checked against
  argentum-core's own reference implementation
  (`plugins/agt_evidence_anchor/action_ref.py`) and matches byte-for-byte.
- The request and result shapes are modeled on `krakenfx/kraken-cli`'s
  own public source, not invented:
  - `src/commands/trade.rs` declares the private `AddOrder` request
    fields used by `kraken order buy <PAIR> <VOL> --type limit --price P`
    (`pair`, `type`, `ordertype`, `volume`, `price`, among others).
  - The same file's own test,
    `master_order_mirrors_the_venue_txid_and_returns_a_live_receipt`,
    asserts the venue's `AddOrder` response shape verbatim
    (`{"descr": {"order": "..."}, "txid": [...]}`) and kraken-cli's own
    unified envelope (`mode`, `status`, `order_id`) — the shapes modeled
    for `params`/`result` below.
  - README.md documents this command as executing real trades against
    the live exchange ("Interacts with the live Kraken exchange and can
    execute real financial transactions").
- **The on-chain anchor is PENDING — not yet executed.** Everything above
  it (`action_ref`, digests, cross-check) is real and final; the anchor
  transaction itself is not. Automated execution of the anchor
  transaction was blocked by this session's own safety classifier (a
  real, irreversible mainnet transaction) — deliberately not overridden.
  Pending manual execution by the repo's operator:
  - **ref (bytes32):** `0x3c46814c3c17d89d7e1d638f9b399752f2f3e2ac03ccf822d51b50ec446ae3fc`
  - **registry:** `0x49fEcA52bC634a9Ab773226D16619deC547794aa` (AnchorRegistry, Base mainnet, chainId 8453)
  - **function:** `anchor(bytes32 ref)` — permissionless
  - **calldata:** `0xeecdf9273c46814c3c17d89d7e1d638f9b399752f2f3e2ac03ccf822d51b50ec446ae3fc`
    (selector `0xeecdf927` for `anchor(bytes32)`, independently verified —
    matches the selector used by every prior anchor in this series, e.g.
    the OKX worked example's on-chain tx input data)
  - **signer:** owner wallet, via `giskard-signer` (key never leaves the vault)
  - See `scripts/anchor.sh` for the exact `cast`-equivalent call.
  Once executed, `artifacts/anchor.json` will carry the real tx/block and
  this section will be updated with `verifier/verify.py`'s `ALL CHECKS PASS`
  confirmation against public Base RPC.

## What is synthetic — declared

- **No running agent session, real Kraken account, or real order was
  involved.** `agent_id`, `timestamp`, `params`, and `result` are all
  constructed in `scripts/produce.py`, not captured from a live
  `kraken order buy` call or any actual spot fill.
- **`params.cl_ord_id`, `result.order_id`, `result.txid`, and
  `result.descr` are obviously-synthetic placeholders** —
  `OTEST1-WORKEDEX-00001` mirrors kraken-cli's own test-fixture naming
  convention (`OTEST1-...`), not a real venue txid. Nothing here was
  submitted to Kraken's actual API, and no real funds moved.

## What this therefore does and does not show

- **Does show:** the `action_ref` derivation applies unchanged to
  `kraken-cli`'s own documented `order buy` request/response shape —
  same four fields, same JCS + SHA-256 path used by every other emitter
  in the spec's cross-reference list, and the same envelope pattern
  already anchored for Binance
  (`giskard09/binance-onchain-pay-action-ref-anchor`), OKX
  (`giskard09/okx-agent-payments-action-ref-anchor`), Turnkey, Keycard,
  Dapr, SCITT, pay-kit, `wdk-mcp-toolkit`, and `agent-toolkit`. It also
  surfaces a distinction specific to this repo: an open issue on
  kraken-cli itself (#42, filed by a third party, 2026-08-10, closed
  without maintainer reply) raises verifiable *pre-trade* mandate
  scoping — who delegated authority, within what limits — as an open
  question. That is a different, earlier-stage problem than the one this
  repo addresses: *post-trade* evidence. Once an order fills, the
  venue's own response (`txid`, `descr`) is the sole record of what was
  requested and returned — nothing about kraken-cli's envelope format
  makes that record independently checkable by a third party without
  trusting the account holder's own report of it. `action_ref` does not
  verify the fill itself — it gives a third party a content-addressed
  identifier for the declared request/result pair, and an
  operator-independent anchor timestamp, regardless of whether the
  underlying fill was accurately reported.
- **Does not show:** that `kraken-cli` or Kraken has integrated,
  endorsed, or adopted `action_ref`. It is our worked example applying a
  public spec to `kraken-cli`'s public source. No claim of "Kraken
  integrated us," no claim of on-chain adoption.
