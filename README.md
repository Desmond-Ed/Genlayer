Social Proof Identification Library

A reusable GenLayer contract for verifying user claims against public social profiles using non deterministic web access and LLM reasoning.

The contract fetches public profile content, evaluates a claim, and stores a confidence scored verification result on chain for reuse by other contracts.

Why this exists

Social verification is expensive and non deterministic.
This library centralizes that logic so applications can depend on a shared, consistent verification primitive instead of re implementing it.

How it works

- Fetches public profile data using gl.nondet.web.render

 - Evaluates the claim via LLM inference

- Stores verification results on chain in an ABI safe format

- Exposes read only methods for downstream contracts

- Consensus is based on semantic equivalence, not exact output matching.

Typical use cases

- DAO membership gating

- Reputation systems

- Grant or bounty eligibility

- Social identity proofs for GenLayer apps

Notes

- Verification is probabilistic

- Consumers should consider confidence scores and timestamps

- Public data only
