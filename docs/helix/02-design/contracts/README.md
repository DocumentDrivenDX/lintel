# Lintel shared contracts

These are target versioned interfaces for the specified MVP, not implemented
runtime APIs or upstream support claims. Source syntax validation and actual
GraphQL/Relay/native conformance are separate checks.

| Contract | Owns | Authoritative source |
| --- | --- | --- |
| [001](CONTRACT-001-exposure-and-projection.md) | Explicit exposure, identity/digests and admission | `../schemas/exposure.schema.json` |
| [002](CONTRACT-002-neutral-execution-port.md) | Neutral async execution, sessions/cursors/outcomes | `../interfaces/ports.pyi` |
| [003](CONTRACT-003-graphql-relay-profile.md) | Server Node/connection/scalar/command behavior | Contract plus illustrative `../examples/task-board.graphql` |
| [004](CONTRACT-004-typescript-relay-clients.md) | Client artifacts, scalar checks, network/store lifecycle | `../schemas/client-manifest.schema.json` |
| [005](CONTRACT-005-hosting-and-resource-bounds.md) | Host configuration, HTTP and resource/lifecycle policy | `../schemas/host-profile.schema.json` |

[Example journey](../examples/README.md) states what the logical source alone
cannot supply. S-01–05 in the upstream inventory remain required qualification.
No native/provider/compiler version is silently selected by a profile name.
