import os
import tempfile
import pygame
import torch
from diffusers import StableDiffusionPipeline

class GenerationCancelledException(Exception):
    """Exception to indicate that generation was cancelled due to a new request."""
    pass

class StableDiffusionImageGenerator:
    """
    A class that generates images based on text prompts using a locally installed Stable Diffusion model.
    
    Optimizations for Mac M2:
      - Uses the "mps" device if available.
      - Generates lower resolution images (256 x 256) for faster inference.
      - Runs fewer inference steps (20 steps) for quick image generation.
    """
    def __init__(self, modelName="CompVis/stable-diffusion-v1-4", device=None):
        """
        :param modelName: Name of the pretrained Stable Diffusion model.
        :param device: Device to run the model on ("mps", "cuda", or "cpu"). If None,
                       the class automatically selects "mps" if available on Mac M2.
        """
        if device is None:
            if torch.backends.mps.is_available():
                device = "mps"
            else:
                device = "cpu"
        self.device = device
        
        # Load the pipeline with half precision for non-CPU devices.
        self.pipe = StableDiffusionPipeline.from_pretrained(
            modelName,
            revision="fp16" if device != "cpu" else None,
            torch_dtype=torch.float16 if device != "cpu" else torch.float32,
            low_cpu_mem_usage=True
        )
        
        # Attributes for handling cancellation of ongoing requests.
        self.request_counter = 0   # Generates sequential tokens per request.
        self.current_token = None  # Token for the currently active request.

    def _cancellation_callback(self, step, timestep, latents, token):
        """
        Callback invoked during image generation to check for cancellation.
        Raises a custom exception if a new request has overridden the current one.
        
        :param step: Current step of the diffusion process.
        :param timestep: Current timestep.
        :param latents: Current latent tensor.
        :param token: Token assigned to the current request.
        """
        if self.current_token != token:
            raise GenerationCancelledException("Generation cancelled due to new request")
            
    def generate_image(self, prompt: str):
        """
        Generate an image based on the given prompt.
        
        Optimizations: 
         - Lower resolution (256 x 256) speeds up the image generation.
         - Reduced number of inference steps (20).
         - Employs a cancellation mechanism: if a new request starts,
           the previous one will be stopped.
         
        :param prompt: The text prompt.
        :return: A pygame.Surface containing the generated image, or None if canceled or an error occurs.
        """
        # Generate a new token for the current request.
        self.request_counter += 1
        current_token = self.request_counter
        self.current_token = current_token
        
        try:
            # Generate a low-resolution image with a cancellation callback.
            generated = self.pipe(
                prompt,
                num_inference_steps=20,
                height=256,
                width=256,
                callback=lambda step, timestep, latents: self._cancellation_callback(step, timestep, latents, current_token),
                callback_steps=1
            )
        except GenerationCancelledException:
            print("Image generation cancelled due to a new request.")
            return None
        except Exception as ex:
            # If an exception occurs and either the token has changed or it's an IndexError, assume cancellation.
            if self.current_token != current_token or isinstance(ex, IndexError):
                print("Image generation cancelled due to a new request.")
                return None
            print("Error generating image with Stable Diffusion:", ex)
            return None 

        # Verify that no new request has overridden this one.
        if self.current_token != current_token:
            return None
        
        image = generated.images[0]
        # Save the image to a temporary file so that it can be loaded via pygame.
        try:
            with tempfile.NamedTemporaryFile(suffix=".png", delete=False) as tmp_file:
                tmp_filename = tmp_file.name
                image.save(tmp_filename)
            # Load the image as a pygame surface.
            pygame_image = pygame.image.load(tmp_filename)
        finally:
            os.unlink(tmp_filename)  # Remove the temporary file.
        return pygame_image 