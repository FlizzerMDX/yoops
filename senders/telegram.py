import json

import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

class TelegramConfig:
	def __init__(self, chat_id, chat_full_id, parse_mode="HTML"):
		self.chat_id = chat_id
		self.chat_full_id = chat_full_id
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

	def send(self, message, data):
		responses = []
		if self.config.chat_id:
			responses.append(self.send_message(message=message))
		if self.config.chat_full_id:
			responses.append(self.send_full_data(data=data))
		return responses

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
				"chat_id": self.config.chat_full_id,
				"text": f"<pre><code class='language-json'>{json.dumps(data, indent=2)}</code></pre>",
				"parse_mode": "HTML"
			},
			timeout=(3, 10)
		)
		return response
