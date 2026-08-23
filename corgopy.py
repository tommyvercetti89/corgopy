#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sys
import os
import time
import socket
import ssl
import json
import re
import ipaddress
import asyncio
import concurrent.futures
from datetime import datetime
from typing import List, Dict, Tuple, Optional, Any, Union

if sys.platform == "win32":
    try:
        import ctypes
        kernel32 = ctypes.windll.kernel32
        hOut = kernel32.GetStdHandle(-11)
        out_mode = ctypes.c_ulong()
        if kernel32.GetConsoleMode(hOut, ctypes.byref(out_mode)):
            kernel32.SetConsoleMode(hOut, out_mode.value | 0x0004 | 0x0008)
        os.system("")
    except Exception:
        pass

try:
    from rich.console import Console
    from rich.table import Table
    from rich.progress import Progress, BarColumn, TextColumn, TimeElapsedColumn, SpinnerColumn
    RICH_AVAILABLE = True
    console = Console(force_terminal=True, color_system="auto")
except ImportError:
    RICH_AVAILABLE = False
    console = None


class UI:
    @staticmethod
    def strip_markup(text: str) -> str:
        clean = re.sub(r'\[/?[a-z_]+(?:\s+[a-z_]+)*\]', '', text)
        return clean.replace('\\[', '[')

    @staticmethod
    def print(msg: str = ""):
        if RICH_AVAILABLE and console:
            console.print(msg)
        else:
            print(UI.strip_markup(msg))

    @staticmethod
    def input(prompt_str: str) -> str:
        if RICH_AVAILABLE and console:
            return console.input(prompt_str).strip()
        else:
            return input(UI.strip_markup(prompt_str)).strip()

    @staticmethod
    def info(msg: str):
        UI.print(f"[bold cyan]\\[*][/bold cyan] {msg}")

    @staticmethod
    def success(msg: str):
        UI.print(f"[bold green]\\[+][/bold green] {msg}")

    @staticmethod
    def warn(msg: str):
        UI.print(f"[bold yellow]\\[!][/bold yellow] {msg}")

    @staticmethod
    def error(msg: str):
        UI.print(f"[bold red]\\[-][/bold red] {msg}")


PORT_SERVICES: Dict[int, str] = {
    20: "FTP-Data",
    21: "FTP",
    22: "SSH (OpenSSH)",
    23: "Telnet",
    25: "SMTP",
    43: "WHOIS",
    53: "DNS",
    67: "DHCP Server",
    68: "DHCP Client",
    69: "TFTP",
    80: "HTTP",
    88: "Kerberos",
    110: "POP3",
    111: "RPCBind",
    113: "Ident",
    119: "NNTP",
    123: "NTP",
    135: "MSRPC",
    137: "NetBIOS-NS",
    138: "NetBIOS-DGM",
    139: "NetBIOS-SSN",
    143: "IMAP",
    161: "SNMP",
    162: "SNMP-Trap",
    179: "BGP",
    194: "IRC",
    389: "LDAP",
    443: "HTTPS (SSL/TLS)",
    445: "Microsoft-DS (SMB)",
    465: "SMTPS",
    500: "ISAKMP (IPsec)",
    514: "Syslog",
    515: "LPD",
    520: "RIP",
    587: "SMTP Submission",
    631: "IPP (CUPS)",
    636: "LDAPS",
    873: "Rsync",
    990: "FTPS",
    993: "IMAPS",
    995: "POP3S",
    1080: "SOCKS Proxy",
    1194: "OpenVPN",
    1433: "MSSQL Server",
    1434: "MSSQL-Monitor",
    1521: "Oracle Database",
    1723: "PPTP",
    1883: "MQTT",
    2049: "NFS",
    2082: "cPanel HTTP",
    2083: "cPanel HTTPS",
    2086: "WHM HTTP",
    2087: "WHM HTTPS",
    2181: "Apache ZooKeeper",
    2375: "Docker API (Unencrypted)",
    2376: "Docker API (TLS)",
    2379: "etcd Client API",
    3000: "Node.js / React Web Service",
    3128: "Squid Proxy",
    3268: "Global Catalog LDAP",
    3306: "MySQL / MariaDB",
    3389: "RDP (Remote Desktop)",
    3690: "SVN",
    4000: "Node.js Dev Server",
    4369: "Erlang Port Mapper (epmd)",
    5000: "Flask / Docker Registry",
    5060: "SIP (VoIP)",
    5222: "XMPP / Jabber",
    5432: "PostgreSQL Database",
    5601: "Kibana Dashboard",
    5672: "RabbitMQ Broker",
    5900: "VNC Remote Desktop",
    5901: "VNC Display :1",
    5984: "CouchDB",
    5985: "WinRM HTTP",
    5986: "WinRM HTTPS",
    6000: "X11 Server",
    6379: "Redis In-Memory Store",
    6443: "Kubernetes API Server",
    6667: "IRC Server",
    7000: "Cassandra Internal",
    7001: "WebLogic / Cassandra",
    7077: "Apache Spark Master",
    7474: "Neo4j Graph Database",
    8000: "HTTP Alternate",
    8008: "HTTP Alternate",
    8080: "HTTP Proxy / Apache Tomcat",
    8081: "HTTP Alternate / Nexus",
    8088: "Hadoop YARN NodeManager",
    8443: "HTTPS Alternate",
    8888: "Jupyter Notebook",
    9000: "SonarQube / Portainer",
    9042: "Cassandra Native",
    9090: "Prometheus Web UI",
    9092: "Apache Kafka Broker",
    9100: "Prometheus Node Exporter",
    9200: "Elasticsearch REST API",
    9300: "Elasticsearch Cluster",
    10000: "Webmin Admin",
    11211: "Memcached",
    27017: "MongoDB Database",
    27018: "MongoDB Shard",
    28017: "MongoDB Web Status",
    50000: "SAP / Jenkins JNLP",
    50070: "Hadoop HDFS NameNode",
}

TOP_100_PORTS: List[int] = [
    7, 9, 13, 21, 22, 23, 25, 26, 37, 53, 79, 80, 81, 88, 106, 110, 111, 113,
    119, 135, 139, 143, 144, 179, 199, 389, 427, 443, 444, 445, 465, 513, 514,
    515, 543, 544, 548, 554, 587, 631, 646, 873, 990, 993, 995, 1025, 1026, 1027,
    1028, 1029, 1110, 1433, 1720, 1723, 1755, 1900, 2000, 2001, 2049, 2121, 2717,
    3000, 3128, 3306, 3389, 3986, 4899, 5000, 5009, 5051, 5060, 5101, 5190, 5357,
    5432, 5631, 5666, 5800, 5900, 6000, 6001, 6646, 7070, 8000, 8008, 8009, 8080,
    8081, 8443, 8888, 9000, 9090, 9100, 9999, 10000, 32768, 49152, 49153, 49154
]

TOP_1000_PORTS: List[int] = sorted(list(set(
    TOP_100_PORTS + list(PORT_SERVICES.keys()) + [i for i in range(1, 1025)]
)))[:1000]

HIGH_RISK_PORTS: List[int] = [
    21, 22, 23, 25, 110, 135, 139, 445, 1433, 1434, 1521, 2049, 2181, 2375, 2376,
    3306, 3389, 5432, 5900, 5901, 5984, 5985, 5986, 6379, 6443, 7001, 8080, 9000,
    9200, 9300, 10000, 11211, 27017, 27018, 50000
]

