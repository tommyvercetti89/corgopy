# CORGOPY

Advanced Asynchronous Network Reconnaissance & Port Scanner written in Python.

Corgopy is a fast, multi-threaded, and asynchronous network port scanning and intelligence tool. It provides an interactive Terminal UI (TUI) menu, eliminating the need to pass manual CLI arguments, alongside flexible port range parsing, deep service banner grabbing, HTTP/SSL reconnaissance, subnet host discovery, and multi-format export capabilities.

---

## Key Features

- **Dual Scanning Core**:
  - **AsyncIO Engine**: Non-blocking coroutine-based socket scanner with configurable concurrency for high-speed reconnaissance.
  - **ThreadPool Engine**: Multi-threaded socket scanner with worker pooling.
- **Interactive Terminal UI**: Menu-driven interface that prompts for targets and scan profiles directly.
- **Custom Port Range Parser**: Supports single ports, comma-separated lists, and arbitrary ranges (e.g., `80`, `80,443,8080`, `1-1000`, `21,22,80-90,8000-8080,3306`).
- **Deep Service & Banner Grabbing**:
  - TCP banner grabber for SSH, FTP, SMTP, MySQL, Redis, Telnet, POP3, IMAP, etc.
  - Web service inspector: extracts HTTP response codes, `Server` and `X-Powered-By` headers, and HTML `<title>` tags.
  - SSL/TLS certificate inspector: extracts Subject Common Name, Issuer, and Expiration dates on encrypted ports.
  - Packet TTL heuristic analysis for remote OS estimation (Linux/Unix, Windows, Cisco/Network appliances).
- **Subnet & Local Network Discovery**: Ping & port sweep engine for CIDR blocks (e.g., `192.168.1.0/24`) and IP ranges.
- **Safety & Protection Guards**:
  - **Public IP Typo Guard**: Automatically detects external Internet IP entries to prevent accidental scans caused by typos and prompts for explicit confirmation.
  - **Instant Emergency Abort**: Pressing `Ctrl + C` immediately closes all active sockets and terminates scanning in milliseconds.
- **Multi-Format Export Engine**:
  - **HTML**: Dark-mode cybersecurity dashboard with searchable tables and stat cards.
  - **JSON**: Structured machine-readable data for script automation.
  - **TXT**: Clean plain-text ASCII summary report.
- **Zero-Emoji Compliance**: Fully conforms to clean, text-based terminal standards using `[+]`, `[-]`, `[*]`, `[!]`, and `[OPEN]` indicators.

---

## Installation

### Prerequisites
- Python 3.8 or newer

### Setup
Clone the repository:
```bash
git clone https://github.com/tommyvercetti89/corgopy.git
cd corgopy
```

Install dependencies:
```bash
pip install -r requirements.txt
```

---

## Usage

### On Windows
Run using the one-click batch launcher:
```cmd
run.bat
```
Or run directly with Python:
```bash
python corgopy.py
```

### On Linux / macOS
```bash
python3 corgopy.py
```

---

## Scan Profiles

| Option | Profile | Description |
|---|---|---|
| [1] | Quick Scan | Scans the top 100 most common ports. |
| [2] | Standard Scan | Scans the top 1000 standard ports (Nmap profile). |
| [3] | Full Range Scan | Scans all ports from 1 to 65535. |
| [4] | Custom Port Range | Scans user-specified ports or ranges (e.g., `80,443,8000-8080`). |
| [5] | High-Risk Services | Targets databases, RDP, SMB, VNC, Redis, MongoDB, and remote admin ports. |
| [6] | Web Services Recon | Targets HTTP/HTTPS endpoints with title, web server, and SSL extraction. |
| [7] | Subnet / Host Discovery | Sweeps CIDR network blocks to discover live hosts. |
| [8] | Deep Service Recon | Performs deep banner and protocol probing across target ports. |
| [9] | Engine & Settings | Configures AsyncIO / ThreadPool engine, concurrency limit (50-1000), and socket timeout. |
| [10]| Export Last Scan | Exports the latest scan report to HTML, JSON, or TXT format in `./exports/`. |
| [0] | Exit | Safely closes the application. |

---

## Project Structure

```text
corgopy/
├── corgopy.py          # Main application, scanning engines, and UI
├── run.bat             # Windows one-click launcher
├── requirements.txt    # Python dependencies
├── .gitignore          # Git ignore rules
├── LICENSE             # MIT License
└── README.md           # Documentation
```

---

## Legal Disclaimer

This tool is designed strictly for educational, security auditing, and defensive network administration purposes. Port scanning remote networks without authorization may violate terms of service or applicable laws. Ensure you have proper authorization before scanning any target network.

---

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
