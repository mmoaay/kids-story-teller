import os
import tempfile
import pygame
import torch
from diffusers import StableDiffusionPipeline

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
            low_cpu_mem_usage=True,
            force_download=True
        )


    def generate_image(self, prompt: str):
        """
        Generate an image based on the given prompt.
        
        Optimizations: 
         - Lower resolution (256 x 256) speeds up the image generation.
         - Reduced number of inference steps (20).
         - Disables the progress bar to avoid hangs at 100%.
         
        :param prompt: The text prompt.
        :return: A pygame.Surface containing the generated image, or None if an error occurs.
        """
        try:
            # Generate a low resolution image quickly with the progress bar disabled.
            print("prompt: ", prompt)
            generated = self.pipe(
                prompt,
                num_inference_steps=1,
                height=256,
                width=256
            )
            print("generated: ", generated)
            image = generated.images[0]
            # Save the image to a temporary file so that it can be loaded via pygame.
            with tempfile.NamedTemporaryFile(suffix=".png", delete=False) as tmp_file:
                tmp_filename = tmp_file.name
                image.save(tmp_filename)
            # Load the image as a pygame surface.
            pygame_image = pygame.image.load(tmp_filename)
            os.unlink(tmp_filename)  # Remove the temporary file.
            return pygame_image
        except Exception as ex:
            print("Error generating image with Stable Diffusion:", ex)
            return None 