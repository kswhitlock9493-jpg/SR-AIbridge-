/* AgriFood_LoRaWAN_Node.ino - ESG / FDA Traceability Node (Arduino-ESP32) */
#include <lmic.h>
#include <hal/hal.h>
#include <math.h>

#define HARMONY_THRESHOLD 0.9995f
#define MIN_SCORE 1e-12f
#define MAX_SUBSYSTEMS 6

typedef struct {
    float scores[MAX_SUBSYSTEMS];
    float weights[MAX_SUBSYSTEMS];
    uint8_t count;
} AgriContext;

float calculate_mu(const AgriContext *ctx){
    float log_sum = 0.0f;
    for(uint8_t i = 0; i < ctx->count; ++i){
        float s = ctx->scores[i];
        if(s < MIN_SCORE) s = MIN_SCORE;
        if(s > 1.0f)      s = 1.0f;
        log_sum += ctx->weights[i] * logf(s);
    }
    return expf(log_sum);
}

bool check_ch(){
    return (temp_sensor_ok()           &&
            moisture_sensor_ok()      &&
            blockchain_hash_verified()&&
            pesticide_below_tolerance()&&
            carbon_credit_positive()  &&
            organic_cert_valid());
}

typedef enum { SHIPMENT_GO, SHIPMENT_HALT } ShipmentDecision;

ShipmentDecision evaluate_agrifood_harmony(float mu, bool ch){
    if(mu >= HARMONY_THRESHOLD && ch) return SHIPMENT_GO;
    digitalWrite(PIN_ALERT_LED, HIGH);
    return SHIPMENT_HALT;
}

/* 0.2 Hz field loop */
void loop(){
    static AgriContext ctx = {
        .scores  = {0.98f, 0.97f, 1.0f, 0.96f, 0.99f, 0.98f},
        .weights = {0.25f, 0.25f, 0.20f, 0.15f, 0.10f, 0.05f},
        .count   = 6
    };
    ctx.scores[0] = read_soil_moisture_coherence();
    ctx.scores[1] = read_temp_stability();
    /* ... */
    float mu = calculate_mu(&ctx);
    bool  ch = check_ch();
    if(evaluate_agrifood_harmony(mu, ch) == SHIPMENT_HALT){
        hold_conveyor();
    }
    send_lorawan_packet(mu, ch);
    delay(5000); // 0.2 Hz
}
