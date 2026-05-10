# Cracktify Server — AWS Deployment Guide

A step-by-step guide for deploying the Cracktify API (FastAPI) on an AWS EC2 instance using Docker and GitHub Container Registry (GHCR). The CI/CD pipeline automates this on every push to `main`, but this guide covers the full manual setup and prerequisites.

---

## Prerequisites

Before deploying, make sure you have the following ready:

- An **AWS account** with EC2 access
- A **GitHub repository** with this server code
- An **AWS Secrets Manager** secret configured (see Step 2)
- A **Cloudinary account** for image storage
- A **Gmail API** project with credentials and a refresh token

---

## Step 1 — Launch an EC2 Instance

1. Go to the [AWS EC2 Console](https://console.aws.amazon.com/ec2) and click **Launch Instance**.
2. Choose an AMI — **Amazon Linux 2023** is recommended.
3. Select an instance type — `t3.small` or higher is recommended.
4. Configure a **Security Group** with the following inbound rules:

   | Type       | Protocol | Port | Source              |
   |------------|----------|------|---------------------|
   | SSH        | TCP      | 22   | Your IP             |
   | Custom TCP | TCP      | 8000 | `cracktify-alb-sg`  |

   > Port `8000` must only be open to the ALB security group — **not** `0.0.0.0/0`. This ensures traffic always flows through the ALB and cannot bypass it directly via the EC2 public IP.

5. Create or select an existing **key pair** (`.pem`) — you'll need this to SSH in.
6. Launch the instance and note the **Public IPv4 address**.
7. Make sure the instance is in **`ap-southeast-1c`** (or whichever AZ your ALB covers — they must match).

---

## Step 2 — Configure AWS Secrets Manager

The server loads all credentials from AWS Secrets Manager via `get_secret()`. Create a secret with the following keys:

| Key                     | Description                                          |
|-------------------------|------------------------------------------------------|
| `SQLHOST`               | PostgreSQL host (e.g., RDS endpoint)                 |
| `SQLUSER`               | PostgreSQL username                                  |
| `SQLPASSWORD`           | PostgreSQL password                                  |
| `SQLDATABASE`           | PostgreSQL database name                             |
| `SQLPORT`               | PostgreSQL port (default: `5432`)                    |
| `ADMIN_USER`            | Your admin username                                  |
| `ADMIN_EMAIL`           | Your admin email address                             |
| `ADMIN_PASSWORD`        | Your hashed password (generated in `utils/password.py`) |
| `JWT_SECRET_KEY`        | Secret key for signing JWT tokens                    |
| `GMAIL_CREDENTIALS`     | Base64-encoded Gmail API `credentials.json`          |
| `GMAIL_TOKEN`           | Base64-encoded Gmail API `token.json`                |
| `CLOUDINARY_CLOUD_NAME` | Your Cloudinary cloud name                           |
| `CLOUDINARY_API_KEY`    | Your Cloudinary API key                              |
| `CLOUDINARY_SECRET_KEY` | Your Cloudinary secret key                           |

To base64-encode your Gmail files:
```bash
base64 -w 0 credentials.json
base64 -w 0 token.json
```

In the AWS Console, go to **Secrets Manager → Store a new secret → Other type of secret**, then add the key-value pairs above.

> The EC2 instance must have an **IAM Role** with `secretsmanager:GetSecretValue` permission attached.

---

## Step 3 — Set Up the EC2 Instance

SSH into your instance:
```bash
ssh -i your-key.pem ec2-user@<EC2_PUBLIC_IP>
```

Install Docker:
```bash
sudo yum update -y
sudo yum install -y docker
sudo systemctl start docker
sudo systemctl enable docker
sudo usermod -aG docker ec2-user
```

Log out and back in to apply the Docker group, then verify:
```bash
exit
ssh -i your-key.pem ec2-user@<EC2_PUBLIC_IP>
docker --version
```

---

## Step 4 — Set Up the Application Load Balancer (ALB)

The ALB sits in front of your EC2, provides a stable DNS endpoint, and handles health checks automatically.

### 4.1 — Create a Security Group for the ALB

1. Go to **EC2 → Security Groups → Create security group**
2. Fill in:
   - **Name** → `cracktify-alb-sg`
   - **VPC** → same VPC as your EC2
3. Add **Inbound rule**:

   | Type | Protocol | Port | Source    |
   |------|----------|------|-----------|
   | HTTP | TCP      | 80   | 0.0.0.0/0 |

4. **Outbound rules** → leave as `All traffic 0.0.0.0/0`
5. Click **Create security group**

### 4.2 — Create a Target Group

1. Go to **EC2 → Target Groups → Create target group**
2. Fill in:
   - **Target type** → `Instances`
   - **Name** → `cracktify-tg`
   - **Protocol** → `HTTP`
   - **Port** → `8000`
   - **VPC** → same VPC as your EC2
3. Under **Health checks**:
   - **Protocol** → `HTTP`
   - **Path** → `/`
   - **Port** → Override → `8000`
   - **Healthy threshold** → `2`
   - **Unhealthy threshold** → `2`
   - **Timeout** → `5`
   - **Interval** → `10`
4. Click **Next** → select your EC2 instance → set port to `8000` → **Include as pending** → **Create target group**

### 4.3 — Create the Load Balancer

1. Go to **EC2 → Load Balancers → Create Load Balancer → Application Load Balancer**
2. Fill in:
   - **Name** → `cracktify-alb`
   - **Scheme** → `Internet-facing`
   - **IP address type** → `IPv4`
3. Under **Network mapping**:
   - **VPC** → same VPC as your EC2
   - **Availability Zones** → select **all AZs** including the one your EC2 is in (e.g. `ap-southeast-1c`)
4. Under **Security groups** → remove default → attach `cracktify-alb-sg`
5. Under **Listeners** → `HTTP:80` → Forward to `cracktify-tg`
6. Click **Create load balancer**

### 4.4 — Lock Down EC2 Security Group

Once the ALB is running, prevent direct access to your EC2 on port `8000`:

1. Go to **EC2 → Security Groups → your EC2's SG → Edit inbound rules**
2. **Delete** any rule with port `8000` and source `0.0.0.0/0`
3. **Add a new rule**:

   | Type       | Protocol | Port | Source             |
   |------------|----------|------|--------------------|
   | Custom TCP | TCP      | 8000 | `cracktify-alb-sg` |

4. Click **Save rules**

> Always delete the old `0.0.0.0/0` rule first and add a new SG-based rule — you cannot edit a CIDR rule into a security group reference rule directly.

---

## Step 5 — Configure GitHub Secrets

Go to your GitHub repository → **Settings → Secrets and variables → Actions** and add:

| Secret Name   | Value                                    |
|---------------|------------------------------------------|
| `EC2_HOST`    | Public IPv4 address of your EC2 instance |
| `EC2_SSH_KEY` | Full contents of your `.pem` key file    |

> `GITHUB_TOKEN` is automatically provided by GitHub Actions — no need to add it manually.

---

## Step 6 — Deploy via CI/CD (Automatic)

Push to the `main` branch to trigger the pipeline:
```bash
git add .
git commit -m "deploy: your message"
git push origin main
```

The workflow in `.github/workflows/ci.yml` will run three jobs in sequence:

1. **check-code** — Installs dependencies and runs `python -m compileall` to catch syntax errors.
2. **build-docker** — Builds the Docker image (no cache) and pushes it to GHCR as `ghcr.io/<your-repo>:latest`.
3. **deploy** — SSHs into the EC2 instance, pulls the new image, removes the old container, and starts a fresh one on port `8000`.

Monitor progress under the **Actions** tab in your GitHub repository.

---

## Step 7 — Manual Deployment (Optional)

To deploy manually on the EC2 instance:
```bash
# Log in to GitHub Container Registry
docker login ghcr.io -u <github-username> -p <github-personal-access-token>

# Pull the latest image
docker pull ghcr.io/<github-org>/<repo-name>:latest

# Remove the old container (if any)
docker rm -f fastapi || true

# Start the new container
docker run -d \
  --name fastapi \
  --restart always \
  -p 8000:8000 \
  ghcr.io/<github-org>/<repo-name>:latest
```

---

## Step 8 — Verify the Deployment

**Check via ALB DNS (correct way):**
```bash
curl http://<ALB_DNS_NAME>/
```

Expected response:
```json
{ "message": "Connected to Cracktify API!" }
```

Interactive API docs:
```
http://<ALB_DNS_NAME>/docs
```

**Check Target Group health:**

Go to **EC2 → Target Groups → cracktify-tg → Targets tab** — your EC2 should show as `healthy`.

> ⚠️ Do **not** use the EC2 public IP directly (`http://<EC2_IP>:8000`). Port `8000` is locked to the ALB only — direct access will time out. Always use the ALB DNS name.

---

## Useful Docker Commands

```bash
docker ps                  # List running containers
docker logs fastapi        # View container logs
docker restart fastapi     # Restart the container
docker stop fastapi        # Stop the container
docker rm -f fastapi       # Remove the container
```

---

## Architecture Overview

```
GitHub (push to main)
         |
         v
 GitHub Actions CI/CD
   |
   |-- [1] check-code
   |       - actions/setup-python@v5 (Python 3.13)
   |       - pip install -r requirements.txt
   |       - python -m compileall .
   |
   |-- [2] build-docker  (needs: check-code)
   |       - docker/login-action → ghcr.io
   |       - docker build --no-cache
   |       - docker push → ghcr.io/<repo>:latest
   |
   `-- [3] deploy  (needs: build-docker)
           - appleboy/ssh-action → EC2
           - docker pull ghcr.io/<repo>:latest
           - docker rm -f fastapi
           - docker run -d --name fastapi -p 8000:8000
                    |
                    v
         Internet Gateway (AWS VPC)
                    |
                    v
       Application Load Balancer (:80)
       cracktify-alb-sg (inbound: 80)
                    |
                    v
             EC2 Instance (:8000)
             Docker container: fastapi
             cracktify-ec2-sg (inbound: 8000 from ALB only)
                    |
                    v
          FastAPI — Cracktify API v2.0.0
          |
          |-- /auth          Authentication routes
          |-- /otp           OTP routes
          |-- /profile       Profile routes
          |-- /cracks        Crack detection routes
          |-- /upload        Upload routes
          |-- /notifications Notification routes
          |-- /engineers     Engineer routes
          |-- /admin         Admin routes
          `-- /ws            WebSocket routes
                    |
          .---------+-----------.-----------.
          |                     |           |
          v                     v           v
   PostgreSQL (RDS)     Cloudinary      Gmail API
   SSL connection       Image storage   OTP / email
   (psycopg2)
          |
          v
   AWS Secrets Manager
   (credentials injected
    at runtime via get_secret())
```

---

## API Routes Reference

| Prefix           | Tag           | Description                              |
|------------------|---------------|------------------------------------------|
| `/auth`          | Auth          | Register, login, token refresh           |
| `/otp`           | OTP           | Send and verify one-time passwords       |
| `/profile`       | Profile       | View and update user profile             |
| `/cracks`        | Cracks        | Submit and retrieve crack detections     |
| `/upload`        | Uploads       | Upload images to Cloudinary              |
| `/notifications` | Notifications | Push notification management             |
| `/engineers`     | Engineers     | Engineer listing and assignment          |
| `/admin`         | Admin         | Admin-only management endpoints          |
| `/ws`            | WebSocket     | Real-time WebSocket connections          |

---

## Troubleshooting

**Container exits immediately after starting**
```bash
docker logs fastapi
```
Check for missing secrets — the most common cause is a key in AWS Secrets Manager that is misspelled or missing entirely.

**504 Gateway Timeout on ALB DNS**
- Port `8000` on EC2 SG is not open to the ALB SG — go to EC2 SG inbound rules, delete the old `0.0.0.0/0` rule and add a new rule with source set to `cracktify-alb-sg`.
- Target Group is unhealthy — check **EC2 → Target Groups → cracktify-tg → Targets tab**.
- EC2 is in a different AZ than the ALB — go to **EC2 → Load Balancers → cracktify-alb → Actions → Edit subnets** and add the AZ your EC2 is in.

**Target Group shows `unused`**
- Your EC2 is not registered — go to **Target Groups → cracktify-tg → Register targets**, select your instance and set port to `8000`.
- AZ mismatch — your EC2's AZ must be included in the ALB's network mapping.

**Target Group shows `unhealthy`**
- Health check port is wrong — go to **Target Groups → Health checks → Edit** and set Port to Override `8000`.
- Docker container is not running — SSH in and run `docker ps`, then `docker logs fastapi`.

**Cannot edit port 8000 source from `0.0.0.0/0` to ALB SG**
- You cannot convert a CIDR rule to a SG reference rule by editing — you must **delete** the existing rule and **add a new one** with the ALB SG as source.

**Direct EC2 IP access times out**
- This is expected and correct after locking down port `8000` to ALB only. Always use the ALB DNS name instead.

**GitHub Actions deploy job fails at SSH step**
- Verify `EC2_HOST` has no extra spaces or newlines.
- Verify `EC2_SSH_KEY` contains the full `.pem` content including the `-----BEGIN RSA PRIVATE KEY-----` header and footer.
- Ensure port `22` is open in the EC2 Security Group.

**`secretsmanager:GetSecretValue` access denied**
- Go to **EC2 → Instances → Your Instance → Actions → Security → Modify IAM Role**.
- Attach a role that includes `secretsmanager:GetSecretValue` permission for your secret's ARN.

**Database connection refused**
- Confirm the RDS Security Group allows inbound TCP on port `5432` from the EC2 Security Group.
- Confirm `SQLHOST`, `SQLUSER`, `SQLPASSWORD`, and `SQLDATABASE` are correct in Secrets Manager.
- The connection uses `sslmode=require` — ensure your RDS instance has SSL enabled.
README
echo "done"