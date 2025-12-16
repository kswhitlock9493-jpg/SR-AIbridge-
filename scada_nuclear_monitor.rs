//! SCADA_Nuclear_Monitor.rs - NRC / IEC 61513 Ground Safety Crate (forbid unsafe)
#![forbid(unsafe_code)]
use std::time::{Duration, SystemTime, UNIX_EPOCH};

const HARMONY_THRESHOLD: f64 = 0.9995;
const MIN_SCORE: f64 = 1e-12;

pub struct NuclearContext {
    pub scores: Vec<f64>,
    pub weights: Vec<f64>,
}

impl NuclearContext {
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
    telemetry_link_alive() &&
    range_safety_clear()   &&
    reactor_pressure_ok()  &&
    operator_alert_ok()    &&
    no_scram_override()
}

#[tokio::main]
async fn main() {
    let ctx = NuclearContext {
        scores: vec![0.98, 0.97, 1.0, 0.96, 0.99],
        weights: vec![0.30, 0.25, 0.20, 0.15, 0.10],
    };
    loop {
        let scores = vec![
            query_neutron_flux_coherence().await,
            query_primary_coolant_health().await,
            query_containment_pressure().await,
            query_cyber_i_c_health().await,
            query_operator_alertness().await,
        ];
        let mu = ctx.calculate_mu();
        let ch = check_ch().await;
        match (mu >= HARMONY_THRESHOLD && ch) {
            true  => println!("Nuclear: CONTROL GO"),
            false => println!("Nuclear: CONTROL HALT – hold rod drive"),
        }
        tokio::time::sleep(Duration::from_secs(1)).await;
    }
}
