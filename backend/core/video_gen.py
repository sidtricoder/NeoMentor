import json
import subprocess
import time
import base64
import os
import requests
import logging
from typing import Optional, Dict, Any
from pathlib import Path
from google.auth import default
from google.auth.transport.requests import Request

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class GoogleVeo2VideoGenerator:
    def __init__(self, project_id: str = "eternal-argon-460400-i0", location_id: str = "us-central1"):
        self.project_id = project_id
        self.location_id = location_id
        self.api_endpoint = f"{location_id}-aiplatform.googleapis.com"
        self.model_id = "veo-2.0-generate-001"
        # Don't set a default image path - require it to be provided
        self.default_image_path = None
        
    def get_access_token(self) -> str:
        """Get Google Cloud access token using Application Default Credentials"""
        try:
            # Use Application Default Credentials
            credentials, project = default(scopes=["https://www.googleapis.com/auth/cloud-platform"])
            credentials.refresh(Request())
            return credentials.token
        except Exception as e:
            logger.error(f"Failed to get access token: {e}")
            raise
    
    def encode_image_to_base64(self, image_path: Path) -> tuple[str, str]:
        """Encode image to base64 string and return with MIME type"""
        if not image_path.exists():
            raise FileNotFoundError(f"Image file not found: {image_path}")
        
        # Determine MIME type based on file extension
        extension = image_path.suffix.lower()
        mime_type_map = {
            '.jpg': 'image/jpeg',
            '.jpeg': 'image/jpeg',
            '.png': 'image/png',
            '.gif': 'image/gif',
            '.bmp': 'image/bmp',
            '.webp': 'image/webp'
        }
        
        mime_type = mime_type_map.get(extension, 'image/jpeg')
        
        with open(image_path, "rb") as image_file:
            encoded_string = base64.b64encode(image_file.read()).decode('utf-8')
        
        return encoded_string, mime_type
    
    def create_video_request(self, prompt: str, image_path: Optional[Path] = None, duration_seconds: int = 5) -> Dict[str, Any]:
        """Create the video generation request payload"""
        request_data = {
            "endpoint": f"projects/{self.project_id}/locations/{self.location_id}/publishers/google/models/{self.model_id}",
            "instances": [
                {
                    "prompt": prompt,
                }
            ],
            "parameters": {
                "aspectRatio": "16:9",
                "sampleCount": 1,
                "durationSeconds": str(duration_seconds),
                "personGeneration": "allow_all",
                "enablePromptRewriting": True,
                "addWatermark": True,
                "includeRaiReason": True,
            }
        }
        
        # Add image if provided
        if image_path and image_path.exists():
            try:
                encoded_image, mime_type = self.encode_image_to_base64(image_path)
                request_data["instances"][0]["image"] = {
                    "bytesBase64Encoded": encoded_image,
                    "mimeType": mime_type
                }
                logger.info(f"Added image to request: {image_path} (MIME: {mime_type})")
            except Exception as e:
                logger.warning(f"Failed to encode image {image_path}: {e}")
        
        return request_data
    
    def create_video_request_with_image_data(self, prompt: str, image_data: bytes = None, image_mime_type: str = None, duration_seconds: int = 5) -> Dict[str, Any]:
        """Create video generation request payload with binary image data from artifacts"""
        request_data = {
            "endpoint": f"projects/{self.project_id}/locations/{self.location_id}/publishers/google/models/{self.model_id}",
            "instances": [
                {
                    "prompt": prompt,
                }
            ],
            "parameters": {
                "aspectRatio": "16:9",
                "sampleCount": 1,
                "durationSeconds": str(duration_seconds),
                "personGeneration": "allow_all",
                "enablePromptRewriting": True,
                "addWatermark": True,
                "includeRaiReason": True,
            }
        }
        
        # Add image data if provided
        if image_data and image_mime_type:
            try:
                encoded_image = base64.b64encode(image_data).decode('utf-8')
                request_data["instances"][0]["image"] = {
                    "bytesBase64Encoded": encoded_image,
                    "mimeType": image_mime_type
                }
                logger.info(f"Added image data to request (MIME: {image_mime_type}, Size: {len(image_data)} bytes)")
            except Exception as e:
                logger.warning(f"Failed to encode image data: {e}")
        
        return request_data

    def submit_video_request(self, request_data: Dict[str, Any]) -> str:
        """Submit video generation request and return operation ID"""
        url = f"https://{self.api_endpoint}/v1/projects/{self.project_id}/locations/{self.location_id}/publishers/google/models/{self.model_id}:predictLongRunning"
        
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.get_access_token()}"
        }
        
        logger.info("Submitting video generation request...")
        response = requests.post(url, headers=headers, json=request_data)
        
        if response.status_code != 200:
            logger.error(f"Request failed with status {response.status_code}: {response.text}")
            raise Exception(f"Video generation request failed: {response.text}")
        
        response_data = response.json()
        operation_name = response_data.get("name", "")
        
        if not operation_name:
            raise Exception("No operation name returned from API")
        
        logger.info(f"Video generation started. Operation ID: {operation_name}")
        return operation_name
    
    def check_operation_status(self, operation_name: str) -> Dict[str, Any]:
        """Check the status of a video generation operation"""
        url = f"https://{self.api_endpoint}/v1/projects/{self.project_id}/locations/{self.location_id}/publishers/google/models/{self.model_id}:fetchPredictOperation"
        
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.get_access_token()}"
        }
        
        fetch_data = {"operationName": operation_name}
        
        response = requests.post(url, headers=headers, json=fetch_data)
        
        if response.status_code != 200:
            logger.error(f"Status check failed with status {response.status_code}: {response.text}")
            raise Exception(f"Status check failed: {response.text}")
        
        return response.json()
    
    def wait_for_completion(self, operation_name: str, max_wait_time: int = 600, check_interval: int = 30) -> Dict[str, Any]:
        """Wait for video generation to complete"""
        start_time = time.time()
        
        while time.time() - start_time < max_wait_time:
            logger.info("Checking operation status...")
            status_response = self.check_operation_status(operation_name)
            
            if status_response.get("done", False):
                logger.info("Video generation completed!")
                return status_response
            
            status = status_response.get("metadata", {}).get("genericMetadata", {}).get("state", "UNKNOWN")
            logger.info(f"Current status: {status}")
            
            if status == "FAILED":
                error_msg = status_response.get("error", {}).get("message", "Unknown error")
                raise Exception(f"Video generation failed: {error_msg}")
            
            logger.info(f"Waiting {check_interval} seconds before next check...")
            time.sleep(check_interval)
        
        raise Exception(f"Video generation timed out after {max_wait_time} seconds")
    
    def save_video(self, video_data: str, output_path: str) -> None:
        """Save base64 encoded video data to file"""
        try:
            video_bytes = base64.b64decode(video_data)
            with open(output_path, "wb") as f:
                f.write(video_bytes)
            logger.info(f"Video saved to: {output_path}")
        except Exception as e:
            logger.error(f"Failed to save video: {e}")
            raise
    
    def save_video_from_json(self, json_path: str, output_path: str) -> None:
        """Save video from a debug JSON file containing base64 video data."""
        try:
            with open(json_path, 'r') as f:
                data = json.load(f)
            video_b64 = data['response']['videos'][0]['bytesBase64Encoded']
            video_bytes = base64.b64decode(video_b64)
            with open(output_path, 'wb') as f:
                f.write(video_bytes)
            logger.info(f"Video decoded and saved as {output_path}")
        except Exception as e:
            logger.error(f"Failed to decode and save video from JSON: {e}")
            raise
    
    def generate_video(self, prompt: str, output_filename: str, image_path: str = None, duration_seconds: int = 5) -> str:
        """Main method to generate video with required image path"""
        output_path = os.path.join("generated_media", output_filename)
        
        if not image_path:
            raise ValueError("Image path is required for video generation")
            
        try:
            # Ensure output directory exists
            os.makedirs(os.path.dirname(output_path), exist_ok=True)
            
            # Verify image input
            image_path_obj = Path(image_path)
            if not image_path_obj.exists():
                raise FileNotFoundError(f"Image file not found: {image_path}")
            if image_path_obj.suffix.lower() not in ['.jpg', '.jpeg', '.png', '.gif', '.bmp', '.webp']:
                 raise ValueError(f"Unsupported image format: {image_path_obj.suffix}")

            # Create request with provided image and duration
            request_data = self.create_video_request(prompt, image_path_obj, duration_seconds)
            
            # Submit request
            operation_name = self.submit_video_request(request_data)
            
            # Wait for completion
            result = self.wait_for_completion(operation_name)
            
            # Always save JSON response first
            debug_file = os.path.join("generated_media", "debug_response.json")
            os.makedirs(os.path.dirname(debug_file), exist_ok=True)
            with open(debug_file, 'w') as f:
                json.dump(result, f, indent=2)
            logger.info(f"Response saved to: {debug_file}")
            
            # Use the response file to save video
            self.save_video_from_json(debug_file, output_path)
            
            if os.path.exists(output_path) and output_path.lower().endswith('.mp4'):
                logger.info(f"Successfully generated and saved video to {output_path}")
                return output_path
            else:
                raise Exception(f"Failed to save video to {output_path} or it is not an mp4 file.")
        
        except Exception as e:
            logger.error(f"Video generation failed: {e}")
            raise

    def generate_video_with_image_data(self, prompt: str, image_data: bytes, image_mime_type: str, output_filename: str = None, duration_seconds: int = 5) -> str:
        """
        Generate video using binary image data from artifacts
        
        Args:
            prompt: Text prompt for video generation
            image_data: Binary image data from artifact
            image_mime_type: MIME type of the image
            output_filename: Optional output filename
            
        Returns:
            Path to generated video file
        """
        if not output_filename:
            output_filename = f"generated_video_{int(time.time())}.mp4"
        
        output_path = os.path.join("generated_media", output_filename)
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        
        try:
            # Create request with binary image data and duration
            request_data = self.create_video_request_with_image_data(prompt, image_data, image_mime_type, duration_seconds)
            
            # Submit request
            operation_id = self.submit_video_request(request_data)
            logger.info(f"Video generation started with operation ID: {operation_id}")
            
            # Wait for completion and get result
            result = self.wait_for_completion(operation_id)
            
            # Always save JSON response first
            debug_file = os.path.join("generated_media", f"debug_response_{int(time.time())}.json")
            os.makedirs(os.path.dirname(debug_file), exist_ok=True)
            with open(debug_file, 'w') as f:
                json.dump(result, f, indent=2)
            logger.info(f"Response saved to: {debug_file}")
            
            # Use the response file to save video
            self.save_video_from_json(debug_file, output_path)
            
            if os.path.exists(output_path) and output_path.lower().endswith('.mp4'):
                logger.info(f"Successfully generated video with artifact image data: {output_path}")
                return output_path
            else:
                raise Exception(f"Failed to save video to {output_path}")
                
        except Exception as e:
            logger.error(f"Video generation with image data failed: {e}")
            raise

