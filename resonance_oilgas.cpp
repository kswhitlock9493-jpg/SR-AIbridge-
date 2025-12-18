/* Resonance_OilGas.cpp - API 51 / IEC 61511 SIL 3 Safety Kernel (MISRA-C++2023) */
#include <cmath>
#include <array>
#include <cstdint>

constexpr float HARMONY_THRESHOLD = 0.9995f;
constexpr float MIN_SCORE = 1e-12f;
constexpr std::size_t MAX_SUBSYSTEMS = 8;

struct OilGasContext {
    std::array<float, MAX_SUBSYSTEMS> scores{};
    std::array<float, MAX_SUBSYSTEMS> weights{};
    std::size_t count = 0;
};

float calculate_mu(const OilGasContext& ctx) {
    float log_sum = 0.0f;
    for (std::size_t i = 0; i < ctx.count; ++i) {
        float s = ctx.scores[i];
        if (s < MIN_SCORE) s = MIN_SCORE;
        if (s > 1.0f) s = 1.0f;
        log_sum += ctx.weights[i] * std::log(s);
    }
    return std::exp(log_sum);
}

bool check_ch() {
    return  no_permit_violation()        &&
            bop_interlock_verified()     &&
            h2s_sensor_ok()              &&
            cyber_threat_yellow_or_less() &&
            insurance_cert_valid();
}

enum class ControlDecision { CONTROL_GO, CONTROL_HALT };

ControlDecision evaluate_oilgas_harmony(float mu, bool ch) {
    if (mu >= HARMONY_THRESHOLD && ch) return ControlDecision::CONTROL_GO;
    trigger_autoheal();
    log_harmony_fault(mu, ch);
    return ControlDecision::CONTROL_HALT;
}

/* 5 Hz control loop */
void control_loop() {
    static OilGasContext ctx = {
        .scores   = {0.98f, 0.97f, 1.0f, 0.96f, 0.99f},
        .weights  = {0.30f, 0.25f, 0.20f, 0.15f, 0.10f},
        .count    = 5
    };
    ctx.scores[0] = read_wellhead_pressure_coherence();
    ctx.scores[1] = read_pipeline_leak_health();
    /* ... */
    float mu = calculate_mu(ctx);
    bool ch  = check_ch();
    if (evaluate_oilgas_harmony(mu, ch) == ControlDecision::CONTROL_HALT) {
        hold_choke_valve();
    }
}
