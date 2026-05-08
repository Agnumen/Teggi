# 🤖 Teggi

> **Teggi** — a modern self-hosted chatbot for managing daily rhythms.  
> Deployable via Docker Compose in one command, perfect for local development and isolated environments.

[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](https://opensource.org/licenses/MIT)
[![Docker](https://img.shields.io/badge/Docker-✓-2496ED?logo=docker)](https://www.docker.com/)
[![Status](https://img.shields.io/badge/Status-Active-success)](https://github.com/Agnumen/Teggi)

---

## ✨ Features

- 🐳 **Docker-based deployment** — full dependency isolation
- 🚀 **One-command startup** — launch the project with a single command
- 🔄 **Automatic rebuilds** — containers rebuild automatically on changes
- 🛠️ **Easy local development** — streamlined setup for developers
- 🔒 **Environment isolation** — safe configuration separation
- ⚙️ **Simple infrastructure** — minimal and clear microservice architecture

---

## 🛠️ Tech Stack

| Technology | Purpose |
|-----------|---------|
| **Docker** | Application containerization |
| **Docker Compose** | Multi-container orchestration |

---

## 🚀 Quick Start

### Requirements

Make sure you have installed:

- [Docker](https://docs.docker.com/get-docker/) ≥ 20.10
- [Docker Compose](https://docs.docker.com/compose/install/) ≥ v2

Verify installation:
```bash
docker --version
docker compose version
```

### Installation

1. Clone the repository:
```bash
git clone https://github.com/Agnumen/Teggi.git
cd Teggi
```

2. Start the application:
```bash
docker compose up -d --build
```

✅ The application will build images and start containers in detached mode.
---

## ⚡ Useful Commands

| Action | Command |
|--------|---------|
| 🟢 Start containers | `docker compose up -d` |
| 🔄 Rebuild and restart | `docker compose up -d --build` |
| 🔴 Stop containers | `docker compose down` |
| 📋 View logs (follow) | `docker compose logs -f` |
| ♻️ Restart services | `docker compose restart` |
| 🗑️ Full cleanup (with volumes) | `docker compose down -v` |

---

## 💻 Development

### Rebuild after code changes
```bash
docker compose up -d --build
```

### List running containers
```bash
docker ps
```

### Access container terminal
```bash
docker compose exec <service_name> sh
# or for bash:
docker compose exec <service_name> bash
```

---

## 📁 Project Structure

```
Teggi/
├── docker-compose.yml    # Orchestration configuration
├── Dockerfile            # Image build instructions
├── .env.example          # Environment variables template
├── .gitignore            # Git exclusions
└── ...                   # Application source code
```

---

## ⚙️ Environment Variables

Create a `.env` file in the project root based on `.env.example`:

```env
# Example configuration
APP_PORT=8000
DEBUG=false
# Add other variables as needed
```

> 💡 Docker Compose automatically loads variables from `.env`.

---

## 🔧 Troubleshooting

### ❌ Containers won't start
```bash
# Check logs
docker compose logs

# Check container status
docker compose ps
```

### 🔌 Port already in use
```bash
# Find process using the port (Linux/macOS)
sudo lsof -i :<PORT>

# Or change the port in docker-compose.yml:
# ports:
#   - "8080:80"  # host:container
```

### 🧹 Full rebuild from scratch
```bash
docker compose down -v
docker compose build --no-cache
docker compose up -d
```

---

## 🔄 Updating

```bash
git pull origin main
docker compose up -d --build
```

---

## 🤝 Contributing

Pull requests are welcome! 🎉

1. Fork the repository
2. Create a feature branch: `git checkout -b feature/amazing-feature`
3. Commit changes: `git commit -m 'Add: amazing feature'`
4. Push to branch: `git push origin feature/amazing-feature`
5. Open a Pull Request

🐞 Found a bug? [Open an Issue](https://github.com/Agnumen/Teggi/issues) with a detailed description.

---

## 📜 License

This project is licensed under the **MIT License**.  
See the [LICENSE](LICENSE) file for details.

---

## 📬 Contact

- **Author**: Armen [@Agnumen](https://github.com/Agnumen)
- **Repository**: [github.com/Agnumen/Teggi](https://github.com/Agnumen/Teggi)
- **Issues & Suggestions**: [Issues](https://github.com/Agnumen/Teggi/issues)

---

> 💡 *Teggi helps teenagers build a healthy digital rhythm. If you find it useful, please give it a ⭐️!*
