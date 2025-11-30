# CONTRIBUTING

### GET START

```sh

git clone git@github.com:alibaba/pont.git

cd pont

yarn (? yarn ???? link ?? packages)

npm run watch

```

? vscode ?????? debug:vscode-pont test:vscode-pont debug:pont-engine test:pont-engine ??? pont-engine ? vscode ???

### pont ??????

#### BaseClass

- name: string; ??

- description: string; ??

- properties: Property[]; ??

- templateArgs: StandardDataType[]; ??

#### Property

- dataType: StandardDataType;

- description?: string;

- name: string;

- required: boolean;

- in: 'query' | 'body' | 'path';

##### StandardDataType

- typeArgs = [] as StandardDataType[];

- typeName = ''; ?????? number???????Array?Object?'1' | '2' | 'a' ?

- isDefsType = false;

- templateIndex = -1; ??????????-1 ????

#### ??

```

class A<T> {

  a: T;

}

class B {

  b = A<number>

}

```

pont ???

```

{

  "name": "A",

  "properties": [{

    "name": "a",

    "required": false,

    "dataType": {

      templateIndex: 0,

      typeName: "T"

    }

  }],

  "templateArgs": [{ "typeName": "T" }],

}

{

  "name": "B",

  "properties": [{

    "name": "b",

    "required": false,

    "dataType": {

      templateIndex: -1,

      typeName: "A",

      typeArgs: [{ typeName: "number" }]

    }

  }],

  "templateArgs": [],

}

```