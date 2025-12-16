//! Ground_Segment_Monitor.rs - NASA-STD Ground Safety Crate (forbid unsafe)
#![forbid(unsafe_code)]
use std::time::{Duration, SystemTime, UNIX_EPOCH};

const HARMONY_THRESHOLD: f64 = 0.9995;
const MIN_SCORE: f64 = 1e-12;

pub struct GroundContext {
    pub scores: Vec<f64>,
    pub weights: Vec<f64>,
}

impl GroundContext {
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
    weather_within_limits() &&
    crew_surgeon_ok()      &&
    no_hold_countdown()
}

#[tokio::main]
async fn main() {
    let ctx = GroundContext {
        scores: vec![0.98, 0.97, 1.0, 0.96, 0.99],
        weights: vec![0.30, 0.25, 0.20, 0.15, 0.10],
    };
    loop {
        let scores = vec![
            query_telemetry_link_health().await,
            query_range_safety_status().await,
            query_weather().await,
            query_crew_surgeon().await,
            query_hold_countdown().await,
        ];
        let mu = ctx.calculate_mu();
        let ch = check_ch().await;
        match (mu >= HARMONY_THRESHOLD && ch) {
            true  => println!("Space: FLIGHT GO"),
            false => println!("Space: FLIGHT HALT – hold countdown"),
        }
        tokio::time::sleep(Duration::from_secs(1)).await;
    }
}
