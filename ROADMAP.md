# Roadmap

Next (0.1.0a7 and later), roughly in order:

1. A stack-backed execution port over UMF Access / Truss on PostgreSQL. Needs a
   non-development `umf-access` or `umf-truss` release on PyPI.
2. Serve Relay connections and relationships from `lintel serve` (needs a port that
   implements `connection` and `related_many`; the in-memory port does not).
3. Publish or drop `umf_access_generated_executor` so prepared-API v2 to v4 can be built
   by users.
4. Mutations (commands and outcomes), TypeScript Relay clients and Batten embedding, as
   specified in `docs/helix/`.
5. A documentation site, once there is something beyond the README to say.

Follow-up for the dependency pin: widen `umf-core` to `>=0.10.11,<0.11` once umf 0.10.11
is released.
