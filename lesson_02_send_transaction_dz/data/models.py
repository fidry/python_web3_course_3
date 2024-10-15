TokenABI = [
    {
        'constant': True,
        'inputs': [],
        'name': 'name',
        'outputs': [{'name': '', 'type': 'string'}],
        'payable': False,
        'stateMutability': 'view',
        'type': 'function'
    },
    {
        'constant': True,
        'inputs': [],
        'name': 'symbol',
        'outputs': [{'name': '', 'type': 'string'}],
        'payable': False,
        'stateMutability': 'view',
        'type': 'function'
    },
    {
        'constant': True,
        'inputs': [],
        'name': 'decimals',
        'outputs': [{'name': '', 'type': 'uint256'}],
        'payable': False,
        'stateMutability': 'view',
        'type': 'function'
    },
    {
        'constant': True,
        'inputs': [{'name': 'who', 'type': 'address'}],
        'name': 'balanceOf',
        'outputs': [{'name': '', 'type': 'uint256'}],
        'payable': False,
        'stateMutability': 'view',
        'type': 'function'
    },
    {
        'constant': True,
        'inputs': [
            {'name': 'spender', 'type': 'address'},
            {'name': 'amount', 'type': 'uint256'}
        ],
        'name': 'approve',
        'outputs': [],
        'payable': False,
        'stateMutability': 'nonpayable',
        'type': 'function'
    },
    {
        'constant': True,
        'inputs': [
            {'name': 'owner', 'type': 'address'},
            {'name': 'spender', 'type': 'address'},
        ],
        'name': 'allowance',
        'outputs': [
            {'name': '', 'type': 'uint256'},
        ],
        'payable': False,
        'stateMutability': 'view',
        'type': 'function'
    },
]
