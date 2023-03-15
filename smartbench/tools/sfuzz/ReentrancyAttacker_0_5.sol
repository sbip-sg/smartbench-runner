/* pragma solidity 0.5.1; */

contract ReentrancyAttacker {
    uint counter = 0;

    function () external payable {
        counter ++;
        if (counter <= 2) {
            (bool success, ) = msg.sender.call(abi.encode("revert()"));
            require(success, "Function call failed.");
        }
        revert();
    }
}
