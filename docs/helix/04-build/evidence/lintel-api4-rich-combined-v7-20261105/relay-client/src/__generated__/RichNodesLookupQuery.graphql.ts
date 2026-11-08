/**
 * @generated SignedSource<<1a737ebd37f275aec8ef3e6761d52468>>
 * @lightSyntaxTransform
 */

/* tslint:disable */
/* eslint-disable */
// @ts-nocheck

import { ConcreteRequest } from 'relay-runtime';
import { DecimalString } from "../scalars";
export type RichNodesLookupQuery$variables = {
  ids: ReadonlyArray<string>;
};
export type RichNodesLookupQuery$data = {
  readonly nodes: ReadonlyArray<{
    readonly amount?: DecimalString;
    readonly enabled?: boolean;
    readonly id: string;
    readonly owner?: string;
    readonly payload?: string;
    readonly taskValue?: string;
  } | null | undefined>;
};
export type RichNodesLookupQuery = {
  response: RichNodesLookupQuery$data;
  variables: RichNodesLookupQuery$variables;
};

const node: ConcreteRequest = (function(){
var v0 = [
  {
    "defaultValue": null,
    "kind": "LocalArgument",
    "name": "ids"
  }
],
v1 = [
  {
    "kind": "Variable",
    "name": "ids",
    "variableName": "ids"
  }
],
v2 = {
  "alias": null,
  "args": null,
  "kind": "ScalarField",
  "name": "id",
  "storageKey": null
},
v3 = {
  "kind": "InlineFragment",
  "selections": [
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
    }
  ],
  "type": "Note",
  "abstractKey": null
},
v4 = {
  "kind": "InlineFragment",
  "selections": [
    {
      "alias": null,
      "args": null,
      "kind": "ScalarField",
      "name": "taskValue",
      "storageKey": null
    }
  ],
  "type": "Task",
  "abstractKey": null
};
return {
  "fragment": {
    "argumentDefinitions": (v0/*:: as any*/),
    "kind": "Fragment",
    "metadata": null,
    "name": "RichNodesLookupQuery",
    "selections": [
      {
        "alias": null,
        "args": (v1/*:: as any*/),
        "concreteType": null,
        "kind": "LinkedField",
        "name": "nodes",
        "plural": true,
        "selections": [
          (v2/*:: as any*/),
          (v3/*:: as any*/),
          (v4/*:: as any*/)
        ],
        "storageKey": null
      }
    ],
    "type": "Query",
    "abstractKey": null
  },
  "kind": "Request",
  "operation": {
    "argumentDefinitions": (v0/*:: as any*/),
    "kind": "Operation",
    "name": "RichNodesLookupQuery",
    "selections": [
      {
        "alias": null,
        "args": (v1/*:: as any*/),
        "concreteType": null,
        "kind": "LinkedField",
        "name": "nodes",
        "plural": true,
        "selections": [
          {
            "alias": null,
            "args": null,
            "kind": "ScalarField",
            "name": "__typename",
            "storageKey": null
          },
          (v2/*:: as any*/),
          (v3/*:: as any*/),
          (v4/*:: as any*/)
        ],
        "storageKey": null
      }
    ]
  },
  "params": {
    "cacheID": "fcab6ef12741b76b4f6e36571151d451",
    "id": null,
    "metadata": {},
    "name": "RichNodesLookupQuery",
    "operationKind": "query",
    "text": "query RichNodesLookupQuery(\n  $ids: [ID!]!\n) {\n  nodes(ids: $ids) {\n    __typename\n    id\n    ... on Note {\n      owner\n      enabled\n      amount\n      payload\n    }\n    ... on Task {\n      taskValue\n    }\n  }\n}\n"
  }
};
})();

(node as any).hash = "acac4cdb1d51245fa3f7324087638be7";

export default node;
