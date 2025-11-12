import os
from anthropic import Anthropic

api_key = os.environ.get("ANTHROPIC_API_KEY")
if not api_key:
    raise SystemExit("ANTHROPIC_API_KEY non défini.")

client = Anthropic(api_key=api_key)
for model in client.models.list():
    print(model.id)