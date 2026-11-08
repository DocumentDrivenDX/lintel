/**
 * @generated SignedSource<<07850a77dbb3a0529d07d47ef3a1a7ff>>
 * @lightSyntaxTransform
 */

/* tslint:disable */
/* eslint-disable */
// @ts-nocheck

import { ConcreteRequest } from 'relay-runtime';
import { DecimalString } from "../scalars";
export type RichNodeLookupQuery$variables = {
  id: string;
};
export type RichNodeLookupQuery$data = {
  readonly node: {
    readonly amount?: DecimalString;
    readonly enabled?: boolean;
    readonly id: string;
    readonly owner?: string;
    readonly payload?: string;
    readonly taskValue?: string;
  } | null | undefined;
};
export type RichNodeLookupQuery = {
  response: RichNodeLookupQuery$data;
  variables: RichNodeLookupQuery$variables;
};

const node: ConcreteRequest = (function(){
var v0 = [
  {
    "defaultValue": null,
    "kind": "LocalArgument",
    "name": "id"
  }
],
v1 = [
  {
    "kind": "Variable",
    "name": "id",
    "variableName": "id"
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
    "name": "RichNodeLookupQuery",
    "selections": [
      {
        "alias": null,
        "args": (v1/*:: as any*/),
        "concreteType": null,
        "kind": "LinkedField",
        "name": "node",
        "plural": false,
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
    "name": "RichNodeLookupQuery",
    "selections": [
      {
        "alias": null,
        "args": (v1/*:: as any*/),
        "concreteType": null,
        "kind": "LinkedField",
        "name": "node",
        "plural": false,
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
    "cacheID": "d3f764c8818ede132dfe49afb9f6c50d",
    "id": null,
    "metadata": {},
    "name": "RichNodeLookupQuery",
    "operationKind": "query",
    "text": "query RichNodeLookupQuery(\n  $id: ID!\n) {\n  node(id: $id) {\n    __typename\n    id\n    ... on Note {\n      owner\n      enabled\n      amount\n      payload\n    }\n    ... on Task {\n      taskValue\n    }\n  }\n}\n"
  }
};
})();

(node as any).hash = "f42272a3a5bf73d1278af820394d61ce";

export default node;
