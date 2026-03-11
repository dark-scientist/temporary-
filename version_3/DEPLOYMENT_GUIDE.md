# 🚀 Dotryder Voice RAG - Complete Deployment Guide

This guide will help you deploy the Dotryder Voice RAG System on any Linux server (Ubuntu/Debian recommended).

## 📋 System Requirements

### Minimum Requirements
- **OS**: RHEL 8+, CentOS 8+, Fedora 35+, or Rocky Linux 8+
- **RAM**: 8GB (16GB recommended)
- **Storage**: 20GB free space
- **CPU**: 4 cores (8 cores recommended)
- **Network**: Stable internet for initial setup

### Recommended Server Specs
- **VPS Providers**: Contabo, DigitalOcean, AWS, Hetzner
- **Instance Type**: 8GB RAM, 4 vCPU, 80GB SSD
- **Ports**: 8000 (API), 5173 (Frontend), 11434 (Ollama)

## 🛠️ Step 1: Initial Server Setup

### Update System
```bash
sudo dnf update -y
sudo dnf install -y curl wget git gcc gcc-c++ make python3 python3-pip python3-virtualenv nodejs npm ffmpeg
```

### Create User (if needed)
```bash
# Create deployment user
sudo adduser dotryder
sudo usermod -aG sudo dotryder
su - dotryder
```

## 🤖 Step 2: Install Ollama

### Install Ollama Server
```bash
# Install Ollama
curl -fsSL https://ollama.ai/install.sh | sh

# Start Ollama service
sudo systemctl enable ollama
sudo systemctl start ollama

# Verify installation
ollama --version
```

### Configure Ollama for Network Access
```bash
# Edit systemd service
sudo systemctl edit ollama

# Add these lines:
[Service]
Environment="OLLAMA_HOST=0.0.0.0:11434"
Environment="OLLAMA_ORIGINS=*"

# Restart service
sudo systemctl daemon-reload
sudo systemctl restart ollama
```

### Download Required Models
```bash
# Download models (this will take 10-15 minutes)
ollama pull llama3.2:3b          # Fast model (2GB)
ollama pull gemma3:4b            # Quality model (3.3GB)
ollama pull nomic-embed-text     # Embeddings (274MB)

# Verify models are installed
ollama list
```

## 📁 Step 3: Clone and Setup Project

### Clone Repository
```bash
cd ~
git clone https://github.com/dark-scientist/temporary-.git dotryder-rag
cd dotryder-rag
```

### Setup Python Environment
```bash
# Create virtual environment
python3 -m venv venv
source venv/bin/activate

# Install Python dependencies
pip install --upgrade pip
pip install -r requirements.txt
```

### Setup Node.js Frontend
```bash
# Install Node.js dependencies
cd frontend
npm install
cd ..
```

## 🔧 Step 4: Configuration

### Configure for Your Server
```bash
# Edit configuration file
nano src/config.py
```

Update these settings:
```python
# Server-optimized settings
USE_QUALITY_MODEL = False  # Use fast model by default
OLLAMA_URL = "http://localhost:11434"

# Voice settings (optional - disable if no audio needed)
ENABLE_STT = True   # Set to False if no microphone
ENABLE_TTS = True   # Set to False if no speakers needed
```

### Configure API for Production
```bash
# Edit API configuration
nano api.py
```

Update the uvicorn settings at the bottom:
```python
if __name__ == "__main__":
    uvicorn.run("api:app", host="0.0.0.0", port=8000, workers=1)
```

## 📊 Step 5: Build Document Index

### Add Your Documents (Optional)
```bash
# Replace default documents with your own
rm -f data/documents/*
cp /path/to/your/documents/*.pdf data/documents/

# Or keep the included Dotryder documents
ls data/documents/  # Should show 3 PDF files
```

### Build Vector Index
```bash
# This will take 5-10 minutes depending on document size
source venv/bin/activate
python build_index.py
```

Expected output:
```
✓ Found X document(s) in ./data/documents
✓ Ollama service is running
✓ Embedding model nomic-embed-text is available
✓ Vector store built and saved
✓ RAG system ready (XXX chunks indexed)
```

## 🚀 Step 6: Start Services

### Method 1: Manual Start (for testing)
```bash
# Terminal 1: Start API Backend
source venv/bin/activate
python api.py

# Terminal 2: Start Frontend (new terminal)
cd frontend
npm run dev -- --host 0.0.0.0
```

