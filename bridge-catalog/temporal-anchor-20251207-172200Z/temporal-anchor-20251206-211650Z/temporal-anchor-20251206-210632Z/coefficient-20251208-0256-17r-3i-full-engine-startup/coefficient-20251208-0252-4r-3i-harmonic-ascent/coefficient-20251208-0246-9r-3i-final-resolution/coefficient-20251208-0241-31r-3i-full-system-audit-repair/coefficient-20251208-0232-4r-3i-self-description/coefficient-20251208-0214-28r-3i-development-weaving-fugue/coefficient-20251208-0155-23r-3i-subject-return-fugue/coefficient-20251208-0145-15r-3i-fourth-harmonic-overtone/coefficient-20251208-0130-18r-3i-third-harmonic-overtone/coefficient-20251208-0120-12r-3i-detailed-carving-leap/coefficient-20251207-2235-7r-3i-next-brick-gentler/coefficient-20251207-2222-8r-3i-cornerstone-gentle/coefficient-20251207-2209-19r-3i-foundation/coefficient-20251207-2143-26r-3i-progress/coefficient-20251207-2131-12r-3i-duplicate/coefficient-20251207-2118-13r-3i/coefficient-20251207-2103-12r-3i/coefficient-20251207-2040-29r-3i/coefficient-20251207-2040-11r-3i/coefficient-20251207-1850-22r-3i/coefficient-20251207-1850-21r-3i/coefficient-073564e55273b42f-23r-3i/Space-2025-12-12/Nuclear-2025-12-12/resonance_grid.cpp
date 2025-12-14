/* Resonance_Grid.cpp - IEC 61850 / NERC CIP Safety Kernel */
#include <cmath>
#include <array>
#include <cstdint>

constexpr float HARMONY_THRESHOLD = 0.9995f;
constexpr float MIN_SCORE         = 1e-12f;
constexpr std::size_t MAX_SUBSYSTEMS = 16;

struct GridContext {
    std::array<float, MAX_SUBSYSTEMS> scores{};
    std::array<float, MAX_SUBSYSTEMS> weights{};
    std::size_t count = 0;
};

float calculate_mu(const GridContext& ctx){
    float log_sum = 0.0f;
    for(std::size_t i = 0; i < ctx.count; ++i){
        float s = ctx.scores[i];
        if(s < MIN_SCORE) s = MIN_SCORE;
        if(s > 1.0f)      s = 1.0f;
        log_sum += ctx.weights[i] * std::log(s);
    }
    return std::exp(log_sum);
}

bool check_ch(){
    return cyber_alarm_clear()      &&
           phase_angle_within_5deg() &&
           freq_within_50mhz()       &&
           breaker_interlock_ok()    &&
           operator_override_off();
}

enum class SwitchDecision { SWITCH_GO, SWITCH_HALT };

SwitchDecision evaluate_grid_harmony(float mu, bool ch){
    if(mu >= HARMONY_THRESHOLD && ch) return SwitchDecision::SWITCH_GO;
    trigger_autoheal();
    log_harmony_fault(mu, ch);
    return SwitchDecision::SWITCH_HALT;
}

/* 50 Hz control loop */
void control_loop(){
    static GridContext ctx = {
        .scores  = {0.98f, 0.97f, 1.0f, 0.96f, 0.99f},
        .weights = {0.30f, 0.25f, 0.20f, 0.15f, 0.10f},
        .count   = 5
    };
    ctx.scores[0] = read_gen_frequency_coherence();
    ctx.scores[1] = read_phase_angle_stability();
    /* ... */
    float mu = calculate_mu(ctx);
    bool  ch = check_ch();
    if(evaluate_grid_harmony(mu, ch) == SwitchDecision::SWITCH_HALT){
        hold_breaker_open();
    }
}
