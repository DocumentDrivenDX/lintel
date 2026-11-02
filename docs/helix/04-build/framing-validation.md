---
ddx:
  id: lintel.framing-validation
  authoring:
    home: repo
---

# Framing validation — 2026-11-02

## Scope and result

The installed HELIX 0.20.0 instance validator checked 19 Lintel governed artifacts
and Batten's SD-002/updated FEAT-002. All 21 final results have zero blocking
findings and zero warnings. See [exact validator output](evidence/validator-results.json).
Research/intake/index/evidence notes are checked as packet content, not falsely
represented as catalog artifact types with their own templates.

Local checks found 12 functional requirements mapped to six features and six
stories, with 24 distinct acceptance IDs, planned named assertions and required
citation strings. All 54 checked local Markdown links resolve; IDs, local trace
targets, declared schema source and pinned example checksum agree. The report
link was checked after creating this record. See [packet checks](evidence/packet-checks.json).
These are planning mappings: every product acceptance test is currently unrun.

## Execution

Used the installed `skills/helix/scripts/validate-instance.py` with its matching
`workflows` catalog. The default Python interpreter lacked PyYAML. Repeated the
check using Batten's Python 3.11 interpreter with an existing cached PyYAML 6.0.3
package on PYTHONPATH; no package installation or network access was needed.
Initial feature-language/story-format and SD title findings were corrected;
only affected artifacts were rechecked where appropriate. Final results are retained.

## Change boundary

Created the separate sibling Lintel packet, HELIX marker, README and AGENTS.md.
Added Batten SD-002, an interface requirement and a README pointer. Existing Batten
frontmatter and concurrent work were preserved. No UMF or runtime implementation
was changed. The source inventory distinguishes published cohorts and local candidates.
The framing packet was initially Git-initialized without a commit or remote.
The owner subsequently authorized source repository creation, commit and push;
Git history and remote refs record the source publication result.

## Qualification limits

No Lintel server code, frozen protocol contracts, dependency locks, installed
artifact tests, native database replay, GraphQL execution, Relay compilation,
browser journey, Databricks deployment or family-site update was performed.
Required upstream spikes/public contracts and boundary checks remain implementation
prerequisites. Structural document validation grants none of these capabilities.

The family entry and intended project Pages path are prepared; actual family
catalog ownership and documentation-site publication remain open. Source
repository publication is a separate owner-authorized delivery action.

## Publication boundary review

The source repository is public at https://github.com/DocumentDrivenDX/lintel .
Before the authorized initial commit, the 21 governed artifacts were revalidated
with zero blocking findings/warnings and 54 local Markdown links resolved.
The staged packet passed Git whitespace checks.

The reviewed dependency direction is explicit: Lintel defines neutral public
execution ports; Batten owns its optional `batten.lintel` implementation in the
Batten repository. Lintel imports no Batten package; generic Batten core/ASGI
modules do not import or discover Lintel. The embedding composition root injects
the binding and router. This is architectural intent; import-checker enforcement
and installed/native integration remain unimplemented.

Batten's feature, integration design and index changes remain in Batten. They
are not copied into the Lintel source packet. Cross-repository links use GitHub
source URLs rather than assuming adjacent filesystem checkouts.
