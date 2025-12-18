//! OilGas_Edge.rs - Zone-2 explosive-proof edge node (forbid unsafe)
#![forbid(unsafe_code)]
use std::time::Duration;
const HARMONY_THRESHOLD: f64 = 0.9995;
const MIN_SCORE: f64 = 1e-12;

pub struct OilGasContext {
    pub scores: Vec<f64>,
    pub weights: Vec<f64>,
}

impl OilGasContext {
    pub fn calculate_mu(&self) -> f64 {
        let mut log_sum = 0.0;
        for (w, s) in self.weights.iter().zip(self.scores.iter()) {
            let s_clipped = s.clamp(MIN_SCORE, 1.0);
            log_sum += w * s_clipped.ln();
        }
        log_sum.exp()
    }
}

pub async fn check_ch() -> bool {
    no_permit_violation().await &&
    bop_interlock_ok().await &&
    h2s_ok().await &&
    cyber_threat_ok().await &&
    insurance_ok().await
}

#[tokio::main]
async fn main() {
    let ctx = OilGasContext {
        scores: vec![0.98, 0.97, 1.0, 0.96, 0.99],
        weights: vec![0.30, 0.25, 0.20, 0.15, 0.10],
    };
    loop {
        let scores = vec![
            read_wellhead_coherence().await,
            read_pipeline_health().await,
            read_flare_stability().await,
            read_cyber_health().await,
            read_operator_alertness().await,
        ];
        let mu = ctx.calculate_mu();
        let ch = check_ch().await;
        match (mu >= HARMONY_THRESHOLD && ch) {
            true  => println!("OilGas: CONTROL GO"),
            false => { println!("OilGas: CONTROL HALT – hold choke"); hold_choke().await; }
        }
        tokio::time::sleep(Duration::from_millis(200)).await; // 5 Hz
    }
}
