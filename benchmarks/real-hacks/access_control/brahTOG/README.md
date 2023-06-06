# 20221109 Brahtopg Arbitrary External Call Vulnerability


## Reference
- https://github.com/SunWeb3Sec/DeFiHackLabs/blob/main/README.md#20221109-brahtopg---arbitrary-external-call-vulnerability

## Hack: 9/11/2022

## Bug: Access Control
- File: BrahTOPG.sol
- Function: `zap`
- Location: Line 405 - 407.

However, the `zap` function is an `internal` function. Hence, we annotate bugs at two functions that call `zap` which are `zapIn` and `zapOut`.


## Source
- https://etherscan.io/address/0xD248B30A3207A766d318C7A87F5Cf334A439446D#code