WEB_PORTS: List[int] = [
    80, 81, 88, 443, 2082, 2083, 2086, 2087, 3000, 4000, 5000, 5601, 5985, 7001,
    7474, 8000, 8008, 8080, 8081, 8088, 8443, 8888, 9000, 9090, 9200, 9443, 10000, 50070
]


class PortResult:
    def __init__(self, port: int, state: str = "OPEN", protocol: str = "tcp"):
        self.port: int = port
        self.state: str = state
        self.protocol: str = protocol
        self.service: str = PORT_SERVICES.get(port, "unknown")
        self.banner: str = ""
        self.http_title: str = ""
        self.http_server: str = ""
        self.http_status: str = ""
        self.ssl_issuer: str = ""
        self.ssl_subject: str = ""
        self.ssl_expiry: str = ""
        self.rtt_ms: float = 0.0

    def get_summary_banner(self) -> str:
        parts = []
        if self.banner:
            clean = self.banner.replace("\r", " ").replace("\n", " ").strip()
            parts.append(clean[:80])
        if self.http_status:
            parts.append(f"HTTP {self.http_status}")
        if self.http_server:
            parts.append(f"Server: {self.http_server}")
        if self.http_title:
            parts.append(f"Title: \"{self.http_title}\"")
        if self.ssl_subject:
            parts.append(f"SSL: {self.ssl_subject}")
        return " | ".join(parts) if parts else "No banner response"

    def to_dict(self) -> Dict[str, Any]:
        return {
            "port": self.port,
            "state": self.state,
            "protocol": self.protocol,
            "service": self.service,
            "banner": self.banner,
            "http_status": self.http_status,
            "http_server": self.http_server,
            "http_title": self.http_title,
            "ssl_subject": self.ssl_subject,
            "ssl_issuer": self.ssl_issuer,
            "ssl_expiry": self.ssl_expiry,
            "rtt_ms": round(self.rtt_ms, 2)
        }


class HostScanReport:
    def __init__(self, target_input: str, resolved_ip: str):
        self.target_input: str = target_input
        self.resolved_ip: str = resolved_ip
        self.hostname: str = ""
        self.os_guess: str = "Unknown"
        self.ttl: int = 0
        self.latency_ms: float = 0.0
        self.scan_profile: str = ""
        self.engine_type: str = "AsyncIO"
        self.start_time: str = ""
        self.end_time: str = ""
        self.duration_seconds: float = 0.0
        self.total_ports_scanned: int = 0
        self.open_ports: List[PortResult] = []
        self.concurrency: int = 200
        self.timeout: float = 0.5

    def to_dict(self) -> Dict[str, Any]:
        return {
            "scan_metadata": {
                "tool": "Corgopy",
                "version": "2.6.0",
                "engine": self.engine_type,
                "profile": self.scan_profile,
                "start_time": self.start_time,
                "end_time": self.end_time,
                "duration_seconds": round(self.duration_seconds, 2),
                "ports_scanned": self.total_ports_scanned,
                "open_ports_count": len(self.open_ports),
                "concurrency": self.concurrency,
                "timeout_seconds": self.timeout
            },
            "host_information": {
                "target_input": self.target_input,
                "resolved_ip": self.resolved_ip,
                "hostname": self.hostname,
                "os_guess": self.os_guess,
                "ttl": self.ttl,
                "latency_ms": round(self.latency_ms, 2)
            },
            "open_ports": [p.to_dict() for p in sorted(self.open_ports, key=lambda x: x.port)]
        }


class DeepProber:
    @staticmethod
    def sanitize_banner(raw_bytes: bytes) -> str:
        try:
            text = raw_bytes.decode('utf-8', errors='ignore')
        except Exception:
            text = repr(raw_bytes)
        clean = "".join(c for c in text if c.isprintable() or c in ("\n", "\r", "\t"))
        return clean.strip()

    @classmethod
    def probe_http(cls, host: str, port: int, use_ssl: bool = False, timeout: float = 1.5) -> Tuple[str, str, str]:
        status, server, title = "", "", ""
        try:
            raw_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            raw_sock.settimeout(timeout)
            
            if use_ssl or port in (443, 8443, 9443, 2083, 2087, 6443):
                ctx = ssl.create_default_context()
                ctx.check_hostname = False
                ctx.verify_mode = ssl.CERT_NONE
                sock = ctx.wrap_socket(raw_sock, server_hostname=host)
            else:
                sock = raw_sock

            sock.connect((host, port))
            request = f"GET / HTTP/1.1\r\nHost: {host}:{port}\r\nUser-Agent: Corgopy/2.6\r\nAccept: */*\r\nConnection: close\r\n\r\n"
            sock.sendall(request.encode('utf-8', errors='ignore'))
            
            response = b""
            while len(response) < 4096:
                chunk = sock.recv(1024)
                if not chunk:
                    break
                response += chunk
            sock.close()

            text_resp = response.decode('utf-8', errors='ignore')
            lines = text_resp.split("\r\n")
            if lines and ("HTTP/" in lines[0]):
                status = lines[0].split(" ", 1)[1] if len(lines[0].split(" ", 1)) > 1 else lines[0]
            
            for line in lines:
                if line.lower().startswith("server:"):
                    server = line.split(":", 1)[1].strip()
                elif line.lower().startswith("x-powered-by:"):
                    powered = line.split(":", 1)[1].strip()
                    server = f"{server} (Powered by: {powered})" if server else powered

            title_match = re.search(r"<title[^>]*>(.*?)</title>", text_resp, re.IGNORECASE | re.DOTALL)
            if title_match:
                title = title_match.group(1).strip()
                title = re.sub(r'\s+', ' ', title)
        except Exception:
            pass
        return status, server, title

    @classmethod
    def probe_ssl_cert(cls, host: str, port: int, timeout: float = 1.5) -> Tuple[str, str, str]:
        subject, issuer, expiry = "", "", ""
        try:
            ctx = ssl.create_default_context()
            ctx.check_hostname = False
            ctx.verify_mode = ssl.CERT_NONE
            with socket.create_connection((host, port), timeout=timeout) as sock:
                with ctx.wrap_socket(sock, server_hostname=host) as ssock:
                    cert = ssock.getpeercert(binary_form=False)
                    if cert:
                        subj_dict = dict(x[0] for x in cert.get('subject', []))
                        subject = subj_dict.get('commonName', '') or subj_dict.get('organizationName', '')
                        iss_dict = dict(x[0] for x in cert.get('issuer', []))
                        issuer = iss_dict.get('commonName', '') or iss_dict.get('organizationName', '')
                        expiry = cert.get('notAfter', '')
        except Exception:
            pass
        return subject, issuer, expiry

    @classmethod
    def probe_generic_banner(cls, host: str, port: int, timeout: float = 1.5) -> str:
        banner = ""
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                s.settimeout(timeout)
                s.connect((host, port))
                
                try:
                    initial = s.recv(1024)
                    if initial:
                        banner = cls.sanitize_banner(initial)
                except socket.timeout:
                    pass

                if not banner:
                    if port == 6379:
                        s.sendall(b"PING\r\n")
                    elif port in (21, 25, 110, 143):
                        s.sendall(b"HELP\r\n")
                    else:
                        s.sendall(b"\r\n\r\n")
                    
                    try:
                        reply = s.recv(1024)
                        if reply:
                            banner = cls.sanitize_banner(reply)
                    except socket.timeout:
                        pass
        except Exception:
            pass
        return banner


