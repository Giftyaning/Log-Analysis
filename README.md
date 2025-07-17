# ieuk-task-2025
This repo contains the log file for completing the 2025 IEUK Engineering task! The log file is too big to view in browser so you'll need to download it to your local machine. 

## Download Task
### Via Github UI 
https://github.com/user-attachments/assets/81972137-bf32-42c1-bc7d-dc65a0b9398f

### Via Git
You'll need to install Git and the Git LFS extension (which can be found [here](https://git-lfs.com/)). If you're unfamiliar with Git, I wouldn't worry about this—just download the log file via the UI. Using Git is not part of the task, so it's not worth spending too much time on it.


### Filters e.g python log_filter.py sample-log.log --top
### Basic Usage
python log_filter.py sample-log.log --> Shows all logs in the file, colorized by HTTP status code.


### Filter by HTTP Status Code
python log_filter.py sample-log.log --http 4xx              --> Shows all client errors (e.g., 403, 404).
python log_filter.py sample-log.log --subnet 185.220.100.0/22
python log_filter.py sample-log.log --http 5xx              --> Shows all server errors (e.g., 500, 502).

python log_filter.py sample-log.log --http 200,302          --> Shows only 200 OK and 302 Redirects.


### Filter by Duration
python log_filter.py sample-log.log --duration-between 300ms-2s         --> Shows requests that took between 300ms and 2 seconds.

python log_filter.py sample-log.log --duration-between 1s-10s           --> Requests lasting between 1 and 10 seconds.

python log_filter.py sample-log.log --duration-between 5m-1h            --> Requests that lasted between 5 minutes and 1 hour.


### Regex Matching (e.g., POST, specific path)
python log_filter.py sample-log.log --regex "POST"          --> Shows only POST requests.

python log_filter.py sample-log.log --regex "/login"        --> Shows requests to /login or similar endpoints.


### Filter by IP Address
python log_filter.py sample-log.log --ip 10.3.0.48          --> Shows logs from a specific IP.


### Filter by Subnet
python log_filter.py sample-log.log --subnet 10.3.0.0/24    --> Show logs from IPs in the subnet 10.3.0.0–10.3.0.255


### Filter by Time Range
python log_filter.py sample-log.log --from "01/07/2025:06:00:00" --to "01/07/2025:06:10:00"     --> Shows logs between 6:00 and 6:10 AM on July 1, 2025.

### Top 10 Longest Requests
python log_filter.py sample-log.log --top                   --> Shows the 10 slowest requests, sorted by duration.


### Summary Reports
python log_filter.py sample-log.log --summary               --> Show average request time per IP and URL.


### Combine Filters
python log_filter.py sample-log.log --http 4xx,5xx --duration-between 1s-10s --regex "/api" --subnet 10.3.0.0/16 --summary --top

--> combines everything:
Only 4xx/5xx responses
Request duration between 1s and 10s
Path matching /api
From subnet 10.3.0.0/16
Outputs both top slowest and summary reports.


### Windows PowerShell Tip
Wrap angle-based values (>1s, <10m) in quotes:                          --> [Leave like this for Bash or Unix based terminals]
python log_filter.py sample-log.log --duration-between "1s-10s"

