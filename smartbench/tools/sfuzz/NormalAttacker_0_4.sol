/* # filename: NormalAttacker.sol */

contract NormalAttacker {
    uint counter = 0;
    function() payable {
        revert();
    }
}
