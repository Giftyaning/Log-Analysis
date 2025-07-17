import sys
import re
import argparse
import ipaddress
from datetime import datetime
from colorama import Fore, Style, init
from collections import defaultdict

# Initialize colorama
init(autoreset=True)

# Colorize Log Lines
def colorize_log(line):
    if ' 5' in line:
        return f"{Fore.RED}{line}{Style.RESET_ALL}"
    elif ' 4' in line:
        return f"{Fore.YELLOW}{line}{Style.RESET_ALL}"
    elif ' 2' in line:
        return f"{Fore.GREEN}{line}{Style.RESET_ALL}"
    return line

# Parse a DateTime String. Converts a date string like 01/07/2025:06:00:04 into a datetime object.
def parse_datetime(raw):
    try:
        return datetime.strptime(raw, "%d/%m/%Y:%H:%M:%S")
    except:
        return None

# Parse Duration Strings
def parse_duration(val):
    if val.endswith("ms"):
        return int(val[:-2])
    elif val.endswith("s"):
        return int(float(val[:-1]) * 1000)
    elif val.endswith("m"):
        return int(float(val[:-1]) * 60 * 1000)
    elif val.endswith("h"):
        return int(float(val[:-1]) * 60 * 60 * 1000)
    return int(val)  # fallback (ms)


# Extract Fields from Each Log Line. Everything is converted to milliseconds for comparison.
# Pulls key data from the log line and returns a dictionary with these values.
def extract_fields(line):
    match = re.match(
        r'(?P<ip>\d+\.\d+\.\d+\.\d+)\s+-\s+\w+\s+-\s+\[(?P<dt>[\d/:]+)\].+?"(?P<method>[A-Z]+)\s+(?P<url>[^\s]+)\s+HTTP.*?"\s+(?P<code>\d{3})\s+\d+\s+".*?"\s+".*?"\s+(?P<duration>\d+)',
        line
    )
    if not match:
        return None
    return {
        'ip': match.group('ip'),
        'datetime': parse_datetime(match.group('dt')),
        'method': match.group('method'),
        'url': match.group('url'),
        'code': match.group('code'),
        'duration_ms': int(match.group('duration')),
        'line': line.strip()
    }


# HTTP Code Filter. Check if the log’s HTTP code (e.g., 403, 500) matches the --http filter.
def match_http_code(code, filters):
    return code in filters


# Check Duration is Between Two Limits. Given a range (like 300ms-2s), checks if a log’s duration falls inside it.
def match_duration_between(duration_ms, between):
    if not between:
        return True
    low, high = between
    return low <= duration_ms <= high


# Filter by IP or Subnet
def ip_match(ip_str, ip_filter=None, subnet_filter=None):
    try:
        ip = ipaddress.ip_address(ip_str)
        if ip_filter and ip != ipaddress.ip_address(ip_filter):
            return False
        if subnet_filter and ip not in ipaddress.ip_network(subnet_filter, strict=False):
            return False
        return True
    except ValueError:
        return False


# Main Filtering and Printing Logic
def read_log_file(path, regex=None, from_dt=None, to_dt=None, http_codes=None,
                  duration_between=None, ip_filter=None, subnet_filter=None,
                  top_longest=False, summarize=False):
    entries = []                                                                    # all logs that match filters.
    durations_by_ip = defaultdict(list)                                             # {IP: [dur1, dur2, ...]} for averaging.
    durations_by_url = defaultdict(list)                                            # {URL: [dur1, dur2, ...]} for averaging.

    with open(path, 'r') as f:                                                      # The Filtering Loop. Each line is parsed. If parsing fails (wrong format), it’s skipped then we check each filter:
        for line in f:
            data = extract_fields(line)
            if not data:
                continue
            if from_dt and data['datetime'] and data['datetime'] < from_dt:
                continue
            if to_dt and data['datetime'] and data['datetime'] > to_dt:
                continue
            if regex and not re.search(regex, line, re.IGNORECASE):
                continue
            if http_codes and data['code'] not in http_codes:
                continue
            if duration_between and not match_duration_between(data['duration_ms'], duration_between):
                continue
            if ip_filter or subnet_filter:
                if not ip_match(data['ip'], ip_filter, subnet_filter):
                    continue

            durations_by_ip[data['ip']].append(data['duration_ms'])
            durations_by_url[data['url']].append(data['duration_ms'])
            entries.append(data)

    if top_longest:                                                                             # Top 10 Longest Requests. Sorts all matched logs by duration and prints the top 10.
        print("\n🔟 Top 10 Longest Requests:")
        top = sorted(entries, key=lambda x: x['duration_ms'], reverse=True)[:10]
        for item in top:
            print(f"{item['duration_ms']}ms - {item['ip']} {item['method']} {item['url']}")

    if summarize:                                                                               # Average Duration by IP and URL
        print("\n📊 Average Duration by IP:")
        for ip, times in durations_by_ip.items():
            avg = sum(times) / len(times)
            print(f"{ip}: {avg:.2f} ms")

        print("\n📊 Average Duration by URL:")
        for url, times in durations_by_url.items():
            avg = sum(times) / len(times)
            print(f"{url}: {avg:.2f} ms")

    if not top_longest and not summarize:                                                       # If Not Top or Summary → Print Full Logs
        for e in entries:
            print(colorize_log(e['line']))

def parse_http_codes(raw):                                                                      # Parse HTTP Codes Like 5xx etc. Accepts mixed formats: --http 4xx,200,302
    result = []
    if not raw:
        return result
    for part in raw.split(','):
        part = part.strip()
        if part.endswith("xx"):
            base = int(part[0]) * 100
            result.extend([str(base + i) for i in range(100)])
        else:
            result.append(part)
    return result

if __name__ == "__main__":
    parser = argparse.ArgumentParser()                                                              # Command-Line Arguments. Parses values and prepares them for filtering.
    parser.add_argument("file", help="Log file path")
    parser.add_argument("--regex", help="Regex pattern to filter")
    parser.add_argument("--from", dest="from_time", help="Start time [DD/MM/YYYY:HH:MM:SS]")
    parser.add_argument("--to", dest="to_time", help="End time [DD/MM/YYYY:HH:MM:SS]")
    parser.add_argument("--http", help="HTTP code filter: 4xx,5xx,200,etc")
    parser.add_argument("--duration-between", help="Filter duration between two values: e.g. 500ms-2s")
    parser.add_argument("--ip", help="Filter by exact IP")
    parser.add_argument("--subnet", help="Filter by subnet (CIDR)")
    parser.add_argument("--top", action="store_true", help="Show top 10 longest requests")
    parser.add_argument("--summary", action="store_true", help="Show average duration per IP and URL")

    args = parser.parse_args()

    from_dt = parse_datetime(args.from_time) if args.from_time else None
    to_dt = parse_datetime(args.to_time) if args.to_time else None
    http_codes = parse_http_codes(args.http)

    between = None
    if args.duration_between:
        try:
            low_raw, high_raw = args.duration_between.split("-")
            between = (parse_duration(low_raw), parse_duration(high_raw))
        except:
            print("Invalid --duration-between format. Use like: 300ms-2s")
            sys.exit(1)

    read_log_file(                                                                      # Final Execution Call
        args.file,
        regex=args.regex,
        from_dt=from_dt,
        to_dt=to_dt,
        http_codes=http_codes,
        duration_between=between,
        ip_filter=args.ip,
        subnet_filter=args.subnet,
        top_longest=args.top,
        summarize=args.summary
    )
