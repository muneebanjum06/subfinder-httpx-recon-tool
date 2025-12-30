#!/usr/bin/env python3
"""
SUBFINDER + HTTPX RECON TOOL v4.0
=================================
Enhanced with smart categorization and output like the first tool
"""

import argparse
import json
import os
import subprocess
import sys
import time
from collections import defaultdict
from datetime import datetime


# Color constants - Same as first tool
class Colors:
    RED = "\033[91m"
    GREEN = "\033[92m"
    YELLOW = "\033[93m"
    BLUE = "\033[94m"
    MAGENTA = "\033[95m"
    CYAN = "\033[96m"
    WHITE = "\033[97m"
    BRIGHT_YELLOW = "\033[93m"
    RESET = "\033[0m"
    BOLD = "\033[1m"
    DIM = "\033[2m"


class OutputManager:
    """Smart output handling like the first tool"""
    def __init__(self, max_hosts=25, group_by_ip=False):
        self.max_hosts = max_hosts
        self.group_by_ip = group_by_ip
    
    def print_banner(self):
        banner = f"""{Colors.CYAN}{Colors.BOLD}
╔═══════════════════════════════════════════════════════════════════╗
║           SUBFINDER + HTTPX RECON TOOL v4.0                       ║
║           Smart Categorization & Output                           ║
╚═══════════════════════════════════════════════════════════════════╝{Colors.RESET}
        """
        print(banner)
    
    def print_info(self, message):
        print(f"{Colors.BLUE}[*]{Colors.RESET} {message}")
    
    def print_success(self, message):
        print(f"{Colors.GREEN}[+]{Colors.RESET} {message}")
    
    def print_warning(self, message):
        print(f"{Colors.YELLOW}[!]{Colors.RESET} {message}")
    
    def print_error(self, message):
        print(f"{Colors.RED}[-]{Colors.RESET} {message}")

    def display_category_overview(self, categorized_hosts):
        """Show overview of all categories like first tool"""
        print(f"\n{Colors.CYAN}{'='*70}")
        print(f"📊 CATEGORIZED RESULTS - SMART VIEW")
        print(f"{'='*70}{Colors.RESET}\n")
        
        print(f"{Colors.MAGENTA}{'📋 CATEGORY OVERVIEW':^70}{Colors.RESET}")
        print(f"{'─'*70}")
        
        total_hosts = 0
        for category, hosts in categorized_hosts.items():
            if hosts:
                total_hosts += len(hosts)
        
        # Category order and icons like first tool
        category_order = [
            "fully_operational",
            "https_only", 
            "http_only",
            "redirects",
            "errors",
            "blocked",
            "no_response"
        ]
        
        for category in category_order:
            if category in categorized_hosts and categorized_hosts[category]:
                hosts = categorized_hosts[category]
                count = len(hosts)
                
                # Get category display info
                config = self._get_category_config(category)
                icon = config["icon"]
                name = config["name"]
                
                # Calculate percentage
                percentage = (count / total_hosts * 100) if total_hosts > 0 else 0
                
                # Determine display mode
                if count > self.max_hosts:
                    display_mode = f"Top {self.max_hosts}"
                else:
                    display_mode = "Showing all"
                
                print(f"  {icon} {name:<20} {Colors.GREEN}{count:>4}{Colors.RESET} ({percentage:5.1f}%) - {display_mode}")
        
        print(f"\n{Colors.CYAN}Total hosts across all categories: {total_hosts}{Colors.RESET}")
    
    def display_categorized_results(self, categorized_hosts):
        """Display detailed results by category"""
        # Category order for display
        category_order = [
            "fully_operational",
            "https_only",
            "http_only", 
            "redirects",
            "errors",
            "blocked",
            "no_response"
        ]
        
        for category in category_order:
            if category in categorized_hosts and categorized_hosts[category]:
                hosts = categorized_hosts[category]
                
                if len(hosts) > self.max_hosts:
                    self._display_large_category(category, hosts)
                else:
                    self._display_small_category(category, hosts)
    
    def _display_small_category(self, category, hosts):
        """Display category with few hosts (shows all)"""
        config = self._get_category_config(category)
        icon = config["icon"]
        name = config["name"]
        color = config["color"]
        
        color_code = getattr(Colors, color, Colors.WHITE)
        print(f"\n{color_code}{'─'*70}")
        print(f"{icon} {name} ({len(hosts)} hosts - Showing ALL)")
        print(f"{'─'*70}{Colors.RESET}")
        
        for i, host in enumerate(hosts, 1):
            self._display_host(host, i, color.lower())
    
    def _display_large_category(self, category, hosts):
        """Display category with many hosts (shows subset)"""
        config = self._get_category_config(category)
        icon = config["icon"]
        name = config["name"]
        color = config["color"]
        
        color_code = getattr(Colors, color, Colors.WHITE)
        print(f"\n{color_code}{'─'*70}")
        print(f"{icon} {name} ({len(hosts)} hosts - Showing top {self.max_hosts})")
        print(f"{'─'*70}{Colors.RESET}")
        
        self.print_warning(f"Large category! Showing {self.max_hosts} of {len(hosts)} hosts.")
        
        # Show subset
        for i, host in enumerate(hosts[:self.max_hosts], 1):
            self._display_host(host, i, color.lower())
        
        # Show what's not displayed
        remaining = len(hosts) - self.max_hosts
        if remaining > 0:
            print(f"\n{Colors.YELLOW}Not shown ({remaining} hosts):{Colors.RESET}")
            
            # Group remaining hosts by hostname patterns
            remaining_hosts = hosts[self.max_hosts:]
            sample = [h.get("clean_url", h.get("url", "")) for h in remaining_hosts[:3]]
            
            if len(sample) > 0:
                sample_str = ", ".join(sample)
                if remaining > 3:
                    sample_str += f" ... (+{remaining - 3} more)"
                print(f"  {Colors.BRIGHT_YELLOW}•{Colors.RESET} {sample_str}")
    
    def _display_host(self, host, index, color):
        """Display a single host"""
        url = host.get("clean_url", host.get("url", ""))
        status = host.get("status_code", "")
        title = host.get("title", "No Title")[:40]
        
        if len(url) > 40:
            url_display = url[:37] + "..."
        else:
            url_display = url
        
        if len(title) > 40:
            title_display = title[:37] + "..."
        else:
            title_display = title
        
        color_code = getattr(Colors, color.upper(), Colors.WHITE)
        
        print(f"  {Colors.DIM}{index:3}.{Colors.RESET} "
              f"{color_code}{status:4}{Colors.RESET} "
              f"{Colors.CYAN}{url_display:<43}{Colors.RESET} "
              f"{Colors.WHITE}{title_display:<43}{Colors.RESET}")
    
    def _get_category_config(self, category):
        """Get display configuration for category"""
        configs = {
            "fully_operational": {"icon": "✅", "name": "FULLY OPERATIONAL", "color": "GREEN"},
            "https_only": {"icon": "🔐", "name": "HTTPS ONLY", "color": "BLUE"},
            "http_only": {"icon": "⚠️", "name": "HTTP ONLY", "color": "YELLOW"},
            "redirects": {"icon": "↪️", "name": "REDIRECTING", "color": "MAGENTA"},
            "errors": {"icon": "🚨", "name": "SERVER ERRORS", "color": "RED"},
            "blocked": {"icon": "🚫", "name": "ACCESS BLOCKED", "color": "RED"},
            "no_response": {"icon": "🔴", "name": "NO RESPONSE", "color": "BRIGHT_YELLOW"},
        }
        return configs.get(category, {"icon": "📌", "name": category.upper(), "color": "WHITE"})
    
    def display_quick_stats(self, stats):
        """Display statistics like first tool"""
        print(f"\n{Colors.CYAN}{'📈 COMPREHENSIVE STATISTICS'}{Colors.RESET}")
        print(f"{'─'*70}")
        
        # Two column layout
        stats_table1 = []
        stats_table2 = []
        
        # Basic stats
        stats_table1.append(("Total Discovered", str(stats.get("total_discovered", 0))))
        stats_table1.append(("DNS Resolved", str(stats.get("dns_resolved", 0))))
        stats_table1.append(("Online Hosts", str(stats.get("online_hosts", 0))))
        stats_table1.append(("Web Services", str(stats.get("web_services", 0))))
        
        # Category stats
        stats_table2.append(("Fully Operational", str(stats.get("fully_operational", 0))))
        stats_table2.append(("Redirects", str(stats.get("redirects", 0))))
        stats_table2.append(("Blocked", str(stats.get("blocked", 0))))
        stats_table2.append(("Server Errors", str(stats.get("errors", 0))))
        
        # Display in two columns
        col_width = 25
        for (label1, value1), (label2, value2) in zip(stats_table1, stats_table2):
            print(f"{Colors.CYAN}{label1:<{col_width}}{Colors.RESET}{Colors.GREEN}{value1:>10}{Colors.RESET}   "
                  f"{Colors.CYAN}{label2:<{col_width}}{Colors.RESET}{Colors.GREEN}{value2:>10}{Colors.RESET}")
    
    def display_interesting_finds(self, interesting):
        """Display interesting findings"""
        if not any(interesting.values()):
            return
        
        print(f"\n{Colors.MAGENTA}{'🎯 INTERESTING FINDS'}{Colors.RESET}")
        print(f"{'─'*70}")
        
        for category, hosts in interesting.items():
            if hosts:
                print(f"\n{Colors.YELLOW}{category.replace('_', ' ').title()}: ({len(hosts)} found){Colors.RESET}")
                
                # Show all if few, otherwise show top 8
                if len(hosts) <= 10:
                    for host in hosts:
                        print(f"  • {host}")
                else:
                    for host in hosts[:8]:
                        print(f"  • {host}")
                    print(f"  {Colors.BRIGHT_YELLOW}... and {len(hosts) - 8} more{Colors.RESET}")


