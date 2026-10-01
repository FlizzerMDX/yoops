from functools import reduce
import string

def remove_empty_from_dict(dict):
	return {key: value for key, value in dict.items() if value is not None and value != ''}

def recursive_str_vars(message):
	return [
		field_name
		for _, field_name, _, _ in string.Formatter().parse(message)
		if field_name is not None
	]

def format_str_with_args(msg_replaces, data):
	for name in recursive_str_vars(message=msg_replaces):
		formatted_name = reduce(lambda x, k: x.get(k, {}) if isinstance(x, dict) else {}, name.split("."), data)
		formatted_name = ", ".join(formatted_name) if isinstance(formatted_name, list) else formatted_name
		msg_replaces = msg_replaces.replace("{" + name + "}", str(formatted_name))
	return msg_replaces

def format_all_str_with_args(json_config, data):
	stack = [json_config]

	while stack:
		current = stack.pop()

		if isinstance(current, dict):
			for key, value in current.items():
				if isinstance(value, str):
					current[key] = format_str_with_args(msg_replaces=value, data=data)
				elif isinstance(value, (dict, list)):
					stack.append(value)

		elif isinstance(current, list):
			for i, value in enumerate(current):
				if isinstance(value, str):
					current[i] = format_str_with_args(msg_replaces=value, data=data)
				elif isinstance(value, (dict, list)):
					stack.append(value)

	return json_config
