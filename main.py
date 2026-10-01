config = {}

from functools import reduce
import json
import string
from types import SimpleNamespace
import yaml

from flask import Flask, jsonify, request

from func.utils import format_all_str_with_args, format_str_with_args
from senders.discord import Discord, DiscordConfig
from senders.telegram import Telegram, TelegramConfig


with open("config.yaml") as stream:
	try:
		config = yaml.safe_load(stream)
	except yaml.YAMLError as exc:
		print(exc)

app = Flask(__name__)

if len(config["routes"]) > 0:
	for route_name in config["routes"]:
		route = config["routes"][route_name]

		def handler(route_name=route_name):
			data = request.get_json()
			json_values = []
			route = config["routes"][route_name]

			for match_value in route.get("match_case", []):
				keys_values = config.get("routes", {}).get(route_name, {}).get("match_case", {}).get(match_value, {}).get("triggers", [])
				conditionAcceptList = []
				for key_value in keys_values:
					key = key_value.get("key", "")
					value = reduce(lambda x, k: x.get(k, {}) if isinstance(x, dict) else {}, key.split("."), data)
					espected_value = key_value.get("value", "")
					conditionAcceptList.append(value == espected_value)
				condition = False
				match config.get("routes", {}).get(route_name, {}).get("match_case", {}).get(match_value, {}).get("triggers_type", "or"):
					case "and":
						condition = conditionAcceptList.count(True) == len(conditionAcceptList)
					case "or":
						condition = True in conditionAcceptList
					case _:
						condition = True in conditionAcceptList

				if condition:
					route = config["routes"][route_name]
					message: str = (route.get("match_case", []).get(match_value, {}) or {}).get("message", None)
					discord_json_config = (route.get("match_case", []).get(match_value, {}) or {}).get("discord_config", {})

					msg_replaces = format_str_with_args(msg_replaces=message, data=data)
					discord_json_config = format_all_str_with_args(json_config=discord_json_config, data=data)

					senders = route.get("senders", {})
					if msg_replaces != "" and senders != {}:
						sends_result = []
						for sender in senders:
							match sender:
								case "telegram":
									telegram = Telegram(
										url=f"https://api.telegram.org/bot{senders.get(sender, {}).get('bot','')}/sendMessage",
										config=TelegramConfig(
											chat_id=senders.get(sender, {}).get('channel_clean_id',''),
											chat_full_id=senders.get(sender, {}).get('channel_full_id',''),
											parse_mode=senders.get(sender, {}).get('parse_mode','MarkdownV2')
										)
									)
									sends_result.append(telegram.send(message=msg_replaces, data=data))
								case "discord":
									discord = Discord(
										url=senders.get(sender, {}).get('url', ''),
										config=DiscordConfig(
											username=senders.get(sender, {}).get('username', None),
											avatar_url=senders.get(sender, {}).get('avatar_url', None)
										)
									)
									discord_json_config["content"] = msg_replaces
									sends_result.append(discord.send(json_config=discord_json_config, data=data))
								case _:
									pass
						if len(sends_result) > 0:
							return jsonify(response=f"{len(sends_result)} message{'s' if len(sends_result) > 1 else ''} has been send correctly")
			return jsonify(route_name=route_name, val=json_values)

		app.add_url_rule(
			route['endpoint'],
			endpoint=f"post_{route_name}",
			view_func=handler,
			methods=["POST"]
		)

if __name__ == "__main__":
	app.run(host=config.get("host", "0.0.0.0"), port=config.get("port", 5555))