class ReconCategorizer:
    """Categorize httpx results like first tool"""
    
    @staticmethod
    def categorize_results(results):
        """Categorize httpx results"""
        categorized = defaultdict(list)
        stats = {
            "total_discovered": len(results),
            "dns_resolved": len(results),  # httpx only returns resolved hosts
            "online_hosts": len(results),
            "web_services": 0,
            "fully_operational": 0,
            "https_only": 0,
            "http_only": 0,
            "redirects": 0,
            "errors": 0,
            "blocked": 0,
            "no_response": 0,
        }
        
        interesting = {
            "admin_panels": [],
            "api_endpoints": [],
            "development_servers": [],
            "shared_hosting": [],  # Would need IP data
        }
        
        # First pass: categorize by status
        for result in results:
            status = result.get("status_code", 0)
            url = result.get("url", "")
            
            # Clean URL for display
            clean_url = url.replace("https://", "").replace("http://", "")
            result["clean_url"] = clean_url
            
            # Determine if HTTPS or HTTP
            is_https = url.startswith("https://")
            
            # Build host data
            host_data = {
                "url": url,
                "clean_url": clean_url,
                "status_code": status,
                "title": result.get("title", "No Title"),
                "is_https": is_https,
            }
            
            # Categorize
            if status == 200:
                stats["web_services"] += 1
                stats["fully_operational"] += 1
                categorized["fully_operational"].append(host_data)
            elif status in [301, 302, 307, 308]:
                stats["web_services"] += 1
                stats["redirects"] += 1
                categorized["redirects"].append(host_data)
            elif status == 403 or status == 401:
                stats["web_services"] += 1
                stats["blocked"] += 1
                categorized["blocked"].append(host_data)
            elif 400 <= status < 500:
                stats["web_services"] += 1
                stats["errors"] += 1
                categorized["errors"].append(host_data)
            elif status >= 500:
                stats["web_services"] += 1
                stats["errors"] += 1
                categorized["errors"].append(host_data)
            elif status == 0:  # No response
                stats["no_response"] += 1
                categorized["no_response"].append(host_data)
            else:
                stats["web_services"] += 1
                categorized["fully_operational"].append(host_data)
            
            # Check for interesting finds
            ReconCategorizer._check_interesting_finds(result, interesting)
        
        return dict(categorized), stats, interesting
    
    @staticmethod
    def _check_interesting_finds(result, interesting):
        """Check for interesting patterns"""
        url = result.get("url", "").lower()
        title = result.get("title", "").lower()
        
        # Admin panels
        admin_keywords = ["admin", "login", "panel", "dashboard", "control", "administrator"]
        if any(keyword in url or keyword in title for keyword in admin_keywords):
            interesting["admin_panels"].append(result.get("clean_url", url))
        
        # API endpoints
        api_keywords = ["api.", "/api", "/v1", "/v2", "/v3", "/graphql", "/rest"]
        if any(keyword in url for keyword in api_keywords):
            interesting["api_endpoints"].append(result.get("clean_url", url))
        
        # Development servers
        dev_ports = [":3000", ":5000", ":8000", ":8080", ":9000", ":4200"]
        if any(port in url for port in dev_ports):
            interesting["development_servers"].append(result.get("clean_url", url))


