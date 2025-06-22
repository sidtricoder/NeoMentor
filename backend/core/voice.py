import os
import time
from pathlib import Path
import logging
import tempfile

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Try to import gradio_client for F5-TTS
try:
    from gradio_client import Client, handle_file
    GRADIO_CLIENT_AVAILABLE = True
    logger.info("Gradio client imported successfully")
except ImportError as e:
    logger.warning(f"Gradio client not available: {e}")
    GRADIO_CLIENT_AVAILABLE = False

# Try to import soundfile for audio processing
try:
    import soundfile as sf
    SOUNDFILE_AVAILABLE = True
    logger.info("SoundFile imported successfully")
except ImportError as e:
    logger.warning(f"SoundFile not available: {e}")
    SOUNDFILE_AVAILABLE = False

class F5TTSVoiceCloner:
    """
    Voice cloning service using F5-TTS via Hugging Face Space API
    """
    
    def __init__(self):
        if GRADIO_CLIENT_AVAILABLE:
            try:
                # Using mrfakename/E2-F5-TTS
                self.client = Client("mrfakename/E2-F5-TTS")
                self.client_available = True
                logger.info("F5-TTS client (mrfakename/E2-F5-TTS) initialized successfully")
            except Exception as e:
                logger.error(f"Failed to initialize F5-TTS client: {e}")
                self.client_available = False
        else:
            self.client_available = False
            
        self.output_dir = Path("generated_media")  # Save all media here
        self.output_dir.mkdir(exist_ok=True)
        
    def clone_voice(self, 
                   ref_audio_path: str,
                   target_text: str,
                   ref_text: str = None, 
                   output_filename: str = None,
                   remove_silence: bool = False,
                   randomize_seed: bool = True,
                   seed: int = 0,
                   cross_fade_duration: float = 0.15,
                   nfe_steps: int = 32,
                   speed: float = 1.0,
                   save_locally: bool = False,
                   session_logger=None) -> tuple:
        """
        Clone voice using reference audio and generate speech for target text
        
        Args:
            ref_audio_path (str): Path to reference audio file (.wav, .mp3, etc.)
            target_text (str): Text to generate with cloned voice
            ref_text (str): Text that was spoken in the reference audio (optional - can be auto-detected)
            output_filename (str): Custom output filename (optional)
            remove_silence (bool): Whether to remove silences from output
            randomize_seed (bool): Whether to randomize seed for generation
            seed (int): Random seed for reproducible results
            cross_fade_duration (float): Cross-fade duration in seconds
            nfe_steps (int): Number of neural flow estimator steps (quality vs speed)
            speed (float): Speech speed multiplier
            save_locally (bool): Whether to save file locally (default: False)
            
        Returns:
            tuple: (audio_path, spectrogram_info, processed_ref_text, seed_used)
        """
        
        if not self.client_available:
            error_msg = "F5-TTS client not available"
            logger.error(error_msg)
            if session_logger:
                session_logger.error(error_msg)
            raise Exception("Voice cloning service not available")
        
        try:
            # Helper function for logging
            def log_info(message):
                logger.info(message)
                if session_logger:
                    session_logger.info(message)
                    # Force flush for real-time delivery
                    for handler in session_logger.logger.handlers:
                        handler.flush()
            
            def log_error(message):
                logger.error(message)
                if session_logger:
                    session_logger.error(message)
                    # Force flush for real-time delivery
                    for handler in session_logger.logger.handlers:
                        handler.flush()
            
            log_info(f"Starting voice cloning...")
            log_info(f"Reference audio: {ref_audio_path}")
            log_info(f"Reference text: {ref_text}")
            log_info(f"Target text: {target_text}")
            
            # Validate input file
            if not os.path.exists(ref_audio_path):
                raise FileNotFoundError(f"Reference audio file not found: {ref_audio_path}")
            
            # Call the API using mrfakename/E2-F5-TTS format
            result = self.client.predict(
                ref_audio_input=handle_file(ref_audio_path),
                ref_text_input=ref_text or "",  # Use empty string if no ref_text provided
                gen_text_input=target_text,
                remove_silence=remove_silence,
                randomize_seed=randomize_seed,
                seed_input=seed,
                cross_fade_duration_slider=cross_fade_duration,
                nfe_slider=nfe_steps,
                speed_slider=speed,
                api_name="/basic_tts"
            )
            
            # Extract results - handle mrfakename/E2-F5-TTS response format
            try:
                if isinstance(result, tuple) and len(result) >= 4:
                    # Expected format: (audio_out, spectrogram_path, ref_text_out, seed_used)
                    audio_out, spectrogram_info, processed_ref_text, seed_used = result[:4]
                    
                    # audio_out should be (sample_rate, audio_data) tuple
                    if isinstance(audio_out, tuple) and len(audio_out) == 2:
                        sample_rate, audio_data = audio_out
                        # Convert to temporary file path for compatibility
                        if SOUNDFILE_AVAILABLE:
                            with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as tmp_file:
                                sf.write(tmp_file.name, audio_data, sample_rate)
                                audio_path = tmp_file.name
                        else:
                            log_error("SoundFile not available, cannot process audio data")
                            audio_path = None
                    else:
                        audio_path = audio_out  # Fallback if it's already a path
                        
                elif isinstance(result, tuple) and len(result) == 3:
                    audio_out, spectrogram_info, processed_ref_text = result
                    if isinstance(audio_out, tuple) and len(audio_out) == 2:
                        sample_rate, audio_data = audio_out
                        if SOUNDFILE_AVAILABLE:
                            with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as tmp_file:
                                sf.write(tmp_file.name, audio_data, sample_rate)
                                audio_path = tmp_file.name
                        else:
                            log_error("SoundFile not available, cannot process audio data")
                            audio_path = None
                    else:
                        audio_path = audio_out
                    seed_used = seed
                elif isinstance(result, tuple) and len(result) == 2:
                    audio_out, spectrogram_info = result
                    if isinstance(audio_out, tuple) and len(audio_out) == 2:
                        sample_rate, audio_data = audio_out
                        if SOUNDFILE_AVAILABLE:
                            with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as tmp_file:
                                sf.write(tmp_file.name, audio_data, sample_rate)
                                audio_path = tmp_file.name
                        else:
                            log_error("SoundFile not available, cannot process audio data")
                            audio_path = None
                    else:
                        audio_path = audio_out
                    processed_ref_text = ref_text or "Generated text"
                    seed_used = seed
                else:
                    log_error(f"Unexpected API response format: {type(result)} with {len(result) if hasattr(result, '__len__') else 'unknown'} elements")
                    raise ValueError(f"Unexpected API response format: {result}")
            except ValueError as ve:
                if "not enough values to unpack" in str(ve):
                    log_error(f"API response unpacking error. Response: {result}")
                    log_error(f"Response type: {type(result)}, length: {len(result) if hasattr(result, '__len__') else 'unknown'}")
                    # Try to handle as single audio file path
                    if hasattr(result, '__getitem__') and len(result) >= 1:
                        audio_path = result[0] if isinstance(result[0], str) else str(result[0])
                        spectrogram_info = None
                        processed_ref_text = ref_text or "Generated text"
                        seed_used = seed
                    else:
                        raise ve
                else:
                    raise ve
            
            # Save audio to local directory only if explicitly requested
            if save_locally and output_filename and audio_path:
                # Ensure the output directory exists
                local_path = Path(output_filename)
                local_path.parent.mkdir(parents=True, exist_ok=True)
                
                try:
                    if audio_path and os.path.exists(audio_path):
                        import shutil
                        shutil.copy2(audio_path, local_path)
                        log_info(f"Audio saved to: {local_path}")
                        return str(local_path), spectrogram_info, processed_ref_text, seed_used
                    else:
                        log_error(f"Source audio file not found: {audio_path}")
                        return None, None, None, None
                except Exception as copy_error:
                    log_error(f"Failed to copy audio file: {copy_error}")
                    return None, None, None, None
            
            log_info(f"Voice cloning completed successfully!")
            log_info(f"Generated audio: {audio_path}")
            log_info(f"Seed used: {seed_used}")
            
            return audio_path, spectrogram_info, processed_ref_text, seed_used
            
        except Exception as e:
            error_msg = f"Error during voice cloning: {str(e)}"
            log_error(error_msg)
            # Always return 4 values for consistency
            return None, None, None, None
    
    def batch_clone(self, 
                   ref_audio_path: str,
                   text_list: list,
                   ref_text: str = None,
                   save_locally: bool = False,
                   **kwargs) -> list:
        """
        Clone voice for multiple text inputs
        
        Args:
            ref_audio_path (str): Path to reference audio file
            text_list (list): List of texts to generate
            ref_text (str): Text that was spoken in the reference audio (optional)
            save_locally (bool): Whether to save files locally (default: False)
            **kwargs: Additional parameters for clone_voice method
            
        Returns:
            list: List of tuples containing results for each text
        """
        
        results = []
        for i, text in enumerate(text_list):
            logger.info(f"Processing text {i+1}/{len(text_list)}: {text[:50]}...")
            
            # Generate unique filename for each output only if saving locally
            output_filename = f"cloned_voice_{i+1}_{int(time.time())}.wav" if save_locally else None
            
            try:
                result = self.clone_voice(
                    ref_audio_path=ref_audio_path,
                    ref_text=ref_text,
                    target_text=text,
                    output_filename=output_filename,
                    save_locally=save_locally,
                    **kwargs
                )
                results.append((text, result))
                
                # Small delay to avoid overwhelming the API
                time.sleep(1)
                
            except Exception as e:
                logger.error(f"Failed to process text {i+1}: {str(e)}")
                results.append((text, None))
        
        return results