def main():
    """Main function to generate Albert Einstein video"""
    # Einstein explanation prompt
    prompt = """Albert Einstein, wearing his characteristic disheveled hair and thoughtful expression, 
    sits in his study surrounded by books and papers. He looks directly at the camera with a warm, 
    intelligent gaze and begins to explain the theory of relativity. His eyes light up with passion 
    as he gestures with his hands, speaking with the wisdom and curiosity that made him one of 
    history's greatest scientists. The lighting is soft and scholarly, emphasizing his iconic features."""
    
    # Initialize video generator
    generator = GoogleVeo2VideoGenerator()
    
    try:
        logger.info("Starting Albert Einstein video generation...")
        logger.info(f"Using image: {generator.albert_image_path}")
        logger.info(f"Prompt: {prompt}")
        
        # Generate video with a unique name
        output_filename = f"albert_einstein_video_{int(time.time())}.mp4"
        output_path = generator.generate_video(prompt, output_filename)
        
        logger.info("="*50)
        logger.info("VIDEO GENERATION COMPLETED SUCCESSFULLY!")
        logger.info(f"Output file: {output_path}")
        logger.info(f"Duration: 5 seconds")
        logger.info(f"Resolution: 16:9 aspect ratio")
        logger.info("="*50)
        
        return output_path
        
    except Exception as e:
        logger.error(f"Failed to generate video: {e}")
        return None

if __name__ == "__main__":
    # Check if Google Cloud credentials are available
    try:
        from google.auth import default
        credentials, project = default()
        logger.info("Google Cloud authentication verified.")
    except Exception as e:
        logger.error(f"Google Cloud authentication failed: {e}")
        logger.error("Please ensure your application has proper Google Cloud credentials")
        exit(1)
    
    # Run the main function
    result = main()
    
    if result:
        print(f"\n✅ Video successfully generated: {result}")
    else:
        print("\n❌ Video generation failed. Check logs for details.")
