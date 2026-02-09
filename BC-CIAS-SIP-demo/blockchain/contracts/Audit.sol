// SPDX-License-Identifier: MIT
pragma solidity ^0.8.0;

contract Audit {
    struct Record {
        address auditor;
        bool result;
        uint timestamp;
        string proof;
    }

    Record[] public records;

    function submitAudit(bool _result, string memory _proof) public {
        records.push(Record(msg.sender, _result, block.timestamp, _proof));
    }

    function getAudit(uint index) public view returns (address, bool, uint, string memory) {
        require(index < records.length, "Invalid index");
        return (
            records[index].auditor,
            records[index].result,
            records[index].timestamp,
            records[index].proof
        );
    }

    function getCount() public view returns (uint) {
        return records.length;
    }
}
