import json

import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

from func.utils import remove_empty_from_dict

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

	def send(self, json_config: dict, data):
		responses = []
		responses.append(self.send_message(json_config=json_config))
		responses.append(self.send_full_data(data=data))
		return responses

	def send_message(self, json_config: dict):
		with_component = json_config.get("components", {})
		with_args = remove_empty_from_dict({
			"thread_id": json_config.get("thread_id", ""),
			"with_components": "true" if with_component != {} else ""
		})
		response = self.session.post(
			f"{self.url}{'?' + '&'.join([str(key) + '=' + str(value) for key, value in with_args.items()]) if len(with_args) > 0 else ''}",
			json={
				"username": self.config.username,
				"avatar_url": self.config.avatar_url,
				**remove_empty_from_dict(json_config)
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
