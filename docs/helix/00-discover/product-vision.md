---
ddx:
  id: lintel.product-vision
  type: product-vision
  activity: discover
  authoring:
    home: repo
  links:
    - id: lintel.owner-intent
      kind: informed_by
---

# Lintel product vision

## Mission Statement

Give Batten application builders a GraphQL API and typed Relay clients from
UMF declarations, preserving the host's authority and the data runtime's meaning.

## Positioning

For Python application authors and Batten platform maintainers, Lintel is an
embeddable API runtime that derives GraphQL types and executable access from
approved UMF models. The alternative is handwritten Strawberry schemas,
resolvers and separately maintained TypeScript API types for every application.

## Vision

An application declares its data and operations once. Its backend publishes a
bounded API and its browser builds typed queries, fragments and mutations
against exactly that API. Runtime upgrades remain a platform responsibility.

**North Star**: One admitted model drives executable access and TypeScript client
artifacts, with observable agreement across the application boundary.

## User Experience

A builder selects a fabricated task board's records, relationships and commands.
Batten prepares the model and mounts Lintel. The builder compiles a Relay list
query and fragments, pages tasks, expands an assignee and submits an approved
command. The host enforces current authority and returns an attributable outcome.
An unsupported selected meaning prevents activation with a useful diagnostic.

## Target Market

| Attribute | Description |
| --- | --- |
| Who | Batten's trusted first-party Python application authors and platform maintainers. Broader demand is unverified. |
| Pain | Backend models, graph access, browser types and access checks drift when assembled per application. |
| Current Solution | Handwritten GraphQL schemas/resolvers and application-specific API/client wiring. |
| Why They Switch | Reuse declared semantics and platform-qualified execution across applications. |

## Key Value Propositions

| Value Proposition | Customer Benefit |
| --- | --- |
| Model-derived API | Builders maintain fewer copies of identities, fields and operations. |
| Relay interoperability | Browser teams reuse node refetch, fragments and connection pagination. |
| Batten embedding | Applications retain host admission, authority and lifecycle controls. |
| Explicit support limits | Teams see unavailable semantics before exposing a misleading API. |

## Success Definition

| Indicator | Measurement |
| --- | --- |
| Reduced duplicate modeling | Compare one Batten application's handwritten schema/client definitions before and after adoption. No numeric target is established. |
| Client/server agreement | Compare generated operation artifacts and actual endpoint results for the same admitted schema. |
| Safe cohort changes | Observe changed-schema/client diagnostics and consumer regression outcomes during platform upgrades. |

## Why Now

UMF has a published Python/native access cohort and Batten is framing packaged
runtimes and TypeScript application interfaces. The owner requested their shared
API layer now. Neither upstream availability nor this request proves Lintel delivery.
