# Deploy on AWS EC2 (Docker Compose + free HTTPS)

Running all three portfolio projects on one server? Use the combined guide in the
`aws-portfolio-deploy` repo instead. This page deploys **this project alone**.

## 0. Protect your wallet first
1. AWS Console → **Billing and Cost Management → Budgets → Create budget**.
2. Choose **Monthly cost budget**, amount e.g. **$10**, alert at 80% to your email.

## 1. Launch the server
1. **EC2 → Launch instance**
   - Name: `portfolio-server`
   - Image: **Ubuntu Server 24.04 LTS**
   - Type: **t3.small** (2 GB RAM; MySQL needs it. `t3.micro` works only with swap, see step 3)
   - Key pair: create one, download the `.pem` file
   - Storage: 20 GB gp3
2. **Network settings → Security group**, allow inbound:
   | Port | Source | Why |
   |---|---|---|
   | 22 | My IP | SSH |
   | 80 | Anywhere | HTTP (certificate check) |
   | 443 | Anywhere | HTTPS |
3. Launch. Then **Elastic IPs → Allocate → Associate** it with the instance, so the IP never changes.

## 2. Connect
```bash
chmod 400 portfolio-key.pem
ssh -i portfolio-key.pem ubuntu@YOUR_ELASTIC_IP
```

## 3. Install Docker (and swap for small instances)
```bash
curl -fsSL https://get.docker.com | sudo sh
sudo usermod -aG docker ubuntu && newgrp docker
# 2 GB swap: prevents MySQL crashing on small servers
sudo fallocate -l 2G /swapfile && sudo chmod 600 /swapfile
sudo mkswap /swapfile && sudo swapon /swapfile
echo '/swapfile none swap sw 0 0' | sudo tee -a /etc/fstab
```

## 4. Get the code and configure
```bash
git clone https://github.com/Ruba9099/WhatsApp-AI-Support-Agent.git
cd WhatsApp-AI-Support-Agent
cp .env.example .env
nano .env    # set strong passwords, ADMIN_API_KEY, LLM and WhatsApp values
```
Generate strong random values with `openssl rand -hex 24`.

## 5. Start it
```bash
docker compose up -d --build
docker compose ps            # both services "healthy"/"running"
curl localhost:8000/health   # {"status":"ok"}
```

## 6. Add free HTTPS with Caddy
No domain? Use **sslip.io**: IP `13.234.10.20` becomes `13-234-10-20.sslip.io` and
Caddy gets a real Let's Encrypt certificate for it automatically.

```bash
sudo apt install -y caddy
sudo tee /etc/caddy/Caddyfile >/dev/null <<'EOF'
13-234-10-20.sslip.io {
    reverse_proxy localhost:8000
}
EOF
sudo systemctl reload caddy
```
Replace the host with your IP (dashes) or your own domain. Open
`https://13-234-10-20.sslip.io/docs` and you'll see the API.

Now finish [WHATSAPP_SETUP.md](WHATSAPP_SETUP.md) with the URL `https://.../webhook`.

## 7. Updating after a new push
```bash
cd whatsapp-ai-support-agent && git pull && docker compose up -d --build
```

## Troubleshooting
| Symptom | Check |
|---|---|
| `api` keeps restarting | `docker compose logs api` – usually a wrong `.env` value |
| MySQL exits | Not enough RAM: add swap (step 3) or use t3.small |
| Caddy has no certificate | Ports 80/443 open in the security group? `sudo journalctl -u caddy` |
| Meta webhook verify fails | `WHATSAPP_VERIFY_TOKEN` must match exactly; restart after editing `.env` |
