from functools import reduce
import string

def resolve_condition_with_direction(operator_type, value, reference):
	match operator_type:
		case "less":
			return value < reference
		case "greater":
			return value > reference
		case "less_equal":
			return value <= reference
		case "greater_equal":
			return value >= reference
		case "not_in":
			return value not in reference
		case "in":
			return value in reference
		case "not_equal":
			return value != reference
		case "equal":
			return value == reference
		case _:
			return value == reference

def resolve_condition(operator_type, operator_direction, expected_value, received_value):
	match operator_direction:
		case "config_to_api":
			return resolve_condition_with_direction(reference=received_value, value=expected_value, operator_direction=operator_direction, operator_type=operator_type)
		case "api_to_config":
			return resolve_condition_with_direction(reference=expected_value, value=received_value, operator_direction=operator_direction, operator_type=operator_type)
		case _:
			return resolve_condition_with_direction(reference=expected_value, value=received_value, operator_direction=operator_direction, operator_type=operator_type)

def remove_empty_from_dict(dict) -> dict:
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
