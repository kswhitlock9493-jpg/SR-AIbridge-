/* hardhat_resonance_plugin.js - CCSS Level-III Hardhat plug-in */
const { task } = require("hardhat/config");
const HarmonyThreshold = 0.9995;
const weights = [0.30, 0.25, 0.20, 0.15, 0.10];

function computeMu(scores) {
  const clamped = scores.map(s => Math.max(Math.min(s, 1.0), 1e-12));
  const logSum = weights.reduce((sum, w, i) => sum + w * Math.log(clamped[i]), 0);
  return Math.exp(logSum);
}

async function checkCH() {
  return (
    (await cyberAlarmClear()) &&
    (await multisigQuorumIntact()) &&
    (await chainTipConfirmationsGe6()) &&
    (await adminOverrideOff()) &&
    (await smartContractAuditRecent())
  );
}

task("resonance-gate", "Block high-value tx if grid is disharmonious")
  .addParam("value", "tx value in BTC")
  .setAction(async ({ value }, hre) => {
    if (parseFloat(value) < 10) return; // only gate ≥ 10 BTC
    const scores = [
      await queryNodeSyncHealth(),
      await queryMempoolFeeConvergence(),
      await queryKeyCustodyIntegrity(),
      await querySmartContractAuditScore(),
      await queryOracleStability(),
    ];
    const mu = computeMu(scores);
    const ch = await checkCH();
    if (mu >= HarmonyThreshold && ch) {
      console.log("Crypto: TX RESONANCE GO");
    } else {
      throw new Error("Crypto: TX HALT – safe-state activated");
    }
  });
