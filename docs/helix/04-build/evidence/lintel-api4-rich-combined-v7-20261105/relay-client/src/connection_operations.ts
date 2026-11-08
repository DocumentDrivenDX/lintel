const connections = graphql`
  query RichCollectionsQuery(
    $noteFirst: Int = 2
    $noteAfter: String
    $taskFirst: Int = 2
    $taskAfter: String
  ) {
    ...RichNotesFragment @arguments(first: $noteFirst, after: $noteAfter)
    ...RichTasksFragment @arguments(first: $taskFirst, after: $taskAfter)
  }

  fragment RichNotesFragment on Query
  @argumentDefinitions(
    first: { type: "Int", defaultValue: 2 }
    after: { type: "String" }
  )
  @refetchable(queryName: "RichNotesPaginationQuery") {
    notes(first: $first, after: $after)
      @connection(key: "RichNotesFragment_notes") {
      edges {
        cursor
        node {
          id
          owner
          enabled
          amount
          payload
        }
      }
      pageInfo {
        endCursor
        hasNextPage
        hasPreviousPage
        startCursor
      }
    }
  }

  fragment RichTasksFragment on Query
  @argumentDefinitions(
    first: { type: "Int", defaultValue: 2 }
    after: { type: "String" }
  )
  @refetchable(queryName: "RichTasksPaginationQuery") {
    tasks(first: $first, after: $after)
      @connection(key: "RichTasksFragment_tasks") {
      edges {
        cursor
        node {
          id
          taskValue
        }
      }
      pageInfo {
        endCursor
        hasNextPage
        hasPreviousPage
        startCursor
      }
    }
  }
`;
void connections;

const recordLookups = graphql`
  query RichNodeLookupQuery($id: ID!) {
    node(id: $id) {
      id
      ... on Note {
        owner
        enabled
        amount
        payload
      }
      ... on Task {
        taskValue
      }
    }
  }

  query RichNodesLookupQuery($ids: [ID!]!) {
    nodes(ids: $ids) {
      id
      ... on Note {
        owner
        enabled
        amount
        payload
      }
      ... on Task {
        taskValue
      }
    }
  }
`;
void recordLookups;
