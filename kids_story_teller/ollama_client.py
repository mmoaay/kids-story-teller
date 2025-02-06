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
        self.context_sent = False
        # New member variable to control callback invocation.
        self.callback_enabled = False

    def ask(self, prompt: str, conversation_context: list, callback):
        """
        Send a query to the Ollama API and stream the response via the callback.
        """
        callback_enabled = False

        if not self.context_sent:
            full_prompt = self.initial_context + "\n" + prompt
            self.context_sent = True
        else:
            full_prompt = prompt

        payload = {
            "model": self.model,
            "stream": True,
            "context": conversation_context,
            "prompt": full_prompt,
        }

        try:
            response = requests.post(self.url, json=payload, headers=self.headers, stream=True)
            response.raise_for_status()
        except requests.RequestException as e:
            callback(f"Request error: {e}")
            return

        tokens = []
        # Process the streamed response line by line.
        for line in response.iter_lines():
            if not line:
                continue
            try:
                body = json.loads(line)
            except json.JSONDecodeError:
                continue
            token = body.get('response', '')
            tokens.append(token)
            # Flush output when punctuation is encountered.
            if token in [".", ":", "!", "?"]:
                current_response = "".join(tokens)
                if self.callback_enabled:
                    callback(current_response)
                tokens = []

            # Check if the current line contains the "</think>" tag.
            if "</think>" in token:
                self.callback_enabled = True
                tokens = []

            if 'error' in body:
                if self.callback_enabled:
                    callback("Error: " + body['error'])
            if body.get('done', False):
                # Update the conversation context with the API response.
                conversation_context[:] = body.get('context', conversation_context)
                break 