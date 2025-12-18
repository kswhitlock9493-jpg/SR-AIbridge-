(* waterwaste_plc.st - IEC 61131-3 ST PLC kernel (MISRA-ST subset) *)
FUNCTION_BLOCK ResonanceMonitor
VAR_INPUT
    scores      : ARRAY[1..5] OF REAL;
    weights     : ARRAY[1..5] OF REAL := [0.30, 0.25, 0.20, 0.15, 0.10];
    harmonyThreshold : REAL := 0.9995;
    minScore    : REAL := 1e-12;
END_VAR
VAR_OUTPUT
    mu          : REAL;
    ch          : BOOL;
    decision    : (CHANGE_GO, CHANGE_HALT);
END_VAR
VAR
    i           : INT;
    logSum      : REAL;
END_VAR

logSum := 0.0;
FOR i := 1 TO 5 DO
    IF scores[i] < minScore THEN scores[i] := minScore; END_IF;
    IF scores[i] > 1.0 THEN scores[i] := 1.0; END_IF;
    logSum := logSum + weights[i] * LN(scores[i]);
END_FOR;
mu := EXP(logSum);

ch := noEPA breach() AND
      labChainOfCustodyOK() AND
      coldChainTempOK() AND
      pesticideBelowTolerance() AND
      carbonCreditPositive() AND
      exportLicenceValid();

IF (mu >= harmonyThreshold) AND ch THEN
    decision := CHANGE_GO;
ELSE
    decision := CHANGE_HALT;
    triggerAutoheal();
END_IF;
END_FUNCTION_BLOCK
