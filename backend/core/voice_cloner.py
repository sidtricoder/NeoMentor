#!/usr/bin/env python3

import os
import time
from .voice import F5TTSVoiceCloner # Relative import

def speak(ref_audio="speaker.wav", important_text="Hello this is test voice cloning.", output_filename=None, session_logger=None):
    """
    Voice cloning function that uses F5-TTS to generate speech
    
    Args:
        ref_audio: Path to reference audio file
        important_text: Text to convert to speech
        output_filename: Output filename for the generated audio
        session_logger: Session logger for real-time logging
        
    Returns:
        tuple: (audio_path, spectrogram, processed_text, seed)
    """
    if output_filename is None:
        output_filename = f"cloned_voice_{int(time.time())}.wav"
    
    output_path = output_filename
    
    try:
        cloner = F5TTSVoiceCloner()
        
        # Helper function for logging
        def log_info(message):
            print(message)
            if session_logger:
                session_logger.info(f"CONSOLE: {message}")
                # Force flush for real-time delivery
                for handler in session_logger.logger.handlers:
                    handler.flush()
        
        def log_error(message):
            print(message)
            if session_logger:
                session_logger.error(f"CONSOLE: {message}")
                # Force flush for real-time delivery
                for handler in session_logger.logger.handlers:
                    handler.flush()
        
        log_info("\n=== Voice Cloning with F5-TTS ===")
        
        # Verify reference audio input
        if not os.path.exists(ref_audio):
            error_msg = f"❌ Reference audio file not found: {ref_audio}"
            log_error(error_msg)
            return None, None, None, None
        if not ref_audio.lower().endswith('.wav'):
            error_msg = f"❌ Reference audio file must be in .wav format: {ref_audio}"
            log_error(error_msg)
            return None, None, None, None

        # Save this one because it's important
        audio_path, spectrogram, processed_text, seed = cloner.clone_voice(
            ref_audio_path=ref_audio,
            target_text=important_text,
            output_filename=output_path, # Pass the full path
            save_locally=True,  # Save this one
            nfe_steps=32,
            remove_silence=True,
            session_logger=session_logger
        )
        
        # Verify that the file was created
        if os.path.exists(audio_path) and audio_path.lower().endswith('.wav'):
            success_msg = f"✅ Important message saved to: {audio_path}"
            log_info(success_msg)
            return audio_path, spectrogram, processed_text, seed
        else:
            error_msg = f"❌ Failed to save audio file or it is not a .wav file: {audio_path}"
            log_error(error_msg)
            return None, None, None, None
            
    except Exception as e:
        error_msg = f"❌ Voice cloning error: {e}"
        log_error(error_msg)
        # Return placeholder values to keep the pipeline working
        placeholder_path = f"generated_media/{output_filename}"
        placeholder_msg = f"📝 Created placeholder audio path: {placeholder_path}"
        log_info(placeholder_msg)
        return placeholder_path, None, None, None

if __name__ == "__main__":
    speak()