class AsyncScanner:
    def __init__(self, target_ip: str, ports: List[int], concurrency: int = 200, timeout: float = 0.5, on_port_found=None, on_progress=None):
        self.target_ip: str = target_ip
        self.ports: List[int] = ports
        self.concurrency: int = concurrency
        self.timeout: float = timeout
        self.on_port_found = on_port_found
        self.on_progress = on_progress
        self.open_ports: List[PortResult] = []
        self.scanned_count: int = 0
        self.is_aborted: bool = False
        self._tasks: List[asyncio.Task] = []

    def abort(self):
        self.is_aborted = True
        for t in self._tasks:
            if not t.done():
                t.cancel()

    async def _scan_single_port(self, sem: asyncio.Semaphore, port: int) -> Optional[PortResult]:
        if self.is_aborted:
            return None
        try:
            async with sem:
                if self.is_aborted:
                    return None
                t0 = time.perf_counter()
                try:
                    conn = asyncio.open_connection(self.target_ip, port)
                    reader, writer = await asyncio.wait_for(conn, timeout=self.timeout)
                    rtt = (time.perf_counter() - t0) * 1000.0
                    
                    result = PortResult(port=port, state="OPEN", protocol="tcp")
                    result.rtt_ms = rtt
                    
                    try:
                        banner_data = await asyncio.wait_for(reader.read(512), timeout=0.25)
                        if banner_data:
                            result.banner = DeepProber.sanitize_banner(banner_data)
                    except Exception:
                        pass
                    
                    writer.close()
                    try:
                        await writer.wait_closed()
                    except Exception:
                        pass

                    if not self.is_aborted:
                        self.open_ports.append(result)
                        if self.on_port_found:
                            self.on_port_found(result)
                    return result
                except (asyncio.TimeoutError, ConnectionRefusedError, OSError):
                    return None
                finally:
                    self.scanned_count += 1
                    if self.on_progress and not self.is_aborted:
                        self.on_progress(self.scanned_count, len(self.ports), port)
        except asyncio.CancelledError:
            return None

    async def run(self) -> List[PortResult]:
        sem = asyncio.Semaphore(self.concurrency)
        self._tasks = [asyncio.create_task(self._scan_single_port(sem, p)) for p in self.ports]
        try:
            await asyncio.gather(*self._tasks, return_exceptions=True)
        except asyncio.CancelledError:
            pass
        return self.open_ports


class ThreadedScanner:
    def __init__(self, target_ip: str, ports: List[int], concurrency: int = 200, timeout: float = 0.5, on_port_found=None, on_progress=None):
        self.target_ip: str = target_ip
        self.ports: List[int] = ports
        self.concurrency: int = concurrency
        self.timeout: float = timeout
        self.on_port_found = on_port_found
        self.on_progress = on_progress
        self.open_ports: List[PortResult] = []
        self.scanned_count: int = 0
        self.is_aborted: bool = False
        self._executor: Optional[concurrent.futures.ThreadPoolExecutor] = None

    def abort(self):
        self.is_aborted = True
        if self._executor:
            self._executor.shutdown(wait=False, cancel_futures=True)

    def _scan_worker(self, port: int) -> Optional[PortResult]:
        if self.is_aborted:
            return None
        t0 = time.perf_counter()
        res = None
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                s.settimeout(self.timeout)
                err = s.connect_ex((self.target_ip, port))
                if err == 0 and not self.is_aborted:
                    rtt = (time.perf_counter() - t0) * 1000.0
                    res = PortResult(port=port, state="OPEN", protocol="tcp")
                    res.rtt_ms = rtt
                    
                    try:
                        s.settimeout(0.25)
                        data = s.recv(512)
                        if data:
                            res.banner = DeepProber.sanitize_banner(data)
                    except Exception:
                        pass

                    if not self.is_aborted:
                        self.open_ports.append(res)
                        if self.on_port_found:
                            self.on_port_found(res)
        except Exception:
            pass
        finally:
            self.scanned_count += 1
            if self.on_progress and not self.is_aborted:
                self.on_progress(self.scanned_count, len(self.ports), port)
        return res

    def run(self) -> List[PortResult]:
        self._executor = concurrent.futures.ThreadPoolExecutor(max_workers=self.concurrency)
        try:
            futures = {self._executor.submit(self._scan_worker, p): p for p in self.ports}
            for future in concurrent.futures.as_completed(futures):
                if self.is_aborted:
                    self._executor.shutdown(wait=False, cancel_futures=True)
                    break
        finally:
            if not self.is_aborted:
                self._executor.shutdown(wait=True)
        return self.open_ports


class SubnetScanner:
    @staticmethod
    def parse_subnet_targets(cidr_str: str) -> List[str]:
        try:
            net = ipaddress.ip_network(cidr_str, strict=False)
            hosts = [str(ip) for ip in net.hosts()]
            return hosts if hosts else [str(net.network_address)]
        except Exception as e:
            UI.error(f"Gecersiz Subnet/CIDR: {e}")
            return []

    @classmethod
    def sweep_host(cls, ip: str, probe_ports: List[int] = [80, 443, 22, 445, 135, 3389, 21], timeout: float = 0.4) -> Optional[Dict[str, Any]]:
        is_alive = False
        open_p = []
        
        for port in probe_ports:
            try:
                with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                    s.settimeout(timeout)
                    if s.connect_ex((ip, port)) == 0:
                        is_alive = True
                        open_p.append(port)
            except Exception:
                pass
        
        if is_alive:
            try:
                hostname = socket.gethostbyaddr(ip)[0]
            except Exception:
                hostname = "N/A"
            return {"ip": ip, "hostname": hostname, "open_ports": open_p}
        return None

    @classmethod
    def run_sweep(cls, targets: List[str], concurrency: int = 100, on_host_found=None, on_progress=None) -> List[Dict[str, Any]]:
        alive_hosts = []
        total = len(targets)
        scanned = 0
        
        with concurrent.futures.ThreadPoolExecutor(max_workers=concurrency) as executor:
            try:
                future_to_ip = {executor.submit(cls.sweep_host, ip): ip for ip in targets}
                for future in concurrent.futures.as_completed(future_to_ip):
                    scanned += 1
                    if on_progress:
                        on_progress(scanned, total, future_to_ip[future])
                    res = future.result()
                    if res:
                        alive_hosts.append(res)
                        if on_host_found:
                            on_host_found(res)
            except KeyboardInterrupt:
                executor.shutdown(wait=False, cancel_futures=True)
                UI.warn("\nSubnet taramasi durduruldu.")
        return alive_hosts


