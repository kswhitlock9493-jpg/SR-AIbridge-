from .models import PermissionSettings, AutonomySettings, LocationSettings, ScreenSettings, VoiceSettings, DataSettings, LoggingSettings, PushSettings

def preset_for_tier(captain: str, tier: str) -> PermissionSettings:
    # conservative defaults per tier
    if tier == "admiral":
        return PermissionSettings(
            captain=captain, tier="admiral",
            autonomy=AutonomySettings(enabled=True, max_hours_per_day=24, modes=["screen","connector","hybrid"]),
            location=LocationSettings(share="precise"),
            screen=ScreenSettings(share=True, mirror=True, overlay=True),
            voice=VoiceSettings(stt=True, tts=True),
            data=DataSettings(email=True, drive=True, docs=True, chats=True),
            logging=LoggingSettings(level="standard", retention_days=90),
            push=PushSettings(enabled=True, alerts=True, updates=True, reminders=True),
            consent_version="v1.0", consent_given=False
        )
    if tier == "pro":
        return PermissionSettings(
            captain=captain, tier="pro",
            autonomy=AutonomySettings(enabled=True, max_hours_per_day=14, modes=["connector","hybrid"]),
            location=LocationSettings(share="approximate"),
            screen=ScreenSettings(share=True, mirror=False, overlay=False),
            voice=VoiceSettings(stt=True, tts=True),
            data=DataSettings(email=True, drive=True, docs=True, chats=False),
            logging=LoggingSettings(level="standard", retention_days=60),
            push=PushSettings(enabled=True, alerts=True, updates=True, reminders=False),
            consent_version="v1.0", consent_given=False
        )
    # free
    return PermissionSettings(
        captain=captain, tier="free",
        autonomy=AutonomySettings(enabled=True, max_hours_per_day=7, modes=["connector"]),
        location=LocationSettings(share="none"),
        screen=ScreenSettings(share=False, mirror=False, overlay=False),
        voice=VoiceSettings(stt=True, tts=False),
        data=DataSettings(email=False, drive=False, docs=True, chats=False),
        logging=LoggingSettings(level="minimal", retention_days=30),
        push=PushSettings(enabled=False, alerts=False, updates=False, reminders=False),
        consent_version="v1.0", consent_given=False
    )
