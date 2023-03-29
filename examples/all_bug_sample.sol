
// SPDX-License-Identifier: MIT
pragma solidity 0.7.6;
pragma experimental ABIEncoderV2;

contract Test {
  struct Sig { uint8 v; bytes32 r; bytes32 s;}

  function claim(bytes32 _msg, Sig memory sig) public {
    address signer = ecrecover(_msg, sig.v, sig.r, sig.s);
    // require(signer == owner);
    // <yes> <report> LEAKING_ETHER
    payable(msg.sender).transfer(address(this).balance);
  }

  function vec_add(uint[2] memory a, uint[2] memory b) public returns (uint[2] memory c){
    // <yes> <report> ARITHMETIC_BUG
    c[0] = a[0] + b[0]; //overflow
    // <yes> <report> ARITHMETIC_BUG
    c[1] = a[1] + b[1]; //overflow
  }
}

contract BugSample {
    uint256 uzero = 0;
    uint256 umax = 0xffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffff;
    uint256 guards = 1;
    address winner;
    address owner;
    bool reentrancy_guard = false;

    constructor() {
        owner = msg.sender;
    }

    function overflow_add(uint256 b) public view returns (uint256) {
        // <yes> <report> ARITHMETIC_BUG
        return umax + b;
    }

    function underflow_minus(uint256 b) public view returns (uint256) {
        // <yes> <report> ARITHMETIC_BUG
        return uzero - b;
    }

    function truncation_inc(uint8 x) public pure returns (uint8) {
        // <yes> <report> ARITHMETIC_BUG
        return x + 1;
    }

    function reentrancy_withdraw() public {
        // <yes> <report> REENTRANCY
        require(guards > 0, "Must have some guards left");
        (bool success, ) = payable(msg.sender).call{value: 1 ether}(""); // REENTRANCY, UNCHECKED_SEND
        require(success);
        guards = 0;
    }

    function access_control(uint256 _guards, address addr) public {
        // <yes> <report> ACCESS_CONTROL
        require(reentrancy_guard == false);
        reentrancy_guard = true;
        (bool success, ) = address(addr).call("");
        require(success);
        guards = _guards;
        reentrancy_guard = false;
    }

    function assert_failure(uint256 _umax) public payable {
        // <yes> <report> ASSERTION_FAILURE
        assert(_umax > 0);
        umax = _umax;
    }

    function guess(uint256 i) public payable {
        require(msg.value > 0, "Must pay to play");

        if (block.timestamp % i == 89) {
            // <yes> <report> BLOCK_DEPENDENCY
            winner = msg.sender;
        }

        if (block.number % i == 97) {
            // <yes> <report> BLOCK_DEPENDENCY
            winner = msg.sender;
        }
    }

    function exception(address addr) public {
        // <yes> <report> UNHANDLED_EXCEPTION
        // <yes> <report> LACK_OF_ZERO_ADDRESS_VALIDATION
        address(addr).call("0x1234"); // EXCEPTION_DISORDER, ADDRESS_VALIDATION
    }

    function kill() public {
        // <yes> <report> UNSAFE_SELFDESTRUCT
        // <yes> <report> LEAKING_ETHER
        selfdestruct(msg.sender); // UNPROTECTED_SELFDESTRUCT
    }

    bool lock1;
    bool lock2;
    function unlock1 () public {
      lock1 = true;
    }
    function unlock2 () public {
      lock2 = true;
    }
    function three_step_bug() public {
        require(lock1);
        require(lock2);
      // <yes> <report> LEAKING_ETHER
      // <yes> <report> UNSAFE_SELFDESTRUCT
      selfdestruct(msg.sender); // UNCHECKED_SEND
    }

}
