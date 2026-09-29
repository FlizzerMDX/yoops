import json

import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

class DiscordConfig:
	def __init__(self, username=None, avatar_url=None):
		self.username = username
		self.avatar_url = avatar_url


class Discord:
	def __init__(self, url: str, config: DiscordConfig) -> None:
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
			json={
				"username": self.config.username,
				"avatar_url": self.config.avatar_url,
				"content": message,
			},
			timeout=(3, 10)
		)
		return response

	def send_full_data(self, data):
		response = self.session.post(
			self.url,
			json={
				"username": self.config.username,
				"avatar_url": self.config.avatar_url,
				"content": f"```json\n{json.dumps(data, indent=2)}\n```",
			},
			timeout=(3, 10)
		)
		return response
