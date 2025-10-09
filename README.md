# Product Market Research - Monorepo CI/CD Setup

## 🏗️ Architecture

- **Backend**: FastAPI + Celery on EC2 with Docker
- **Frontend**: React app on S3 + CloudFront
- **Container Registry**: GitHub Container Registry (GHCR) - FREE!
- **Structure**: Monorepo with separate CI/CD pipelines

## 🚀 Quick Setup

### 1. Backend (EC2 + Docker)

**EC2 Setup (One-time):**
```bash
# Install Docker & Docker Compose
curl -fsSL https://get.docker.com -o get-docker.sh && sudo sh get-docker.sh
sudo curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
sudo chmod +x /usr/local/bin/docker-compose
```

**Copy files to EC2:**
- `backend/docker-compose.prod.yml`
- `backend/nginx.conf` 
- `backend/.env.prod` (create from template)

**GitHub Secrets:**
- `EC2_HOST` - Your EC2 IP
- `EC2_USERNAME` - ubuntu
- `EC2_SSH_KEY` - Your SSH private key

### 2. Frontend (S3 + CloudFront)

**GitHub Secrets:**
- `AWS_ACCESS_KEY_ID`
- `AWS_SECRET_ACCESS_KEY`
- `REACT_APP_API_URL` - Your backend API URL

**S3 Setup:**
```bash
# Create S3 bucket
aws s3 mb s3://product-market-research-frontend

# Configure for static hosting
aws s3 website s3://product-market-research-frontend --index-document index.html --error-document index.html
```

## 🔄 Deployment

- **Backend**: Push changes to `backend/` → GitHub Actions builds Docker image → Pushes to GHCR → Deploys to EC2
- **Frontend**: Push changes to `frontend/` → GitHub Actions builds React app → Deploys to S3 → Invalidates CloudFront

## 📁 Monorepo Structure

```
product-market-research/
├── backend/
│   ├── .github/workflows/deploy.yml    # Backend CI/CD
│   ├── docker-compose.prod.yml         # Docker configuration
│   ├── nginx.conf                      # Nginx reverse proxy
│   └── env.prod.template              # Environment variables
├── frontend/
│   └── .github/workflows/deploy.yml   # Frontend CI/CD
└── README.md
```

## 🎯 Key Benefits

- **Separate CI/CD**: Backend and frontend deploy independently
- **Path-based triggers**: Only relevant workflows run
- **Single repository**: Easier to manage
- **Free GHCR**: No AWS ECR costs

That's it! 🎉