def check_httpx_version():
    """Check httpx version and available flags"""
    try:
        result = subprocess.run(
            ["httpx", "-h"], capture_output=True, text=True, timeout=5
        )
        output = result.stdout + result.stderr
        return True
    except Exception:
        print(f"{Colors.RED}[-]{Colors.RESET} httpx not found! Install with:")
        print(f"    go install -v github.com/projectdiscovery/httpx/cmd/httpx@latest")
        return False


def run_subfinder(domain, output_file):
    """Run subfinder to discover subdomains"""
    print(f"{Colors.BLUE}[*]{Colors.RESET} Running Subfinder for: {Colors.CYAN}{domain}{Colors.RESET}")
    
    cmd = ["subfinder", "-d", domain, "-silent", "-o", output_file]
    
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=300)
        
        if result.returncode != 0:
            return False
        
        if os.path.exists(output_file):
            with open(output_file, "r") as f:
                subdomains = [line.strip() for line in f if line.strip()]
                if subdomains:
                    print(f"{Colors.GREEN}[+]{Colors.RESET} Found {Colors.CYAN}{len(subdomains)}{Colors.RESET} subdomains")
                    return True
        return False
        
    except Exception:
        return False


def run_httpx(input_file, output_file, simple_mode=False):
    """Run httpx with stdin approach"""
    if not os.path.exists(input_file):
        return False
    
    with open(input_file, "r") as f:
        subdomain_list = f.read()
    
    print(f"{Colors.BLUE}[*]{Colors.RESET} Running httpx on {Colors.CYAN}{len(subdomain_list.splitlines())}{Colors.RESET} subdomains...")
    
    # Try different command approaches
    if simple_mode:
        cmd = ["httpx", "-silent", "-status-code", "-title", "-json"]
    else:
        cmd = ["httpx", "-silent", "-status-code", "-title", "-tech-detect", "-json"]
    
    try:
        result = subprocess.run(
            cmd, input=subdomain_list, capture_output=True, text=True, timeout=900
        )
        
        if result.returncode == 0 and result.stdout:
            lines = [line.strip() for line in result.stdout.split("\n") if line.strip()]
            if lines:
                with open(output_file, "w") as f:
                    for line in lines:
                        f.write(line + "\n")
                print(f"{Colors.GREEN}[+]{Colors.RESET} Found {Colors.GREEN}{len(lines)}{Colors.RESET} alive hosts")
                return True
    except Exception:
        pass
    
    return False


