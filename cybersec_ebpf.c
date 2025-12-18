/* cybersec_ebpf.c - eBPF probe for real-time cyber metrics (CO-RE) */
#include <linux/bpf.h>
#include <linux/pkt_cls.h>
#include <bpf/bpf_helpers.h>
#include <bpf/bpf_core_read.h>

char _license[] SEC("license") = "GPL";

#define HARMONY_THRESHOLD 0.9995f
#define MIN_SCORE         1e-12f

struct {
	__uint(type, BPF_MAP_TYPE_ARRAY);
	__type(key, __u32);
	__type(value, float);
	__uint(max_entries, 5);
} cyber_map SEC(".maps");

static inline float calculate_mu(float *scores, float *weights, int n) {
	float log_sum = 0.0f;
	for (int i = 0; i < n; i++) {
		float s = scores[i];
		if (s < MIN_SCORE) s = MIN_SCORE;
		if (s > 1.0f) s = 1.0f;
		log_sum += weights[i] * logf(s);
	}
	return expf(log_sum);
}

SEC("kprobe/__x64_sys_write")
int trace_write(struct pt_regs *ctx) {
	float scores[5] = {0};
	float weights[5] = {0.30f, 0.25f, 0.20f, 0.15f, 0.10f};
	for (int i = 0; i < 5; i++) {
		scores[i] = *(__u32 *)bpf_map_lookup_elem(&cyber_map, &i);
	}
	float mu = calculate_mu(scores, weights, 5);
	if (mu < HARMONY_THRESHOLD) {
		bpf_printk("CyberSec: CHANGE_HALT mu=%.4f\n", mu);
	}
	return 0;
}
