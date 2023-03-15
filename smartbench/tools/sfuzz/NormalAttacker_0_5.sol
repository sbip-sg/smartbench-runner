/* # filename: NormalAttacker.sol */

/* pragma solidity 0.5.0; */

contract NormalAttacker {
    uint counter = 0;

    function () external payable {
        revert();
    }
}