### Method 2: Production Deployment with PM2
```bash
# Install PM2
sudo npm install -g pm2

# Create ecosystem file
cat > ecosystem.config.js << 'EOF'
module.exports = {
  apps: [
    {
      name: 'dotryder-api',
      script: 'api.py',
      interpreter: './venv/bin/python',
      cwd: '/home/dotryder/dotryder-rag',
      env: {
        PYTHONPATH: '/home/dotryder/dotryder-rag'
      }
    },
    {
      name: 'dotryder-frontend',
      script: 'npm',
      args: 'run dev -- --host 0.0.0.0',
      cwd: '/home/dotryder/dotryder-rag/frontend'
    }
  ]
}
EOF

# Start services
pm2 start ecosystem.config.js
pm2 save
pm2 startup
```

## 🔒 Step 7: Configure Firewall

### Open Required Ports
```bash
# RHEL/CentOS/Fedora with firewalld
sudo firewall-cmd --permanent --add-port=22/tcp     # SSH
sudo firewall-cmd --permanent --add-port=8000/tcp   # API
sudo firewall-cmd --permanent --add-port=5173/tcp   # Frontend
sudo firewall-cmd --permanent --add-port=11434/tcp  # Ollama (optional)
sudo firewall-cmd --reload
```

### For Production: Use Nginx Reverse Proxy
```bash
# Install Nginx
sudo dnf install nginx

# Create config
sudo nano /etc/nginx/conf.d/dotryder.conf
```

Add this configuration:
```nginx
server {
    listen 80;
    server_name your-domain.com;  # Replace with your domain

    # Frontend
    location / {
        proxy_pass http://localhost:5173;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection 'upgrade';
        proxy_set_header Host $host;
        proxy_cache_bypass $http_upgrade;
    }

    # API
    location /api/ {
        proxy_pass http://localhost:8000/;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
    }
}
```

Enable the site:
```bash
sudo nginx -t
sudo systemctl enable nginx
sudo systemctl restart nginx
```

## 🧪 Step 8: Test Deployment

### Test API
```bash
# Health check
curl http://localhost:8000/health

# Test chat
curl -X POST http://localhost:8000/chat \
  -H "Content-Type: application/json" \
  -H "X-Username: test" \
  -d '{"message": "Hello, what can you tell me about the documents?"}'
```

### Test Frontend
Open browser and go to:
- **Local**: http://localhost:5173
- **Server**: http://your-server-ip:5173
- **With Nginx**: http://your-domain.com

### Login Credentials
| Username | Password | Role |
|----------|----------|------|
| prithwin | prithwin123 | User |
| kiran | kiran123 | User |
| admin | admin123 | Admin |

## 🔧 Step 9: Performance Optimization

### For Low-Resource Servers
Edit `src/llm.py` and reduce these values:
```python
"options": {
    "num_predict": 20,      # Shorter responses
    "num_thread": 2,        # Fewer threads
    "num_ctx": 64,          # Smaller context
    "keep_alive": "10m"     # Keep model loaded
}
```

### Monitor Resources
```bash
# Check system resources
htop

# Check Ollama models
ollama ps

# Check disk space
df -h

# Check service logs
pm2 logs
```

## 🐛 Troubleshooting

### Troubleshooting

### Server Performance Issues

If the system is slow or timing out on your server:

**1. Check Available Models**
```bash
ollama list
```

**2. Install Missing Models**
If you see timeout errors for fallback models, install them:
```bash
# Install lightweight fallback model (recommended for resource-constrained servers)
ollama pull tinyllama

# Or install the configured fallback
ollama pull smollm2:1.7b
```

**3. Resource-Constrained Servers**
For servers with limited RAM (< 8GB), use smaller models:
```bash
# Switch to tinyllama (1.1GB) instead of llama3.2:3b (2GB)
ollama pull tinyllama
```

Then update `version_3/src/config.py`:
```python
OLLAMA_MODEL = "tinyllama"  # Change from llama3.2:3b
```

**4. Model Loading Performance**
- Model loading takes 3-4 seconds on first request
- Subsequent requests are much faster (0.8s generation time)
- The system uses `keep_alive: 10m` to keep models hot

