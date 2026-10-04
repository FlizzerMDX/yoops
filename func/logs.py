import datetime
from typing import Literal

class bcolors:
	BOLD = '\033[1m'
	UNDERLINE = '\033[4m'
	RESET = "\033[0m"
	ERROR = '\033[91m'
	WARNING = '\033[93m'
	INFO = '\033[36m'

log_types = Literal[
	"INF",
	"WRN",
	"ERR",
	]

logs_colors = {
	"INF": bcolors.INFO,
	"WRN": bcolors.WARNING,
	"ERR": bcolors.ERROR,
}

def write_logs(type: log_types, content: str):
	output_date = datetime.datetime.now().astimezone().strftime("%Y-%m-%d %H:%M:%S")
	print(f"[{output_date}] {bcolors.BOLD}{logs_colors[type]}{type}{bcolors.RESET} {content}")
