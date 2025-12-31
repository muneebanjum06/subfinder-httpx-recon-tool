# SubTTPX (Subfinder + HTTPx)

Automated reconnaissance tool combining **Subfinder** and **HTTPX** for offensive security engagements.
It discovers subdomains, checks live hosts, categorizes them by HTTP status, and highlights interesting findings like admin panels, API endpoints, and development servers.

---

## Features

* Discover subdomains using **Subfinder**
* Check alive hosts, HTTP status codes, titles, and tech stack via **HTTPX**
* Categorize hosts into:

  * Fully Operational
  * HTTPS Only
  * HTTP Only
  * Redirecting
  * Server Errors
  * Access Blocked
  * No Response
* Highlight interesting endpoints:

  * Admin panels (`/admin`, `/login`, `/dashboard`)
  * API endpoints (`/api`, `/v1`, `/graphql`)
  * Development servers (`:3000`, `:8080`, etc.)
* Generate **JSON** and **text reports**
* Configurable max hosts per category
* Colorful console output for quick insights

---

## Requirements

* Python 3.9+
* [Subfinder](https://github.com/projectdiscovery/subfinder)
* [HTTPX](https://github.com/projectdiscovery/httpx)

---

## Installation

1. Clone the repository:

```bash
git clone https://github.com/muneebanjum06/subfinder-httpx-recon-tool.git
cd subfinder-httpx-recon-tool
```

2. Install Subfinder and HTTPX:

```bash
go install -v github.com/projectdiscovery/subfinder/v2/cmd/subfinder@latest
go install -v github.com/projectdiscovery/httpx/cmd/httpx@latest
```

3. (Optional) If Python dependencies are added in the future:

```bash
pip install -r requirements.txt
```

---

## Usage

```bash
# Basic scan
python3 recon_tool.py -d example.com

# Save results in custom folder
python3 recon_tool.py -d example.com -o ./results

# Show all hosts per category
python3 recon_tool.py -d example.com --max-hosts all

# Simple HTTPX mode (faster, no tech detection)
python3 recon_tool.py -d example.com --simple
```

### Command-Line Options

| Option          | Description                                                 |
| --------------- | ----------------------------------------------------------- |
| `-d, --domain`  | Target domain (required)                                    |
| `-o, --output`  | Output directory (default: current folder)                  |
| `--simple`      | Simple HTTPX mode (no tech detection)                       |
| `--timeout`     | Timeout in seconds for Subfinder/HTTPX (default: 600)       |
| `--max-hosts`   | Maximum hosts per category (`number` or `all`, default: 25) |

---

## Example Output

![image](Examples/1.png)

![image](Examples/2.png)

![image](Examples/3.png)

![image](Examples/4.png)

---

## Folder Structure

```
subfinder-httpx-recon-tool/
│
├─ recon_tool.py          # Main Python script
├─ Example/               # Example output
├─ README.md              # Documentation
```

---

## Contributing

Pull requests are welcome! For major changes, please open an issue first.

* Add new interesting patterns or categories
* Improve output formatting
* Integrate additional reconnaissance tools

---

## License

This project is licensed under the **MIT License**. See [LICENSE](LICENSE) for details.

---

## Contact

Muneeb Anjum – [GitHub](https://github.com/muneebanjum06) – [muneebanjum370@gmail.com](mailto:muneebanjum370@gmail.com)
