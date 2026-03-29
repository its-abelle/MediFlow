// SPDX-License-Identifier: MIT
pragma solidity ^0.8.19;

/**
 * @title MediFlow
 * @dev Implements a TB diagnostic and accountability ledger.
 */
contract MediFlow {
    struct AIPrediction {
        string predictionId;
        bytes32 predictionHash; // SHA256 of the full prediction data
        bytes32 patientIdHash;  // SHA256 of the patient ID for lookup without exposure
        uint256 timestamp;
        address recordedBy;
    }

    struct DoctorValidation {
        string validationId;
        string predictionId;
        string doctorId;
        string decision;
        string signature; // HMAC signature or ECDSA if using wallet
        uint256 timestamp;
        address doctorAddress;
    }

    // Storage
    mapping(string => AIPrediction) public predictions; // predictionId -> Prediction
    mapping(string => DoctorValidation) public validations; // predictionId -> Validation
    mapping(bytes32 => string[]) public patientToPredictions; // patientIdHash -> predictionIds

    // Events
    event AIPredictionRecorded(string indexed predictionId, bytes32 indexed patientIdHash, bytes32 predictionHash);
    event DoctorValidationRecorded(string indexed predictionId, string validationId, string decision);

    /**
     * @dev Records an AI prediction hash on-chain.
     */
    function recordAIPrediction(
        string memory _predictionId,
        bytes32 _predictionHash,
        bytes32 _patientIdHash
    ) public {
        require(bytes(predictions[_predictionId].predictionId).length == 0, "Prediction already exists");

        predictions[_predictionId] = AIPrediction({
            predictionId: _predictionId,
            predictionHash: _predictionHash,
            patientIdHash: _patientIdHash,
            timestamp: block.timestamp,
            recordedBy: msg.sender
        });

        patientToPredictions[_patientIdHash].push(_predictionId);

        emit AIPredictionRecorded(_predictionId, _patientIdHash, _predictionHash);
    }

    /**
     * @dev Records a doctor's validation of an AI prediction.
     */
    function recordDoctorValidation(
        string memory _validationId,
        string memory _predictionId,
        string memory _doctorId,
        string memory _decision,
        string memory _signature
    ) public {
        require(bytes(predictions[_predictionId].predictionId).length > 0, "Prediction does not exist");
        require(bytes(validations[_predictionId].validationId).length == 0, "Validation already exists for this prediction");

        validations[_predictionId] = DoctorValidation({
            validationId: _validationId,
            predictionId: _predictionId,
            doctorId: _doctorId,
            decision: _decision,
            signature: _signature,
            timestamp: block.timestamp,
            doctorAddress: msg.sender
        });

        emit DoctorValidationRecorded(_predictionId, _validationId, _decision);
    }

    /**
     * @dev Retrieves prediction IDs for a given patient.
     */
    function getPatientPredictions(bytes32 _patientIdHash) public view returns (string[] memory) {
        return patientToPredictions[_patientIdHash];
    }
}
