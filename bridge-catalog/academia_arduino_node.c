/* Academia_Arduino_Node.c - OSHA / NIH Lab Safety Node (MISRA-C:2012 subset) */
#include <Arduino.h>
#include <math.h>

#define HARMONY_THRESHOLD 0.9995f
#define MIN_SCORE         1e-12f
#define MAX_SUBSYSTEMS    7

typedef struct {
    float scores[MAX_SUBSYSTEMS];
    float weights[MAX_SUBSYSTEMS];
    uint8_t count;
} LabContext;

float calculate_mu(const LabContext *ctx){
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
    return !digitalRead(PIN_CHEM_OVERDUE)     &&
           analogRead(PIN_HOOD_VELOCITY) > 100 &&
           digitalRead(PIN_BSC_CERT_OK)      &&
           digitalRead(PIN_LASER_INTERLOCK) &&
           digitalRead(PIN_RAD_BADGE_OK)    &&
           digitalRead(PIN_IRB_OK)          &&
           digitalRead(PIN_ESTOP_NOT_PRESSED);
}

typedef enum { LAB_GO, LAB_HALT } LabDecision;

LabDecision evaluate_lab_harmony(float mu, bool ch){
    if(mu >= HARMONY_THRESHOLD && ch) return LAB_GO;
    digitalWrite(PIN_ALARM_LED, HIGH);
    return LAB_HALT;
}

/* 1 Hz lab loop */
void loop(){
    static LabContext ctx = {
        .scores  = {0.98f, 0.97f, 1.0f, 0.96f, 0.99f, 0.98f, 1.0f},
        .weights = {0.25f, 0.20f, 0.20f, 0.15f, 0.10f, 0.10f, 0.05f},
        .count   = 7
    };
    ctx.scores[0] = read_chemical_inventory_accuracy();
    ctx.scores[1] = read_fume_hood_velocity();
    /* ... */
    float mu = calculate_mu(&ctx);
    bool  ch = check_ch();
    if(evaluate_lab_harmony(mu, ch) == LAB_HALT){
        hold_experiment();
    }
    delay(1000); // 1 Hz
}
