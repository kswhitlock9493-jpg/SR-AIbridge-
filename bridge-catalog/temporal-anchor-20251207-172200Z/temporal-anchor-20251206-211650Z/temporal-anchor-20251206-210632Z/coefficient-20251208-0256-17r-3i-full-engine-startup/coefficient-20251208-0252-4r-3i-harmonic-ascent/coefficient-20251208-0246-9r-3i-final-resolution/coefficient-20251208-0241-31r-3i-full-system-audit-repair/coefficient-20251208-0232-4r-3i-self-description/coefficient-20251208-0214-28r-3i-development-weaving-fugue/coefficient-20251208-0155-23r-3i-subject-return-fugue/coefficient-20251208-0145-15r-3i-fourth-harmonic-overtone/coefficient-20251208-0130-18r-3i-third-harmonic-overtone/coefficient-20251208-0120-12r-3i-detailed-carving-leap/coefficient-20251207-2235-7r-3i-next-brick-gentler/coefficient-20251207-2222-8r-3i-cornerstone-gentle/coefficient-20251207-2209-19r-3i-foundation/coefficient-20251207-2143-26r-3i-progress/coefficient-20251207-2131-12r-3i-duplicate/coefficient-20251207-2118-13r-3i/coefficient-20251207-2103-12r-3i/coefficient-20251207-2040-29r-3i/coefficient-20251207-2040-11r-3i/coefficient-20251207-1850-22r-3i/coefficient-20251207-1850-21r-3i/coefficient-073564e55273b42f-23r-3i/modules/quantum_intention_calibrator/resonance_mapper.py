import hashlib, math, datetime, json

class ResonanceMapper:
    BASE_FREQ = 1440.0
    PHI       = (1 + 5**0.5)/2
    SIGIL     = "≡"

    def __init__(self):
        self.whitlock_numer = 31
        self.whitlock_denom = 17

    def intention_to_params(self, text: str) -> dict:
        vec = self._semantic_vector(text)
        freq = self._optimal_freq(vec)
        phase = self._phase_align(vec)
        coeff = self._whitlock_coeff(vec)
        return {
            "intention_hash": hashlib.sha256(text.encode()).hexdigest()[:16],
            "frequency":      round(freq, 6),
            "phase":          phase,
            "harmonic":       self._harmonic_name(freq),
            "coefficient":    coeff,
            "sigil":          self.SIGIL,
            "timestamp":      datetime.datetime.utcnow().isoformat() + "Z"
        }

    def _semantic_vector(self, text: str) -> int:
        return sum(ord(c) for c in text.lower() if c.isalnum())

    def _optimal_freq(self, vec: int) -> float:
        return self.BASE_FREQ + (vec % 1000) / 1000

    def _phase_align(self, vec: int) -> str:
        theta = (vec % 360) * math.pi / 180
        return f"cos({theta:.4f}) + i·sin({theta:.4f})"

    def _harmonic_name(self, freq: float) -> str:
        nth = int(round((freq - self.BASE_FREQ) * 1000))
        return f"{nth}th_overtone"

    def _whitlock_coeff(self, vec: int) -> str:
        n = (vec % self.whitlock_numer) + 1
        d = self.whitlock_denom
        return f"({n} + 3i)/{d}"
