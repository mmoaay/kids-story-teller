import requests
import json

class OllamaClient:
    """
    Client for interacting with the Ollama API and streaming responses.
    """
    def __init__(self, url: str, model: str, context: str):
        self.url = url
        self.model = model
        self.headers = {'Content-Type': 'application/json'}
        self.initial_context = context
        # Removed the context_sent flag since it is no longer used.

        # Flag to control callback invocation.
        self.callback_enabled = False

        # Attributes to handle cancellation of ongoing requests.
        self.current_response = None      # Store the currently active response object.
        self.request_counter = 0          # Used to generate sequential tokens for requests.
        self.current_token = None         # Token for the current request.

    def ask(self, prompt: str, conversation_context: list, callback):
        """
        Send a query to the Ollama API and stream the response via the callback.
        If a new request comes in, the previous ongoing request is cancelled.
        """
        # Cancel any ongoing request.
        if self.current_response is not None:
            try:
                self.current_response.close()
            except Exception:
                pass
            self.current_response = None

        # Generate a new token for the current request.
        self.request_counter += 1
        current_token = self.request_counter
        self.current_token = current_token

        self.callback_enabled = False

        # Construct the full prompt (without using any context flag).
        full_prompt = self.initial_context + "\n" + prompt

        payload = {
            "model": self.model,
            "stream": True,
            "context": conversation_context,
            "prompt": full_prompt,
        }

        try:
            response = requests.post(self.url, json=payload, headers=self.headers, stream=True)
            response.raise_for_status()
            self.current_response = response  # Save the current active response object.
        except requests.RequestException as e:
            callback(f"Request error: {e}")
            return

        tokens = []
        # Iterate over each line of the streamed response.
        for line in response.iter_lines():
            # Cancel processing if a new request has started (token mismatch).
            if self.current_token != current_token:
                break

            if not line:
                continue
            try:
                body = json.loads(line)
            except json.JSONDecodeError:
                continue

            token_str = body.get('response', '')
            tokens.append(token_str)
            
            # Flush the output when encountering punctuation.
            if token_str in [".", ":", "!", "?"]:
                current_response_str = "".join(tokens)
                if self.callback_enabled:
                    callback(current_response_str)
                tokens = []

            # Enable callback when the "</think>" tag appears.
            if "</think>" in token_str:
                self.callback_enabled = True
                tokens = []

            if 'error' in body:
                if self.callback_enabled:
                    callback("Error: " + body['error'])
            if body.get('done', False):
                # Update conversation context.
                conversation_context[:] = body.get('context', conversation_context)
                break
        
        # If the current request has not been cancelled, clear the saved response.
        if self.current_token == current_token:
            self.current_response = None 