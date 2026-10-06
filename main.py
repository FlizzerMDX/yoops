config = {}

from functools import reduce
import json
import string
from types import SimpleNamespace
import yaml

from flask import Flask, jsonify, request

from func.logs import write_logs
from func.utils import format_all_str_with_args, format_str_with_args, resolve_condition
from senders.discord import Discord, DiscordConfig
from senders.telegram import Telegram, TelegramConfig


with open("config.yaml") as stream:
	write_logs(type="INF", content="Chargement du fichier de configuration...")
	try:
		write_logs(type="INF", content="Chargement du fichier de configuration terminé avec succès.")
		config = yaml.safe_load(stream)
	except yaml.YAMLError as exc:
		write_logs(type="ERR", content="Erreur lors du chargement du fichier de configuration.")
		print(exc)

app = Flask(__name__)

if len(config["routes"]) > 0:
	for route_name in config["routes"]:
		route = config["routes"][route_name]

		def handler(route_name=route_name):
			data = request.get_json()
			json_values = []
			route = config["routes"][route_name]
			sends_result = []
			for match_value in route.get("match_case", [{}]):
				keys_values = config.get("routes", {}).get(route_name, {}).get("match_case", {}).get(match_value, {}).get("triggers", [])
				condition_accept_list = []
				for key_value in keys_values:
					key = key_value.get("key", "")
					expected_value = key_value.get("value", "")
					received_value = reduce(lambda x, k: x.get(k, {}) if isinstance(x, dict) else {}, key.split("."), data)
					operator_values = key_value.get("operator", {})
					operator_type = operator_values.get("type", "")
					operator_direction = operator_values.get("direction", "")
					condition_accept_list.append(resolve_condition(operator_type=operator_type, operator_direction=operator_direction, expected_value=expected_value, received_value=received_value))

				condition = False
				match config.get("routes", {}).get(route_name, {}).get("match_case", {}).get(match_value, {}).get("triggers_type", "or"):
					case "and":
						condition = condition_accept_list.count(True) == len(condition_accept_list)
					case "or":
						condition = True in condition_accept_list
					case _:
						condition = True in condition_accept_list

				if condition:
					route = config["routes"][route_name]
					senders = route.get("senders", {})
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

								message: str = (route.get("match_case", [{}]).get(match_value, {}) or {}).get("message", {})
								message_global: str = message.get("global", "")
								telegram_message: str = message.get("telegram", {}).get("content", message_global)
								msg_replaces = format_str_with_args(msg_replaces=telegram_message, data=data)
								sends_result.append(telegram.send(message=msg_replaces, data=data))
							case "discord":
								discord = Discord(
									url=senders.get(sender, {}).get('url', ''),
									config=DiscordConfig(
										username=senders.get(sender, {}).get('username', None),
										avatar_url=senders.get(sender, {}).get('avatar_url', None)
									)
								)

								message: str = (route.get("match_case", [{}]).get(match_value, {}) or {}).get("message", {})
								message_global: str = message.get("global", "")
								discord_json_message = message.get("discord", {})
								discord_json_message["content"] = discord_json_message.get("content", message_global)
								discord_json_message = format_all_str_with_args(
									json_config=discord_json_message,
									data=data)
								sends_result.append(discord.send(json_config=discord_json_message, data=data))
							case _:
								print("pass")
								print(f"sender = {sender}")
								# pass
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
