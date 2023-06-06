# 20230203 - Orion Protocol - Reentrancy

## Reference
- https://github.com/SunWeb3Sec/DeFiHackLabs#20230203---orion-protocol---reentrancy

## Hack: 23/02/2023

## Bug: Reentrancy
- File: 07\_17\_PoolFunctionality.sol
- Functions: User can call the external function `doSwapThroughOrionPool` that calls the internal function `_doSwapTokens`
- Location: Line 181-193.

## Source
- https://bscscan.com/address/0xd2997f29b5285ab74bbca62d26c6723a74500183#code
