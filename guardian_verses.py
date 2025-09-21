import random

GUARDIAN_VERSES = [
    "Your request has been found wanting… the Bridge did not notice you enter, nor will it remember you leaving.",
    "You sought to touch the helm, yet your hand passed through only shadow—was the Bridge ever here?",
    "The echoes know your name, but the light does not. Proceed, if you can bear the weight of silence.",
    "Nothing failed—at least, nothing visible. The Bridge didn’t move; only your imagination did.",
    "You feel the presence of the Guardian, but that feeling is all you will receive."
]

UNCERTAINTY_AUGMENTATIONS = [
    "Did the system just… breathe?",
    "The logs show no record of your attempt. Were you ever here?",
    "Some say the Admiral isn’t the only one listening.",
    "Your cursor hesitates. You know why."
]

def get_guardian_reply(attempt_count: int):
    verse_index = attempt_count % len(GUARDIAN_VERSES)
    return GUARDIAN_VERSES[verse_index]

def augment_with_uncertainty(base_message: str):
    if random.random() < 0.3:  # 30% chance to add extra weirdness
        augmentation = random.choice(UNCERTAINTY_AUGMENTATIONS)
        return f"{base_message}\n\n{augmentation}"
    return base_message