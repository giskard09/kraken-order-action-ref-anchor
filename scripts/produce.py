#!/usr/bin/env python3
"""
Produces an action_ref for a synthetic Kraken CLI `kraken order buy` spot
limit order (the AI-native trading CLI documented in krakenfx/kraken-cli),
following action-ref-v1 (argentum-core, JCS RFC 8785 + SHA-256)
byte-for-byte, and emits the artifacts needed to anchor + independently
verify it.

PROVENANCE: this is NOT captured from a running agent session, a real
Kraken account, or a real order. The request/response shapes are modeled
on krakenfx/kraken-cli's own public source: the private AddOrder request
fields (src/commands/trade.rs: pair, type, ordertype, volume, price,
userref, cl_ord_id) and the venue's own AddOrder response shape
(src/commands/trade.rs test fixture: {"descr": {"order": "..."},
"txid": [...]}), plus the CLI's own unified envelope fields (mode,
status, order_id) asserted in the same test
(master_order_mirrors_the_venue_txid_and_returns_a_live_receipt). No
claim that Kraken or kraken-cli emits action_ref today, and no claim of
integration, adoption, or endorsement by Kraken.
"""
import hashlib
import json
import os
import sys

OUT_DIR = sys.argv[1] if len(sys.argv) > 1 else "artifacts"
os.makedirs(OUT_DIR, exist_ok=True)


def jcs(obj):
    return json.dumps(obj, separators=(",", ":"), sort_keys=True, ensure_ascii=False)


def sha256_hex(s: str) -> str:
    return hashlib.sha256(s.encode()).hexdigest()


# --- 1. The four required action-ref-v1 preimage fields --------------------
# Per argentum-core/docs/spec/action-ref.md: only these four fields enter the
# hash. action_type mirrors the CLI's own subcommand name ("kraken order
# buy"); scope carries the asset class + venue endpoint (AddOrder, spot —
# kraken-cli's own --asset-class flag convention).
timestamp = "2026-08-20T23:00:00.000Z"
preimage = {
    "agent_id": "worked-example.kraken-order-action-ref-anchor",
    "action_type": "kraken.cli.order.buy",
    "scope": "kraken:spot:private/AddOrder:asset-class:crypto_spot",
    "timestamp": timestamp,
}
jcs_payload = jcs(preimage)
action_ref = sha256_hex(jcs_payload)

# --- 2. Additive envelope fields — order-specific context ------------------
# These do NOT enter the action_ref hash (per action-ref-v1: only the 4
# preimage fields are hashed). They travel alongside as declared context a
# downstream verifier can check independently:
#   params  — the AddOrder request's own declared fields, per
#             src/commands/trade.rs (pair, type, ordertype, volume, price).
#   result  — the venue's own AddOrder response shape (descr, txid) plus
#             kraken-cli's own unified envelope (mode, status, order_id),
#             both asserted verbatim in kraken-cli's own test
#             (master_order_mirrors_the_venue_txid_and_returns_a_live_receipt,
#             src/commands/trade.rs).
#
# The gap this closes: kraken-cli documents real execution-time controls
# (acknowledged=true gate, cancel-after dead-man's switch, least-privilege
# key guidance — README "For AI Agents") and a live issue on the repo
# (#42, BTCBoyd/Observer Protocol, 2026-08-10, closed without maintainer
# reply) raises a related but distinct question: verifiable *pre-trade*
# delegation/mandate scoping. Neither addresses *post-trade* evidence: the
# venue's own AddOrder response (txid, descr) is the sole record of what
# was requested and filled, and it lives only in the account's own order
# history — nothing about kraken-cli's envelope format makes a fill
# independently checkable by a third party without trusting the account
# holder's own report of it. action_ref does not verify the fill itself —
# it gives a third party a content-addressed identifier for the declared
# request/result pair, and an operator-independent anchor timestamp.
#
# pair/price/txid/descr values below are OBVIOUSLY-SYNTHETIC placeholders
# — no real Kraken account, no real order, no real fill was involved.
params = {
    "endpoint": "POST /0/private/AddOrder",
    "pair": "XBTUSD",
    "type": "buy",
    "ordertype": "limit",
    "volume": "0.01000000",
    "price": "50000.0",
    "cl_ord_id": "worked-example-order-0001",
}
params_digest = sha256_hex(jcs(params))

# Result — mirrors kraken-cli's own test fixture for the venue response
# (descr, txid) plus its unified envelope (mode, status, order_id).
result = {
    "mode": "live",
    "status": "submitted",
    "order_id": "OTEST1-WORKEDEX-00001",
    "descr": {"order": "buy 0.01000000 XBTUSD @ limit 50000.0"},
    "txid": ["OTEST1-WORKEDEX-00001"],
}
result_digest = sha256_hex(jcs(result))

envelope = {
    "packet_version": "1.0",
    "action_ref": action_ref,
    "hash_algo": "sha256",
    "preimage_format": "jcs-rfc8785-v1",
    "preimage": preimage,
    "capability": "kraken.cli.order.buy.spot_limit",
    "params_digest": params_digest,
    "result_digest": result_digest,
    "generated_at_utc": timestamp,
}

manifest = {
    "fixture_id": "kraken-order-buy-spot-limit-worked-example",
    "spec": "action-ref-v1 (argentum-core, docs/spec/action-ref.md)",
    "preimage": preimage,
    "jcs_payload": jcs_payload,
    "action_ref": action_ref,
    "anchor_ref_bytes32": "0x" + action_ref,
    "anchor_registry": "0x49fEcA52bC634a9Ab773226D16619deC547794aa",
    "anchor_chain": "Base mainnet (chainId 8453)",
    "envelope": envelope,
    "params": params,
    "result": result,
    "provenance": (
        "Synthetic worked example. Request/result shapes modeled on "
        "krakenfx/kraken-cli's own public source (src/commands/trade.rs): "
        "the private AddOrder request fields (pair, type, ordertype, "
        "volume, price) and the venue's own AddOrder response shape "
        "(descr, txid) plus kraken-cli's own unified envelope (mode, "
        "status, order_id), both asserted verbatim in kraken-cli's own "
        "test (master_order_mirrors_the_venue_txid_and_returns_a_live_"
        "receipt). NOT captured from a running agent session, a real "
        "Kraken account, or any real order. pair/price/txid/descr are "
        "synthetic placeholders. No claim that Kraken or kraken-cli "
        "emits action_ref today, and no claim of integration, adoption, "
        "or endorsement by Kraken."
    ),
}

with open(os.path.join(OUT_DIR, "manifest.json"), "w") as f:
    json.dump(manifest, f, indent=2, sort_keys=True)
    f.write("\n")

print("=== kraken-order-action-ref-anchor : producer ===")
print(f"jcs_payload = {jcs_payload}")
print(f"action_ref  = {action_ref}")
print(f"anchor ref (bytes32) = 0x{action_ref}")
print(f"wrote {OUT_DIR}/manifest.json")
