import json

import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

class TelegramConfig:
	def __init__(self, chat_id, parse_mode="HTML"):
		self.chat_id = chat_id
		self.parse_mode = parse_mode

class Telegram:
	def __init__(self, url: str, config: TelegramConfig) -> None:
		self.url = url
		self.config = config
		self.session = requests.Session()
		retries = Retry(
			total=3,
			backoff_factor=1,
			status_forcelist=[500, 502, 503, 504]
		)
		self.session.mount('https://', HTTPAdapter(max_retries=retries))

	def send_message(self, message):
		response = self.session.post(
			self.url,
			params={
				"chat_id": self.config.chat_id,
				"text": message,
				"parse_mode": self.config.parse_mode
			},
			timeout=(3, 10)
		)
		return response

	def send_full_data(self, data):
		response = self.session.post(
			self.url,
			params={
				"chat_id": self.config.chat_id,
				"text": f"<pre><code class='language-json'>{json.dumps(data, indent=2)}</code></pre>",
				"parse_mode": self.config.parse_mode
			},
			timeout=(3, 10)
		)
		return response
