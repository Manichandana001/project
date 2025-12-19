const Audit = artifacts.require("Audit");

module.exports = function (deployer) {
  deployer.deploy(Audit);
};