def parse_httpx_results(results_file):
    """Parse httpx JSON results"""
    results = []
    
    if not os.path.exists(results_file):
        return results
    
    with open(results_file, "r") as f:
        for line in f:
            line = line.strip()
            if line:
                try:
                    data = json.loads(line)
                    if "url" in data:
                        results.append(data)
                except json.JSONDecodeError:
                    continue
    
    return results


def save_enhanced_results(results, categorized, stats, interesting, domain, output_dir):
    """Save enhanced results like first tool"""
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
    
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    
    # Enhanced JSON with all data
    enhanced = {
        "metadata": {
            "domain": domain,
            "timestamp": datetime.now().isoformat(),
            "tool": "subfinder_httpx_v4.0",
            "total_results": len(results)
        },
        "statistics": stats,
        "categorized_results": categorized,
        "interesting_finds": interesting,
        "raw_data": results
    }
    
    # Save JSON
    json_file = f"{output_dir}/recon_{domain}_{timestamp}.json"
    try:
        with open(json_file, "w") as f:
            json.dump(enhanced, f, indent=2, default=str)
        print(f"{Colors.GREEN}[+]{Colors.RESET} JSON report: {Colors.CYAN}{json_file}{Colors.RESET}")
    except Exception as e:
        print(f"{Colors.RED}[-]{Colors.RESET} Failed to save JSON: {str(e)}")
    
    # Save text report
    txt_file = f"{output_dir}/recon_{domain}_{timestamp}.txt"
    try:
        with open(txt_file, "w") as f:
            f.write(f"{'='*70}\n")
            f.write(f"RECONNAISSANCE REPORT - {domain}\n")
            f.write(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write(f"{'='*70}\n\n")
            
            f.write("STATISTICS\n")
            f.write("-" * 40 + "\n")
            for key, value in stats.items():
                f.write(f"{key.replace('_', ' ').title()}: {value}\n")
            
            f.write("\n\nCATEGORIZED RESULTS\n")
            f.write("=" * 60 + "\n")
            
            for category, hosts in categorized.items():
                if hosts:
                    f.write(f"\n{category.upper()} ({len(hosts)} hosts)\n")
                    f.write("-" * 40 + "\n")
                    for host_info in hosts:
                        url = host_info.get('clean_url', host_info.get('url', ''))
                        status = host_info.get('status_code', 'N/A')
                        title = host_info.get('title', 'No Title')
                        f.write(f"{url} (Status: {status})\n")
                        f.write(f"  Title: {title}\n\n")
        
        print(f"{Colors.GREEN}[+]{Colors.RESET} Text report: {Colors.CYAN}{txt_file}{Colors.RESET}")
    except Exception as e:
        print(f"{Colors.RED}[-]{Colors.RESET} Failed to save text report: {str(e)}")


def main():
    parser = argparse.ArgumentParser(
        description="Subfinder + httpx Recon Tool v4.0 - Enhanced with smart output",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=f"""
{Colors.CYAN}Examples for Large Results:{Colors.RESET}
  {sys.argv[0]} -d example.com                    # Default (25 hosts/category)
  {sys.argv[0]} -d example.com --max-hosts 50     # Show 50 hosts per category
  {sys.argv[0]} -d example.com --max-hosts all    # Show ALL hosts
  {sys.argv[0]} -d example.com -o ./results       # Save to directory
  {sys.argv[0]} -d example.com --simple          # Simple mode (no tech detection)
        """
    )
    
    parser.add_argument("-d", "--domain", required=True, help="Target domain")
    parser.add_argument("-o", "--output", default=".", help="Output directory")
    parser.add_argument("--simple", action="store_true", help="Simple httpx mode")
    parser.add_argument("--timeout", type=int, default=600, help="Timeout in seconds")
    parser.add_argument("--max-hosts", type=str, default="25", help="Max hosts per category")
    parser.add_argument("--group-by-ip", action="store_true", help="Group by IP (not implemented)")
    
    args = parser.parse_args()
    
    # Parse max-hosts argument
    if args.max_hosts.lower() == "all":
        max_hosts = 999999
    else:
        try:
            max_hosts = int(args.max_hosts)
            if max_hosts < 1:
                raise ValueError
        except ValueError:
            print(f"{Colors.RED}[-] Invalid --max-hosts value. Use number or 'all'{Colors.RESET}")
            sys.exit(1)
    
    # Initialize output manager
    output = OutputManager(max_hosts=max_hosts, group_by_ip=args.group_by_ip)
    output.print_banner()
    
    # Check tools
    if not check_httpx_version():
        sys.exit(1)
    
    print(f"{Colors.BLUE}[*]{Colors.RESET} Target: {Colors.CYAN}{args.domain}{Colors.RESET}")
    print(f"{Colors.BLUE}[*]{Colors.RESET} Start: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"{Colors.BLUE}[*]{Colors.RESET} Max hosts per category: {max_hosts if max_hosts < 999999 else 'all'}")
    print()
    
    # Create temp files
    temp_dir = "/tmp" if os.path.exists("/tmp") else "."
    timestamp = int(time.time())
    subs_file = f"{temp_dir}/subs_{args.domain}_{timestamp}.txt"
    alive_file = f"{temp_dir}/alive_{args.domain}_{timestamp}.json"
    
    try:
        # Step 1: Run subfinder
        if not run_subfinder(args.domain, subs_file):
            print(f"{Colors.RED}[-]{Colors.RESET} Subfinder failed")
            sys.exit(1)
        
        # Step 2: Run httpx
        if not run_httpx(subs_file, alive_file, args.simple):
            print(f"{Colors.RED}[-]{Colors.RESET} httpx failed")
            sys.exit(1)
        
        # Step 3: Parse results
        results = parse_httpx_results(alive_file)
        if not results:
            print(f"{Colors.RED}[-]{Colors.RESET} No results found")
            sys.exit(1)
        
        print(f"{Colors.GREEN}[+]{Colors.RESET} Successfully processed {len(results)} results")
        print()
        
        # Step 4: Categorize results
        categorizer = ReconCategorizer()
        categorized, stats, interesting = categorizer.categorize_results(results)
        
        # Step 5: Display results (like first tool)
        output.display_quick_stats(stats)
        output.display_category_overview(categorized)
        output.display_categorized_results(categorized)
        output.display_interesting_finds(interesting)
        
        # Step 6: Save enhanced results
        save_enhanced_results(results, categorized, stats, interesting, args.domain, args.output)
        
        # Cleanup
        for temp_file in [subs_file, alive_file]:
            if os.path.exists(temp_file):
                try:
                    os.remove(temp_file)
                except:
                    pass
        
        # Final message
        print(f"\n{Colors.GREEN}{'='*70}")
        print(f"✅ SCAN COMPLETED SUCCESSFULLY!")
        print(f"📊 Total alive hosts: {len(results)}")
        print(f"⏱️  Finished: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"{'='*70}{Colors.RESET}")
        
    except KeyboardInterrupt:
        print(f"\n{Colors.YELLOW}[!] Scan interrupted{Colors.RESET}")
        sys.exit(0)
    except Exception as e:
        print(f"{Colors.RED}[-] Error: {str(e)}{Colors.RESET}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()