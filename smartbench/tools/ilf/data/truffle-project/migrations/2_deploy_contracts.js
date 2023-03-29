// NOTE: need update the corresponding contract name.
var contract_name = artifacts.require("ContractName");

module.exports = function(deployer) {
  deployer.deploy(contract_name);
};
