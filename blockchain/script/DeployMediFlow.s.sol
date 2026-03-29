//SPDX-License-Identifier: MIT
pragma solidity ^0.8.0;

import {Script} from "forge-std/Script.sol";
import {MediFlow} from "../src/MediFlow.sol";

contract DeployMediFlow is Script {
    function run() external {
        vm.startBroadcast();

        MediFlow mediFlow = new MediFlow();

        vm.stopBroadcast();
    }
}
