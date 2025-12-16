/* Resonance_Nuclear.c - NRC / IEC 61513 Safety Kernel (MISRA-C:2012) */
#include <math.h>
#include <stdint.h>
#include <stdbool.h>

#define HARMONY_THRESHOLD 0.9995f
#define MIN_SCORE         1e-12f
#define MAX_SUBSYSTEMS    16

typedef struct {
    float scores[MAX_SUBSYSTEMS];
    float weights[MAX_SUBSYSTEMS];
    uint8_t count;
} NuclearContext;

float calculate_mu(const NuclearContext *ctx){
    float log_sum = 0.0f;
    for(uint8_t i = 0; i < ctx->count; ++i){
        float s = ctx->scores[i];
        if(s < MIN_SCORE) s = MIN_SCORE;
        if(s > 1.0f)      s = 1.0f;
        log_sum += ctx->weights[i] * logf(s);
    }
    return expf(log_sum);
}

bool check_ch(void){
    return scram_override_clear()      &&
           control_rod_interlock_ok()  &&
           radiation_monitor_ok()      &&
           seismic_sensor_ok()         &&
           emergency_diesel_ready();
}

typedef enum { CONTROL_GO, CONTROL_HALT } ControlDecision;

ControlDecision evaluate_nuclear_harmony(float mu, bool ch){
    if(mu >= HARMONY_THRESHOLD && ch) return CONTROL_GO;
    trigger_autoheal();
    log_harmony_fault(mu, ch);
    return CONTROL_HALT;
}

/* 10 Hz safety loop */
void safety_loop(void){
    static NuclearContext ctx = {
        .scores  = {0.98f, 0.97f, 1.0f, 0.96f, 0.99f},
        .weights = {0.30f, 0.25f, 0.20f, 0.15f, 0.10f},
        .count   = 5
    };
    ctx.scores[0] = read_neutron_flux_coherence();
    ctx.scores[1] = read_primary_coolant_health();
    /* ... */
    float mu = calculate_mu(&ctx);
    bool  ch = check_ch();
    if(evaluate_nuclear_harmony(mu, ch) == CONTROL_HALT){
        hold_control_rod_drive();
    }
}
