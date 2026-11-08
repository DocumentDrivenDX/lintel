/**
 * @generated SignedSource<<ab4c6fdbacd9bf9a60795ac4d0f054e2>>
 * @lightSyntaxTransform
 */

/* tslint:disable */
/* eslint-disable */
// @ts-nocheck

import { ConcreteRequest } from 'relay-runtime';
import { FragmentRefs } from "relay-runtime";
export type RichCollectionsQuery$variables = {
  noteAfter?: string | null | undefined;
  noteFirst?: number | null | undefined;
  taskAfter?: string | null | undefined;
  taskFirst?: number | null | undefined;
};
export type RichCollectionsQuery$data = {
  readonly " $fragmentSpreads": FragmentRefs<"RichNotesFragment" | "RichTasksFragment">;
};
export type RichCollectionsQuery = {
  response: RichCollectionsQuery$data;
  variables: RichCollectionsQuery$variables;
};

const node: ConcreteRequest = (function(){
var v0 = {
  "defaultValue": null,
  "kind": "LocalArgument",
  "name": "noteAfter"
},
v1 = {
  "defaultValue": 2,
  "kind": "LocalArgument",
  "name": "noteFirst"
},
v2 = {
  "defaultValue": null,
  "kind": "LocalArgument",
  "name": "taskAfter"
},
v3 = {
  "defaultValue": 2,
  "kind": "LocalArgument",
  "name": "taskFirst"
},
v4 = [
  {
    "kind": "Variable",
    "name": "after",
    "variableName": "noteAfter"
  },
  {
    "kind": "Variable",
    "name": "first",
    "variableName": "noteFirst"
  }
],
v5 = [
  {
    "kind": "Variable",
    "name": "after",
    "variableName": "taskAfter"
  },
  {
    "kind": "Variable",
    "name": "first",
    "variableName": "taskFirst"
  }
],
v6 = {
  "alias": null,
  "args": null,
  "kind": "ScalarField",
  "name": "cursor",
  "storageKey": null
},
v7 = {
  "alias": null,
  "args": null,
  "kind": "ScalarField",
  "name": "id",
  "storageKey": null
},
v8 = {
  "alias": null,
  "args": null,
  "kind": "ScalarField",
  "name": "__typename",
  "storageKey": null
},
v9 = {
  "alias": null,
  "args": null,
  "concreteType": "PageInfo",
  "kind": "LinkedField",
  "name": "pageInfo",
  "plural": false,
  "selections": [
    {
      "alias": null,
      "args": null,
      "kind": "ScalarField",
      "name": "endCursor",
      "storageKey": null
    },
    {
      "alias": null,
      "args": null,
      "kind": "ScalarField",
      "name": "hasNextPage",
      "storageKey": null
    },
    {
      "alias": null,
      "args": null,
      "kind": "ScalarField",
      "name": "hasPreviousPage",
      "storageKey": null
    },
    {
      "alias": null,
      "args": null,
      "kind": "ScalarField",
      "name": "startCursor",
      "storageKey": null
    }
  ],
  "storageKey": null
};
return {
  "fragment": {
    "argumentDefinitions": [
      (v0/*:: as any*/),
      (v1/*:: as any*/),
      (v2/*:: as any*/),
      (v3/*:: as any*/)
    ],
    "kind": "Fragment",
    "metadata": null,
    "name": "RichCollectionsQuery",
    "selections": [
      {
        "args": (v4/*:: as any*/),
        "kind": "FragmentSpread",
        "name": "RichNotesFragment"
      },
      {
        "args": (v5/*:: as any*/),
        "kind": "FragmentSpread",
        "name": "RichTasksFragment"
      }
    ],
    "type": "Query",
    "abstractKey": null
  },
  "kind": "Request",
  "operation": {
    "argumentDefinitions": [
      (v1/*:: as any*/),
      (v0/*:: as any*/),
      (v3/*:: as any*/),
      (v2/*:: as any*/)
    ],
    "kind": "Operation",
    "name": "RichCollectionsQuery",
    "selections": [
      {
        "alias": null,
        "args": (v4/*:: as any*/),
        "concreteType": "NoteConnection",
        "kind": "LinkedField",
        "name": "notes",
        "plural": false,
        "selections": [
          {
            "alias": null,
            "args": null,
            "concreteType": "NoteEdge",
            "kind": "LinkedField",
            "name": "edges",
            "plural": true,
            "selections": [
              (v6/*:: as any*/),
              {
                "alias": null,
                "args": null,
                "concreteType": "Note",
                "kind": "LinkedField",
                "name": "node",
                "plural": false,
                "selections": [
                  (v7/*:: as any*/),
                  {
                    "alias": null,
                    "args": null,
                    "kind": "ScalarField",
                    "name": "owner",
                    "storageKey": null
                  },
                  {
                    "alias": null,
                    "args": null,
                    "kind": "ScalarField",
                    "name": "enabled",
                    "storageKey": null
                  },
                  {
                    "alias": null,
                    "args": null,
                    "kind": "ScalarField",
                    "name": "amount",
                    "storageKey": null
                  },
                  {
                    "alias": null,
                    "args": null,
                    "kind": "ScalarField",
                    "name": "payload",
                    "storageKey": null
                  },
                  (v8/*:: as any*/)
                ],
                "storageKey": null
              }
            ],
            "storageKey": null
          },
          (v9/*:: as any*/)
        ],
        "storageKey": null
      },
      {
        "alias": null,
        "args": (v4/*:: as any*/),
        "filters": null,
        "handle": "connection",
        "key": "RichNotesFragment_notes",
        "kind": "LinkedHandle",
        "name": "notes"
      },
      {
        "alias": null,
        "args": (v5/*:: as any*/),
        "concreteType": "TaskConnection",
        "kind": "LinkedField",
        "name": "tasks",
        "plural": false,
        "selections": [
          {
            "alias": null,
            "args": null,
            "concreteType": "TaskEdge",
            "kind": "LinkedField",
            "name": "edges",
            "plural": true,
            "selections": [
              (v6/*:: as any*/),
              {
                "alias": null,
                "args": null,
                "concreteType": "Task",
                "kind": "LinkedField",
                "name": "node",
                "plural": false,
                "selections": [
                  (v7/*:: as any*/),
                  {
                    "alias": null,
                    "args": null,
                    "kind": "ScalarField",
                    "name": "taskValue",
                    "storageKey": null
                  },
                  (v8/*:: as any*/)
                ],
                "storageKey": null
              }
            ],
            "storageKey": null
          },
          (v9/*:: as any*/)
        ],
        "storageKey": null
      },
      {
        "alias": null,
        "args": (v5/*:: as any*/),
        "filters": null,
        "handle": "connection",
        "key": "RichTasksFragment_tasks",
        "kind": "LinkedHandle",
        "name": "tasks"
      }
    ]
  },
  "params": {
    "cacheID": "20e80c3b12cac834487bc29ff1fddde3",
    "id": null,
    "metadata": {},
    "name": "RichCollectionsQuery",
    "operationKind": "query",
    "text": "query RichCollectionsQuery(\n  $noteFirst: Int = 2\n  $noteAfter: String\n  $taskFirst: Int = 2\n  $taskAfter: String\n) {\n  ...RichNotesFragment_4zj9Eo\n  ...RichTasksFragment_2n70UV\n}\n\nfragment RichNotesFragment_4zj9Eo on Query {\n  notes(first: $noteFirst, after: $noteAfter) {\n    edges {\n      cursor\n      node {\n        id\n        owner\n        enabled\n        amount\n        payload\n        __typename\n      }\n    }\n    pageInfo {\n      endCursor\n      hasNextPage\n      hasPreviousPage\n      startCursor\n    }\n  }\n}\n\nfragment RichTasksFragment_2n70UV on Query {\n  tasks(first: $taskFirst, after: $taskAfter) {\n    edges {\n      cursor\n      node {\n        id\n        taskValue\n        __typename\n      }\n    }\n    pageInfo {\n      endCursor\n      hasNextPage\n      hasPreviousPage\n      startCursor\n    }\n  }\n}\n"
  }
};
})();

(node as any).hash = "fecfa7311ae93bcdd6d9b5db2915bda8";

export default node;