class ReportExporter:
    @staticmethod
    def ensure_export_dir() -> str:
        export_dir = os.path.join(os.getcwd(), "exports")
        os.makedirs(export_dir, exist_ok=True)
        return export_dir

    @classmethod
    def export_json(cls, report: HostScanReport) -> str:
        export_dir = cls.ensure_export_dir()
        clean_ip = report.resolved_ip.replace(":", "_")
        filename = f"corgopy_{clean_ip}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        filepath = os.path.join(export_dir, filename)
        
        with open(filepath, "w", encoding="utf-8") as f:
            json.dump(report.to_dict(), f, indent=4, ensure_ascii=False)
        return filepath

    @classmethod
    def export_txt(cls, report: HostScanReport) -> str:
        export_dir = cls.ensure_export_dir()
        clean_ip = report.resolved_ip.replace(":", "_")
        filename = f"corgopy_{clean_ip}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
        filepath = os.path.join(export_dir, filename)

        lines = [
            "=" * 78,
            "CORGOPY - NETWORK RECONNAISSANCE & PORT SCAN REPORT",
            "=" * 78,
            f"Target Input       : {report.target_input}",
            f"Resolved IP        : {report.resolved_ip}",
            f"Hostname           : {report.hostname or 'N/A'}",
            f"Estimated OS       : {report.os_guess} (TTL: {report.ttl})",
            f"Scan Profile       : {report.scan_profile}",
            f"Scan Engine        : {report.engine_type} ({report.concurrency} threads/coros, {report.timeout}s timeout)",
            f"Start Time         : {report.start_time}",
            f"End Time           : {report.end_time}",
            f"Duration           : {report.duration_seconds:.2f} seconds",
            f"Total Scanned      : {report.total_ports_scanned} ports",
            f"Open Ports Found   : {len(report.open_ports)}",
            "-" * 78,
            f"{'PORT':<10} {'STATE':<8} {'SERVICE':<22} {'DETAILS / BANNER'}",
            "-" * 78
        ]

        for p in sorted(report.open_ports, key=lambda x: x.port):
            port_str = f"{p.port}/tcp"
            details = p.get_summary_banner()
            lines.append(f"{port_str:<10} {p.state:<8} {p.service[:20]:<22} {details}")

        lines.append("=" * 78)
        lines.append(f"Report Generated at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')} by Corgopy v2.6.0")
        lines.append("=" * 78)

        with open(filepath, "w", encoding="utf-8") as f:
            f.write("\n".join(lines))
        return filepath

    @classmethod
    def export_html(cls, report: HostScanReport) -> str:
        export_dir = cls.ensure_export_dir()
        clean_ip = report.resolved_ip.replace(":", "_")
        filename = f"corgopy_{clean_ip}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.html"
        filepath = os.path.join(export_dir, filename)

        rows_html = []
        for p in sorted(report.open_ports, key=lambda x: x.port):
            banner_esc = (p.banner or "").replace("<", "&lt;").replace(">", "&gt;")
            title_esc = (p.http_title or "").replace("<", "&lt;").replace(">", "&gt;")
            server_esc = (p.http_server or "").replace("<", "&lt;").replace(">", "&gt;")
            ssl_esc = (p.ssl_subject or "").replace("<", "&lt;").replace(">", "&gt;")

            extra_parts = []
            if p.http_status:
                extra_parts.append(f'<span class="badge badge-info">HTTP {p.http_status}</span>')
            if server_esc:
                extra_parts.append(f'<span class="badge badge-secondary">Server: {server_esc}</span>')
            if title_esc:
                extra_parts.append(f'<div class="meta-item"><strong>Title:</strong> {title_esc}</div>')
            if ssl_esc:
                extra_parts.append(f'<div class="meta-item"><strong>SSL Subject:</strong> {ssl_esc}</div>')
            if banner_esc:
                extra_parts.append(f'<div class="meta-code"><code>{banner_esc}</code></div>')

            details_html = "".join(extra_parts) if extra_parts else '<span class="text-muted">No banner response</span>'

            row = f"""
            <tr>
                <td><span class="badge badge-port">{p.port}/tcp</span></td>
                <td><span class="badge badge-open">[+] OPEN</span></td>
                <td><strong>{p.service}</strong></td>
                <td><span class="text-mono">{p.rtt_ms:.1f} ms</span></td>
                <td>{details_html}</td>
            </tr>
            """
            rows_html.append(row)

        table_body = "".join(rows_html) if rows_html else '<tr><td colspan="5" style="text-align:center; padding: 30px; color:#8b949e;">No open ports discovered.</td></tr>'

        html_content = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Corgopy Recon Report - {report.resolved_ip}</title>
    <style>
        :root {{
            --bg-primary: #0a0e17;
            --bg-card: #111927;
            --bg-card-hover: #162032;
            --border-color: #1e293b;
            --text-primary: #f1f5f9;
            --text-secondary: #94a3b8;
            --text-muted: #64748b;
            --accent-cyan: #00e5ff;
            --accent-green: #10b981;
            --accent-yellow: #f59e0b;
            --accent-red: #ef4444;
            --accent-purple: #8b5cf6;
        }}
        * {{
            box-sizing: border-box;
            margin: 0;
            padding: 0;
            font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Helvetica Neue", Arial, sans-serif;
        }}
        body {{
            background-color: var(--bg-primary);
            color: var(--text-primary);
            padding: 30px 20px;
            line-height: 1.5;
        }}
        .container {{
            max-width: 1200px;
            margin: 0 auto;
        }}
        .header {{
            background: linear-gradient(135deg, #0d1527 0%, #152238 100%);
            border: 1px solid var(--border-color);
            border-radius: 12px;
            padding: 24px 30px;
            margin-bottom: 24px;
            display: flex;
            justify-content: space-between;
            align-items: center;
            flex-wrap: wrap;
            gap: 15px;
        }}
        .header-title h1 {{
            font-size: 24px;
            letter-spacing: 1px;
            color: var(--accent-cyan);
            font-weight: 700;
        }}
        .header-title p {{
            color: var(--text-secondary);
            font-size: 13px;
            margin-top: 4px;
        }}
        .header-badge {{
            background: rgba(0, 229, 255, 0.1);
            border: 1px solid var(--accent-cyan);
            color: var(--accent-cyan);
            padding: 6px 14px;
            border-radius: 20px;
            font-size: 12px;
            font-weight: bold;
            letter-spacing: 0.5px;
        }}
        .stats-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(220px, 1fr));
            gap: 16px;
            margin-bottom: 24px;
        }}
        .stat-card {{
            background-color: var(--bg-card);
            border: 1px solid var(--border-color);
            border-radius: 10px;
            padding: 18px 20px;
        }}
        .stat-label {{
            font-size: 12px;
            color: var(--text-secondary);
            text-transform: uppercase;
            letter-spacing: 0.5px;
            margin-bottom: 6px;
        }}
        .stat-value {{
            font-size: 22px;
            font-weight: 700;
            color: var(--text-primary);
        }}
        .stat-value.highlight-green {{ color: var(--accent-green); }}
        .stat-value.highlight-cyan {{ color: var(--accent-cyan); }}
        .stat-value.highlight-yellow {{ color: var(--accent-yellow); }}
        
        .info-panel {{
            background-color: var(--bg-card);
            border: 1px solid var(--border-color);
            border-radius: 10px;
            padding: 20px;
            margin-bottom: 24px;
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));
            gap: 16px;
            font-size: 14px;
        }}
        .info-item strong {{
            color: var(--text-secondary);
            margin-right: 8px;
        }}

        .search-bar {{
            margin-bottom: 16px;
            display: flex;
            gap: 10px;
        }}
        .search-input {{
            flex: 1;
            background-color: var(--bg-card);
            border: 1px solid var(--border-color);
            color: var(--text-primary);
            padding: 10px 16px;
            border-radius: 8px;
            font-size: 14px;
            outline: none;
        }}
        .search-input:focus {{
            border-color: var(--accent-cyan);
        }}

        .table-container {{
            background-color: var(--bg-card);
            border: 1px solid var(--border-color);
            border-radius: 10px;
            overflow-x: auto;
        }}
        table {{
            width: 100%;
            border-collapse: collapse;
            text-align: left;
            font-size: 13px;
        }}
        th {{
            background-color: #0d1524;
            color: var(--text-secondary);
            padding: 14px 18px;
            font-weight: 600;
            border-bottom: 1px solid var(--border-color);
            text-transform: uppercase;
            font-size: 11px;
            letter-spacing: 0.5px;
        }}
        td {{
            padding: 14px 18px;
            border-bottom: 1px solid var(--border-color);
            vertical-align: top;
        }}
        tr:hover td {{
            background-color: var(--bg-card-hover);
        }}

        .badge {{
            display: inline-block;
            padding: 3px 8px;
            border-radius: 4px;
            font-size: 11px;
            font-weight: 600;
            font-family: monospace;
        }}
        .badge-port {{ background: #1e293b; color: var(--accent-cyan); }}
        .badge-open {{ background: rgba(16, 185, 129, 0.15); color: var(--accent-green); border: 1px solid var(--accent-green); }}
        .badge-info {{ background: rgba(0, 229, 255, 0.1); color: var(--accent-cyan); margin-right: 4px; }}
        .badge-secondary {{ background: #1e293b; color: #cbd5e1; margin-right: 4px; }}
        
        .text-mono {{ font-family: monospace; color: var(--text-secondary); }}
        .text-muted {{ color: var(--text-muted); }}
        .meta-item {{ margin-top: 5px; font-size: 12px; color: #cbd5e1; }}
        .meta-code {{
            margin-top: 6px;
            background: #090d16;
            border: 1px solid #1c2738;
            padding: 6px 10px;
            border-radius: 4px;
            font-family: monospace;
            font-size: 11px;
            color: #38bdf8;
            max-width: 600px;
            overflow-x: auto;
            white-space: pre-wrap;
            word-break: break-all;
        }}
        .footer {{
            text-align: center;
            margin-top: 30px;
            font-size: 12px;
            color: var(--text-muted);
        }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <div class="header-title">
                <h1>CORGOPY RECON REPORT</h1>
                <p>Advanced Asynchronous Network Reconnaissance & Port Scanner</p>
            </div>
            <div class="header-badge">STATUS: COMPLETE</div>
        </div>

        <div class="stats-grid">
            <div class="stat-card">
                <div class="stat-label">Target Host</div>
                <div class="stat-value highlight-cyan">{report.resolved_ip}</div>
            </div>
            <div class="stat-card">
                <div class="stat-label">Open Ports</div>
                <div class="stat-value highlight-green">{len(report.open_ports)}</div>
            </div>
            <div class="stat-card">
                <div class="stat-label">Ports Scanned</div>
                <div class="stat-value">{report.total_ports_scanned}</div>
            </div>
            <div class="stat-card">
                <div class="stat-label">Duration</div>
                <div class="stat-value highlight-yellow">{report.duration_seconds:.2f}s</div>
            </div>
        </div>

        <div class="info-panel">
            <div class="info-item"><strong>Target Input:</strong> {report.target_input}</div>
            <div class="info-item"><strong>Hostname:</strong> {report.hostname or 'N/A'}</div>
            <div class="info-item"><strong>OS Heuristic:</strong> {report.os_guess} (TTL: {report.ttl})</div>
            <div class="info-item"><strong>Scan Profile:</strong> {report.scan_profile}</div>
            <div class="info-item"><strong>Engine:</strong> {report.engine_type} ({report.concurrency} concurrent)</div>
            <div class="info-item"><strong>Scan Timestamp:</strong> {report.start_time}</div>
        </div>

        <div class="search-bar">
            <input type="text" id="searchInput" class="search-input" placeholder="Search port, service name, banner, or HTTP title..." onkeyup="filterTable()">
        </div>

        <div class="table-container">
            <table id="portsTable">
                <thead>
                    <tr>
                        <th style="width: 110px;">Port</th>
                        <th style="width: 100px;">State</th>
                        <th style="width: 200px;">Service</th>
                        <th style="width: 100px;">Latency</th>
                        <th>Service Banner / HTTP Recon / SSL Details</th>
                    </tr>
                </thead>
                <tbody>
                    {table_body}
                </tbody>
            </table>
        </div>

        <div class="footer">
            Generated by Corgopy v2.6.0 • Clean Recon Engine • No Emojis Policy Compliant
        </div>
    </div>

    <script>
        function filterTable() {{
            const input = document.getElementById("searchInput").value.toLowerCase();
            const rows = document.querySelectorAll("#portsTable tbody tr");
            rows.forEach(row => {{
                const text = row.textContent.toLowerCase();
                row.style.display = text.includes(input) ? "" : "none";
            }});
        }}
    </script>
</body>
</html>
        """
        with open(filepath, "w", encoding="utf-8") as f:
            f.write(html_content)
        return filepath


class InputParser:
    @staticmethod
    def parse_port_range(input_str: str) -> List[int]:
        ports = set()
        parts = input_str.replace(" ", "").split(",")
        for part in parts:
            if not part:
                continue
            if "-" in part:
                subparts = part.split("-")
                if len(subparts) == 2 and subparts[0].isdigit() and subparts[1].isdigit():
                    start_p, end_p = int(subparts[0]), int(subparts[1])
                    start_p = max(1, min(start_p, 65535))
                    end_p = max(1, min(end_p, 65535))
                    if start_p > end_p:
                        start_p, end_p = end_p, start_p
                    for p in range(start_p, end_p + 1):
                        ports.add(p)
            elif part.isdigit():
                p = int(part)
                if 1 <= p <= 65535:
                    ports.add(p)
        return sorted(list(ports))

    @staticmethod
    def is_private_or_local(ip_str: str) -> bool:
        try:
            ip_obj = ipaddress.ip_address(ip_str)
            return ip_obj.is_private or ip_obj.is_loopback
        except ValueError:
            return False

    @staticmethod
    def resolve_target(target: str) -> Tuple[Optional[str], Optional[str]]:
        target = target.strip()
        if not target:
            return None, None
        try:
            ipaddress.ip_address(target)
            return target, target
        except ValueError:
            try:
                ip = socket.gethostbyname(target)
                return target, ip
            except socket.gaierror as e:
                UI.error(f"Hedef cozumlenemedi ({target}): {e}")
                return None, None

    @staticmethod
    def estimate_os_ttl(target_ip: str) -> Tuple[str, int]:
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                s.settimeout(1.0)
                for p in [80, 443, 22, 53, 445, 135]:
                    if s.connect_ex((target_ip, p)) == 0:
                        ttl = s.getsockopt(socket.IPPROTO_IP, socket.IP_TTL)
                        if ttl <= 64:
                            return "Linux / Unix / macOS / Android", ttl
                        elif ttl <= 128:
                            return "Windows (10 / 11 / Server)", ttl
                        elif ttl <= 255:
                            return "Cisco / Network Appliance / Solaris", ttl
                        return "Unknown OS", ttl
        except Exception:
            pass
        return "Unknown OS (TTL not captured)", 0


class CorgopyApp:
    def __init__(self):
        self.engine_type: str = "AsyncIO"
        self.concurrency: int = 200
        self.timeout: float = 0.5
        self.last_report: Optional[HostScanReport] = None

    def print_banner(self):
        banner_text = """
================================================================================
  ______   ______   ______   ______   ______   ______   __  __ 
 /\\  ___\\ /\\  __ \\ /\\  == \\ /\\  ___\\ /\\  __ \\ /\\  == \\ /\\ \\_\\ \\
 \\ \\ \\____\\ \\ \\/\\ \\\\ \\  __< \\ \\ \\__ \\\\ \\ \\/\\ \\\\ \\  _-/ \\ \\____ \\
  \\ \\_____\\\\ \\_____\\\\ \\_\\ \\_\\\\ \\_____\\\\ \\_____\\\\ \\_\\    \\/\\_____\\
   \\/_____/ \\/_____/ \\/_/ /_/ \\/_____/ \\/_____/ \\/_/     \\/_____/
                                                                 
  [+] CORGOPY - Advanced Port & Network Reconnaissance Engine
  [+] Version : 2.6.0 | Dual Engine: AsyncIO & ThreadPool
  [+] Safety  : Public IP Typo Guard & Instant Ctrl+C Abort Enabled
  [+] Status  : Ready | Clean Cyber CLI (Strictly No Emojis)
================================================================================
"""
        UI.print(f"[bold cyan]{banner_text}[/bold cyan]")

    def show_main_menu(self):
        UI.print("\n[bold cyan][ MAIN MENU ][/bold cyan]")
        UI.print("[bright_black]" + "-" * 80 + "[/bright_black]")
        UI.print(" [bold cyan]\\[1][/bold cyan]  Quick Scan                  : Top 100 En Yaygin Portlar")
        UI.print(" [bold cyan]\\[2][/bold cyan]  Standard Scan               : Top 1000 Port (Nmap Standardi)")
        UI.print(" [bold cyan]\\[3][/bold cyan]  Full Range Scan             : 1 - 65535 Tum Portlar")
        UI.print(" [bold cyan]\\[4][/bold cyan]  Custom Port Range / List    : Ozel Port Araligi (Orn: 80,443,8000-8080)")
        UI.print(" [bold cyan]\\[5][/bold cyan]  High-Risk Services Scan     : Kritik Veritabani, RDP, SMB, VNC Portlari")
        UI.print(" [bold cyan]\\[6][/bold cyan]  Web Services Recon          : HTTP/HTTPS, Web Server, Title & SSL Analizi")
        UI.print(" [bold cyan]\\[7][/bold cyan]  Subnet / Host Discovery     : Ag Cihaz Kesfi (CIDR / IP Araligi Sweep)")
        UI.print(" [bold cyan]\\[8][/bold cyan]  Deep Service Recon          : Acik Portlar Uzerinde Detayli Banner & SSL Grab")
        UI.print(f" [bold cyan]\\[9][/bold cyan]  Engine & Settings           : Motor Secimi, Is Parcacigi ({self.concurrency}) & Zaman Asimi ({self.timeout}s)")
        UI.print(" [bold cyan]\\[10][/bold cyan] Export Last Scan           : Son Tarama Raporunu Disa Aktar (HTML / JSON / TXT)")
        UI.print(" [bold cyan]\\[0][/bold cyan]  Exit                        : Cikis")
        UI.print("[bright_black]" + "-" * 80 + "[/bright_black]")

    def settings_menu(self):
        while True:
            UI.print("\n[bold yellow][ ENGINE & PERFORMANCE AYARLARI ][/bold yellow]")
            UI.print(f" [bold cyan]\\[1][/bold cyan] Calisma Motoru     : {self.engine_type} (AsyncIO / ThreadPool)")
            UI.print(f" [bold cyan]\\[2][/bold cyan] Eszamanlilik Sayisi: {self.concurrency} (50 - 1000 arasi)")
            UI.print(f" [bold cyan]\\[3][/bold cyan] Socket Zaman Asimi : {self.timeout} saniye (0.1s - 3.0s)")
            UI.print(" [bold cyan]\\[0][/bold cyan] Ana Menuye Don")
            
            choice = UI.input("\n[bold cyan]\\[?][/bold cyan] Seciminiz [0-3]: ")
            if choice == "1":
                self.engine_type = "ThreadPool" if self.engine_type == "AsyncIO" else "AsyncIO"
                UI.success(f"Tarama motoru degistirildi: {self.engine_type}")
            elif choice == "2":
                val = UI.input(f"[bold cyan]\\[?][/bold cyan] Yeni eszamanlilik limitini girin (50-1000) [{self.concurrency}]: ")
                if val.isdigit() and 10 <= int(val) <= 2000:
                    self.concurrency = int(val)
                    UI.success(f"Eszamanlilik guncellendi: {self.concurrency}")
                else:
                    UI.warn("Gecersiz sayi!")
            elif choice == "3":
                val = UI.input(f"[bold cyan]\\[?][/bold cyan] Yeni zaman asimini saniye olarak girin (0.1 - 3.0) [{self.timeout}]: ")
                try:
                    t_val = float(val)
                    if 0.05 <= t_val <= 10.0:
                        self.timeout = t_val
                        UI.success(f"Zaman asimi guncellendi: {self.timeout}s")
                    else:
                        UI.warn("Gecersiz zaman araligi!")
                except ValueError:
                    UI.warn("Gecersiz ondalikli sayi!")
            elif choice == "0":
                break

    def prompt_target_and_validate(self) -> Optional[str]:
        target = UI.input("[bold cyan]\\[?][/bold cyan] Hedef IP veya Domain girin: ")
        if not target:
            return None
        
        target_name, target_ip = InputParser.resolve_target(target)
        if not target_ip:
            return None

        is_private = InputParser.is_private_or_local(target_ip)
        is_official_test = target_name.lower() in ("scanme.nmap.org", "localhost", "127.0.0.1")

        if not is_private and not is_official_test:
            UI.print("\n[bold yellow]" + "!" * 80 + "[/bold yellow]")
            UI.warn(f"DIKKAT: '{target_ip}' bir dis internet (Public IP) adresidir.")
            UI.warn("Yerel modeminiz degildir (Yerel ev aginiz 192.168.x.x blogundadir).")
            UI.print("[bold yellow]" + "!" * 80 + "[/bold yellow]")
            confirm = UI.input("[bold cyan]\\[?][/bold cyan] Bu dis IP adresini taramak istediginizden emin misiniz? (E/H) [Varsayilan: H]: ").lower()
            if confirm not in ("e", "evet", "y", "yes"):
                UI.info("Tarama guvenlik geregi iptal edildi. Ana menuye donuluyor.\n")
                return None

        return target

    def run_port_scan_pipeline(self, target_input: str, ports: List[int], profile_name: str, do_deep_recon: bool = True):
        target_name, target_ip = InputParser.resolve_target(target_input)
        if not target_ip:
            return

        report = HostScanReport(target_input=target_name, resolved_ip=target_ip)
        report.scan_profile = profile_name
        report.engine_type = self.engine_type
        report.concurrency = self.concurrency
        report.timeout = self.timeout
        report.total_ports_scanned = len(ports)
        report.start_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        try:
            report.hostname = socket.gethostbyaddr(target_ip)[0]
        except Exception:
            report.hostname = "N/A"
        
        report.os_guess, report.ttl = InputParser.estimate_os_ttl(target_ip)

        UI.print("\n" + "=" * 80)
        UI.info(f"Hedef         : [bold white]{target_name}[/bold white] ({target_ip})")
        UI.info(f"Hostname      : {report.hostname}")
        UI.info(f"OS Tahmini    : {report.os_guess} (TTL: {report.ttl})")
        UI.info(f"Profil        : {profile_name} ({len(ports)} port)")
        UI.info(f"Motor         : {self.engine_type} | Concurrency: {self.concurrency} | Timeout: {self.timeout}s")
        UI.info("[bold yellow]DURDURMA BILGISI: Taramayi istediginiz an aninda kesmek icin [Ctrl + C] tuslarina basabilirsiniz.[/bold yellow]")
        UI.print("=" * 80 + "\n")

        found_ports: List[PortResult] = []
        is_user_aborted = False

        def on_port_discovered(p_res: PortResult):
            UI.success(f"Port Bulundu: [bold green]{p_res.port}/tcp[/bold green] | Servis: [cyan]{p_res.service}[/cyan] (RTT: {p_res.rtt_ms:.1f}ms)")

        t_start = time.perf_counter()

        if self.engine_type == "AsyncIO":
            scanner = AsyncScanner(
                target_ip=target_ip,
                ports=ports,
                concurrency=self.concurrency,
                timeout=self.timeout,
                on_port_found=on_port_discovered
            )
        else:
            scanner = ThreadedScanner(
                target_ip=target_ip,
                ports=ports,
                concurrency=self.concurrency,
                timeout=self.timeout,
                on_port_found=on_port_discovered
            )

        if RICH_AVAILABLE and console:
            try:
                with Progress(
                    SpinnerColumn(spinner_name="dots"),
                    TextColumn("[bold cyan]{task.description}"),
                    BarColumn(bar_width=40),
                    TextColumn("[progress.percentage]{task.percentage:>3.0f}%"),
                    TextColumn("({task.completed}/{task.total} port)"),
                    TimeElapsedColumn(),
                    console=console
                ) as progress:
                    task_id = progress.add_task("[bold cyan]Portlar Taraniyor...", total=len(ports))
                    
                    def update_progress(done: int, total: int, current_port: int):
                        progress.update(task_id, completed=done)

                    scanner.on_progress = update_progress

                    if self.engine_type == "AsyncIO":
                        found_ports = asyncio.run(scanner.run())
                    else:
                        found_ports = scanner.run()
            except KeyboardInterrupt:
                is_user_aborted = True
                scanner.abort()
                UI.warn("\n[!] DIKKAT: Tarama kullanici tarafindan aninda kesildi (Ctrl+C).")
                found_ports = scanner.open_ports
        else:
            def update_cli_progress(done: int, total: int, current_port: int):
                if done % 25 == 0 or done == total:
                    pct = (done / total) * 100
                    sys.stdout.write(f"\r[*] Taraniyor: %{pct:.1f} ({done}/{total}) - Port: {current_port}   ")
                    sys.stdout.flush()

            scanner.on_progress = update_cli_progress

            try:
                if self.engine_type == "AsyncIO":
                    found_ports = asyncio.run(scanner.run())
                else:
                    found_ports = scanner.run()
            except KeyboardInterrupt:
                is_user_aborted = True
                scanner.abort()
                UI.warn("\n[!] DIKKAT: Tarama durduruldu (Ctrl+C).")
                found_ports = scanner.open_ports
            print()

        t_duration = time.perf_counter() - t_start
        report.duration_seconds = t_duration
        report.end_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        report.open_ports = found_ports

        if do_deep_recon and report.open_ports and not is_user_aborted:
            UI.print("\n" + "-" * 80)
            UI.info(f"Acik portlar uzerinde Derin Servis & Banner Grabbing baslatiliyor ({len(report.open_ports)} port)...")
            UI.print("-" * 80)
            
            for p in report.open_ports:
                is_web = p.port in WEB_PORTS or "http" in p.service.lower() or p.port in (80, 443, 8080, 8443, 3000, 5000, 8000)
                if is_web:
                    is_ssl = p.port in (443, 8443, 9443, 2083, 2087, 6443)
                    status, server, title = DeepProber.probe_http(target_ip, p.port, use_ssl=is_ssl, timeout=1.5)
                    if status:
                        p.http_status = status
                    if server:
                        p.http_server = server
                    if title:
                        p.http_title = title
                    
                    if is_ssl or p.port == 443:
                        subj, iss, exp = DeepProber.probe_ssl_cert(target_ip, p.port, timeout=1.5)
                        if subj:
                            p.ssl_subject = subj
                            p.ssl_issuer = iss
                            p.ssl_expiry = exp

                if not p.banner and not p.http_title:
                    banner = DeepProber.probe_generic_banner(target_ip, p.port, timeout=1.5)
                    if banner:
                        p.banner = banner

        self.display_scan_results(report)
        self.last_report = report
        self.prompt_export_menu(report)

    def display_scan_results(self, report: HostScanReport):
        UI.print("\n" + "=" * 80)
        UI.print("[bold green][ TARAMA TAMAMLANDI - SONUCLAR ][/bold green]")
        UI.print(f" Hedef IP        : [bold white]{report.resolved_ip}[/bold white] ({report.hostname or 'N/A'})")
        UI.print(f" Sure            : [bold yellow]{report.duration_seconds:.2f}[/bold yellow] saniye")
        UI.print(f" Acik Port Sayisi: [bold green]{len(report.open_ports)}[/bold green] / {report.total_ports_scanned}")
        UI.print("=" * 80)

        if not report.open_ports:
            UI.warn("Hedefte belirtilen aralikta hicbir acik port bulunamadi.")
            return

        if RICH_AVAILABLE and console:
            table = Table(title=f"Open Ports on {report.resolved_ip}", show_header=True, header_style="bold cyan", border_style="bright_black")
            table.add_column("PORT", style="bold green", width=12)
            table.add_column("STATE", style="bold yellow", width=10)
            table.add_column("SERVICE", style="cyan", width=24)
            table.add_column("LATENCY", style="dim", width=10)
            table.add_column("DETAILS / BANNER / HTTP RECON", style="white")

            for p in sorted(report.open_ports, key=lambda x: x.port):
                summary = p.get_summary_banner()
                table.add_row(f"{p.port}/tcp", "[+] OPEN", p.service[:23], f"{p.rtt_ms:.1f}ms", summary)
            console.print(table)
        else:
            print(f"\n{'PORT':<12} {'STATE':<10} {'SERVICE':<24} {'LATENCY':<10} {'DETAILS / BANNER'}")
            print("-" * 78)
            for p in sorted(report.open_ports, key=lambda x: x.port):
                summary = p.get_summary_banner()
                print(f"{f'{p.port}/tcp':<12} {'[+] OPEN':<10} {p.service[:23]:<24} {f'{p.rtt_ms:.1f}ms':<10} {summary}")
            print("-" * 78)

    def prompt_export_menu(self, report: HostScanReport):
        UI.print("\n[bold cyan][ RAPOR DISA AKTARMA ][/bold cyan]")
        UI.print(" [bold cyan]\\[1][/bold cyan] HTML Dashboard Raporu Olarak Kaydet")
        UI.print(" [bold cyan]\\[2][/bold cyan] JSON Dosyasi Olarak Kaydet")
        UI.print(" [bold cyan]\\[3][/bold cyan] TXT Metin Raporu Olarak Kaydet")
        UI.print(" [bold cyan]\\[4][/bold cyan] Tum Formatlarda Kaydet (HTML + JSON + TXT)")
        UI.print(" [bold cyan]\\[0][/bold cyan] Rapor Kaydetmeden Devam Et")
        
        choice = UI.input("\n[bold cyan]\\[?][/bold cyan] Seciminiz [0-4] [Varsayilan: 1]: ") or "1"
        if choice == "1":
            path = ReportExporter.export_html(report)
            UI.success(f"HTML Rapor kaydedildi: {path}")
        elif choice == "2":
            path = ReportExporter.export_json(report)
            UI.success(f"JSON Rapor kaydedildi: {path}")
        elif choice == "3":
            path = ReportExporter.export_txt(report)
            UI.success(f"TXT Rapor kaydedildi: {path}")
        elif choice == "4":
            p_html = ReportExporter.export_html(report)
            p_json = ReportExporter.export_json(report)
            p_txt = ReportExporter.export_txt(report)
            UI.success(f"HTML Rapor : {p_html}")
            UI.success(f"JSON Rapor : {p_json}")
            UI.success(f"TXT Rapor  : {p_txt}")
        elif choice == "0":
            UI.info("Rapor disari aktarilmadi.")

    def run_subnet_discovery_pipeline(self):
        cidr_input = UI.input("\n[bold cyan]\\[?][/bold cyan] Taranacak Subnet / CIDR girin (Orn: 192.168.1.0/24): ")
        if not cidr_input:
            UI.warn("Girdi bos olamaz!")
            return
        
        targets = SubnetScanner.parse_subnet_targets(cidr_input)
        if not targets:
            return
        
        UI.print("\n" + "=" * 80)
        UI.info(f"Subnet Kesfi Baslatiliyor: {cidr_input} ({len(targets)} host)")
        UI.info(f"Eszamanlilik: {self.concurrency} | Timeout: {self.timeout}s")
        UI.info("[bold yellow]DURDURMA BILGISI: [Ctrl + C] ile istediginiz an kesebilirsiniz.[/bold yellow]")
        UI.print("=" * 80 + "\n")

        alive_results = []
        
        def on_host_found(h):
            ports_str = ", ".join(str(x) for x in h['open_ports']) if h['open_ports'] else "N/A"
            UI.success(f"Canli Host: [bold green]{h['ip']}[/bold green] | Hostname: {h['hostname']} | Acik Portlar: {ports_str}")

        if RICH_AVAILABLE and console:
            try:
                with Progress(
                    SpinnerColumn(spinner_name="dots"),
                    TextColumn("[bold cyan]{task.description}"),
                    BarColumn(bar_width=40),
                    TextColumn("[progress.percentage]{task.percentage:>3.0f}%"),
                    TextColumn("({task.completed}/{task.total} IP)"),
                    TimeElapsedColumn(),
                    console=console
                ) as progress:
                    task_id = progress.add_task("[bold cyan]IP'ler Taranıyor...", total=len(targets))
                    def update_prog(done, total, current_ip):
                        progress.update(task_id, completed=done)
                    alive_results = SubnetScanner.run_sweep(targets, concurrency=self.concurrency, on_host_found=on_host_found, on_progress=update_prog)
            except KeyboardInterrupt:
                UI.warn("\nSubnet taramasi durduruldu (Ctrl+C).")
        else:
            def update_cli_prog(done, total, current_ip):
                if done % 10 == 0 or done == total:
                    sys.stdout.write(f"\r[*] Taranan: {done}/{total} - IP: {current_ip}   ")
                    sys.stdout.flush()
            alive_results = SubnetScanner.run_sweep(targets, concurrency=self.concurrency, on_host_found=on_host_found, on_progress=update_cli_prog)
            print()

        UI.print("\n" + "=" * 80)
        UI.success(f"Subnet Taramasi Tamamlandi! Bulunan Canli Host Sayisi: {len(alive_results)} / {len(targets)}")
        UI.print("=" * 80)

        if alive_results:
            UI.print("\n" + f"{'IP ADRESI':<18} {'HOSTNAME':<28} {'TESPIT EDILEN PORTLAR'}")
            UI.print("-" * 80)
            for h in alive_results:
                ports_str = ", ".join(str(x) for x in h['open_ports']) if h['open_ports'] else "Discovery probe"
                UI.print(f"{h['ip']:<18} {h['hostname'][:26]:<28} {ports_str}")
            UI.print("-" * 80)

    def start(self):
        self.print_banner()
        while True:
            self.show_main_menu()
            choice = UI.input("\n[bold cyan]\\[?][/bold cyan] Seciminiz [0-10]: ")

            if choice == "1":
                target = self.prompt_target_and_validate()
                if target:
                    self.run_port_scan_pipeline(target, TOP_100_PORTS, "Quick Scan (Top 100 Ports)")

            elif choice == "2":
                target = self.prompt_target_and_validate()
                if target:
                    self.run_port_scan_pipeline(target, TOP_1000_PORTS, "Standard Scan (Top 1000 Ports)")

            elif choice == "3":
                target = self.prompt_target_and_validate()
                if target:
                    confirm = UI.input("[bold yellow]\\[!][/bold yellow] 1-65535 tum portlar taranacak. Devam edilsin mi? (E/H) [E]: ").lower()
                    if confirm in ("", "e", "y"):
                        full_ports = list(range(1, 65536))
                        self.run_port_scan_pipeline(target, full_ports, "Full Range Scan (1-65535)")

            elif choice == "4":
                target = self.prompt_target_and_validate()
                if target:
                    port_str = UI.input("[bold cyan]\\[?][/bold cyan] Port araligi veya listesi girin (Orn: 80,443,8000-8080,3306): ")
                    parsed = InputParser.parse_port_range(port_str)
                    if parsed:
                        UI.info(f"Ayristirilan port sayisi: {len(parsed)} port")
                        self.run_port_scan_pipeline(target, parsed, f"Custom Scan ({port_str})")
                    else:
                        UI.error("Gecersiz port formati!")

            elif choice == "5":
                target = self.prompt_target_and_validate()
                if target:
                    self.run_port_scan_pipeline(target, HIGH_RISK_PORTS, "High-Risk & Database Services Scan")

            elif choice == "6":
                target = self.prompt_target_and_validate()
                if target:
                    self.run_port_scan_pipeline(target, WEB_PORTS, "Web & API Services Recon")

            elif choice == "7":
                self.run_subnet_discovery_pipeline()

            elif choice == "8":
                target = self.prompt_target_and_validate()
                if target:
                    port_str = UI.input("[bold cyan]\\[?][/bold cyan] Port listesi girin [Varsayilan: Top 100]: ")
                    ports = InputParser.parse_port_range(port_str) if port_str else TOP_100_PORTS
                    self.run_port_scan_pipeline(target, ports, "Deep Service & Banner Recon", do_deep_recon=True)

            elif choice == "9":
                self.settings_menu()

            elif choice == "10":
                if self.last_report:
                    self.prompt_export_menu(self.last_report)
                else:
                    UI.warn("Henuz yapilmis bir tarama bulunmuyor!")

            elif choice == "0":
                UI.info("Corgopy kapatiliyor. Iyi calismalar!")
                break
            else:
                UI.warn("Gecersiz secim! Lutfen listeden bir sayi girin.")


if __name__ == "__main__":
    try:
        app = CorgopyApp()
        app.start()
    except KeyboardInterrupt:
        UI.warn("\n[-] Program kullanici tarafindan sonlandirildi.")
        sys.exit(0)