**5. Memory Usage**
- Ollama typically uses 5+ GB RAM for llama3.2:3b
- Use `htop` or `free -h` to monitor memory usage
- Consider smaller models if memory is limited

**6. Timeout Errors**
If you see "Read timed out" errors, the timeout has been increased to 300s in version_3.

### Common Issues

**1. Ollama not accessible**
```bash
# Check if Ollama is running
sudo systemctl status ollama

# Check if models are loaded
ollama ps

# Restart Ollama
sudo systemctl restart ollama
```

**2. API fails to start**
```bash
# Check Python dependencies
source venv/bin/activate
pip list

# Check for missing models
ollama list

# Check logs
python api.py
```

**3. Frontend won't load**
```bash
# Check Node.js version
node --version  # Should be 16+

# Reinstall dependencies
cd frontend
rm -rf node_modules package-lock.json
npm install
```

**4. System stops after "LLM client initialized"**
```bash
# This means RAG system failed to load - usually missing vector index
ls database/vector_store/  # Should show files

# If empty, build index first:
python build_index.py

# Then restart API:
python api.py
```

**5. "No documents found" error**
```bash
# Check documents folder
ls data/documents/  # Should show PDF files

# If empty, add documents:
cp /path/to/your/*.pdf data/documents/
python build_index.py
```

### Performance Issues
- **Slow first request**: Normal - model loading time
- **All requests slow**: Check server resources with `htop`
- **Out of memory**: Use smaller model or add swap space
- **High CPU**: Reduce `num_thread` in config

## 📊 Monitoring

### Check System Health
```bash
# API health
curl http://localhost:8000/health

# System stats
curl http://localhost:8000/stats

# PM2 status
pm2 status

# System resources
free -h && df -h
```

### Log Files
- **API logs**: `pm2 logs dotryder-api`
- **Frontend logs**: `pm2 logs dotryder-frontend`
- **Ollama logs**: `sudo journalctl -u ollama -f`
- **System logs**: `/var/log/syslog`

## 🔄 Updates and Maintenance

### Update Code
```bash
cd ~/dotryder-rag
git pull origin main
source venv/bin/activate
pip install -r requirements.txt
cd frontend && npm install && cd ..
pm2 restart all
```

### Update Models
```bash
ollama pull llama3.2:3b
ollama pull nomic-embed-text
pm2 restart dotryder-api
```

### Backup Data
```bash
# Backup database and documents
tar -czf dotryder-backup-$(date +%Y%m%d).tar.gz \
  data/documents/ logs/ database/
```

## 🎯 Production Checklist

- [ ] Server meets minimum requirements
- [ ] Ollama installed and running
- [ ] All models downloaded
- [ ] Python environment setup
- [ ] Node.js dependencies installed
- [ ] Document index built successfully
- [ ] API responds to health check
- [ ] Frontend loads in browser
- [ ] Login system works
- [ ] Chat functionality tested
- [ ] Firewall configured
- [ ] PM2 or systemd services running
- [ ] Nginx reverse proxy (optional)
- [ ] SSL certificate (for production)
- [ ] Monitoring setup
- [ ] Backup strategy in place

## 📞 Support

If you encounter issues:

1. **Check logs**: `pm2 logs` or service logs
2. **Verify requirements**: All dependencies installed
3. **Test components**: API, Ollama, Frontend separately
4. **Check resources**: RAM, CPU, disk space
5. **Review configuration**: Model names, ports, paths

## 🚀 Quick Start Summary

For experienced users, here's the rapid deployment:

```bash
# 1. Install dependencies
sudo dnf update -y && sudo dnf install -y curl git python3-virtualenv nodejs npm ffmpeg
curl -fsSL https://ollama.ai/install.sh | sh

# 2. Setup Ollama
sudo systemctl enable ollama && sudo systemctl start ollama
ollama pull llama3.2:3b && ollama pull nomic-embed-text

# 3. Clone and setup
git clone https://github.com/dark-scientist/temporary-.git dotryder-rag
cd dotryder-rag
python3 -m venv venv && source venv/bin/activate
pip install -r requirements.txt
cd frontend && npm install && cd ..

# 4. Build index and start
python build_index.py
python api.py &
cd frontend && npm run dev -- --host 0.0.0.0
```

Access at: http://your-server-ip:5173

---

**Happy Deploying! 🎉**

*This system provides a complete offline voice-enabled RAG solution with modern UI and enterprise features.*