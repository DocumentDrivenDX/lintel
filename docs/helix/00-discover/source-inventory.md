---
ddx:
  id: lintel.source-inventory
  type: research-note
  activity: discover
  authoring:
    home: repo
  links:
    - id: lintel.owner-intent
      kind: informed_by
---

# Source inventory and evidence limits

The [manifest](sources/manifest.json) records exact hashes and checkout heads for
inspected public UMF, Weft and Batten sources. Some primary-checkout files and
candidate Batten packages are uncommitted. Working-tree hashes identify what was
read; a Git HEAD alone does not claim those candidate files were published.
Engine source is neither copied nor imported into Lintel. One small public UMF
commerce fixture is pinned for offline design/schema inspection; it is not the
final task-board application and adds no Lintel execution claim.

Published UMF 0.5.2 qualification differs from older narrative notes and Batten's
newer local Weft pin. Use the actual intersecting installed cohort for build work.
The active UMF Rust-migration proposal is recorded as candidate direction.
Native, package, browser and deployed claims remain separate.

## Standards and framework references

- [GraphQL September 2025](https://spec.graphql.org/September2025/): language and execution reference edition; selected feature support requires tests.
- [Relay server guide](https://relay.dev/docs/guides/graphql-server-specification/): object refetch and connection conventions.
- [Relay object identification](https://relay.dev/graphql/objectidentification.htm): Node and node lookup/field-stability requirements.
- [Relay connections](https://relay.dev/graphql/connections.htm): edges, cursors, PageInfo and supported pagination conventions.
- [Relay type emission](https://relay.dev/docs/guides/type-emission/): operation/fragment TypeScript artifacts; guide served v21.0.1 during inspection.
- [Strawberry FastAPI](https://strawberry.rocks/docs/integrations/fastapi): GraphQLRouter, context injection and async resolver behavior. Observed documentation 0.339.1; implementation dependency remains unselected/unlocked.
- [Strawberry Relay](https://strawberry.rocks/docs/guides/relay): existing Python Relay integration. It does not qualify Lintel's backend pagination.
- [Databricks Apps development](https://docs.databricks.com/aws/en/dev-tools/databricks-apps/app-development): Python app/configuration development.
- [Databricks app configuration](https://docs.databricks.com/aws/en/dev-tools/databricks-apps/app-runtime): app.yaml execution configuration.
- [Databricks app authorization](https://docs.databricks.com/aws/en/dev-tools/databricks-apps/auth): app and user authority are distinct.

Reference retrieval was read-only; no workspace access, live app deployment,
package resolution, GraphQL execution or Relay compilation was performed.
Public documentation is consulted, not vendored. Version locks and publication
schema sources belong to the implementation cohort when chosen.

## Family publication lookup

The requested root `https://documentdrivendx.github.io/` could not be retrieved,
and `DocumentDrivenDX/DocumentDrivenDX.github.io` returned 404. This does not prove
the site/catalog does not exist. Batten's local public configuration identifies
its project site at `/batten/`; family registry ownership remains unresolved.


## Specification expansion references

The 2026-11-02 expansion rechecked the public Python UMF exports, current core
0.10 schema and Batten TablePort; its minimal existing operation shape does not
claim the newly specified neutral execution protocol.
[GraphQL over HTTP working draft](https://http-spec.graphql.org/draft/) was consulted
on 2026-11-02; CONTRACT-005 defines a selected finite profile rather than claiming
full draft conformance. Relay/GraphQL references above informed the target profile.
No live provider or compiler execution was performed as research.
