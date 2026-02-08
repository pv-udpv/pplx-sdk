# Docker-based Self-Hosted GitHub Actions Runner

This directory contains configuration for running a self-hosted GitHub Actions runner using Docker.

## Overview

The self-hosted runner is based on [`myoung34/docker-github-actions-runner`](https://github.com/myoung34/docker-github-actions-runner) and runs in **ephemeral mode**, meaning the runner is automatically destroyed after completing each job for enhanced security.

## Prerequisites

- **Docker** (20.10 or later)
- **Docker Compose** (v2.0 or later)
- **Fine-Grained Personal Access Token (PAT)** with appropriate permissions

## Quick Start

### 1. Create GitHub Fine-Grained PAT

1. Go to https://github.com/settings/tokens?type=beta
2. Click "Generate new token"
3. Configure the token:
   - **Token name**: `pplx-sdk-self-hosted-runner`
   - **Repository access**: Select "Only select repositories" → Choose `pv-udpv/pplx-sdk`
   - **Repository permissions**:
     - `Administration`: **Read and write** (required for self-hosted runners)
     - `Actions`: **Read and write** (optional, for workflow management)
     - `Metadata`: **Read** (automatically included)
4. Click "Generate token" and copy the token (starts with `github_pat_`)

### 2. Configure Environment Variables

```bash
# Copy the example environment file
cp .env.example .env

# Edit .env and add your GitHub PAT
nano .env
```

Replace `github_pat_YOUR_FINE_GRAINED_PERSONAL_ACCESS_TOKEN_HERE` with your actual token.

### 3. Start the Runner

```bash
# From the runner/ directory
docker-compose up -d

# View logs
docker-compose logs -f

# Check runner status
docker-compose ps
```

### 4. Verify Runner Registration

1. Go to https://github.com/pv-udpv/pplx-sdk/settings/actions/runners
2. You should see a runner named `docker-runner-<hostname>` with status "Idle"
3. Labels: `self-hosted`, `linux`, `x64`, `docker`

## Using the Self-Hosted Runner in Workflows

### Option 1: Use Self-Hosted Runner Exclusively

Edit `.github/workflows/ci.yml`:

```yaml
jobs:
  test:
    runs-on: [self-hosted, linux, x64, docker]
    # ... rest of job configuration
```

### Option 2: Support Both GitHub-Hosted and Self-Hosted

```yaml
jobs:
  test:
    runs-on: ${{ matrix.runner }}
    strategy:
      matrix:
        runner: [ubuntu-latest, [self-hosted, linux, x64, docker]]
        python-version: ["3.12", "3.13"]
    # ... rest of job configuration
```

### Option 3: Use Self-Hosted for Specific Jobs

```yaml
jobs:
  test-github-hosted:
    runs-on: ubuntu-latest
    # ... runs on GitHub's infrastructure

  test-self-hosted:
    runs-on: [self-hosted, linux, x64, docker]
    # ... runs on your self-hosted runner
```

## Configuration

### Environment Variables

Edit `docker-compose.yml` or `.env` file:

| Variable | Default | Description |
|----------|---------|-------------|
| `GH_PAT` | (required) | GitHub Fine-Grained Personal Access Token |
| `REPO_URL` | https://github.com/pv-udpv/pplx-sdk | Repository URL |
| `RUNNER_NAME` | docker-runner-${HOSTNAME} | Runner name shown in GitHub |
| `LABELS` | self-hosted,linux,x64,docker | Runner labels for workflow targeting |
| `EPHEMERAL` | true | Destroy runner after each job (recommended) |
| `RUNNER_WORKDIR` | /tmp/runner/work | Work directory inside container |

### Resource Limits

**Note:** Docker Compose ignores `deploy.resources` limits in standard mode. These limits only apply when:
- Deploying to Docker Swarm, or
- Using `docker compose up --compatibility`

For standard Docker Compose, use `docker run` resource flags or Docker daemon limits instead.

Example `deploy.resources` configuration (commented out in `docker-compose.yml`):

```yaml
deploy:
  resources:
    limits:
      cpus: '2.0'      # Maximum CPU cores (Swarm/compatibility only)
      memory: 4G       # Maximum memory (Swarm/compatibility only)
    reservations:
      cpus: '1.0'      # Minimum CPU cores (Swarm/compatibility only)
      memory: 2G       # Minimum memory (Swarm/compatibility only)
```

## Management

### Stop the Runner

```bash
docker-compose down
```

### Restart the Runner

```bash
docker-compose restart
```

### View Logs

```bash
# Follow logs
docker-compose logs -f

# View last 100 lines
docker-compose logs --tail=100
```

### Update Runner Image

```bash
# Pull latest image
docker-compose pull

# Restart with new image
docker-compose up -d
```

### Remove Runner Completely

```bash
# Stop and remove containers, volumes
docker-compose down -v

# Remove runner work directory
rm -rf runner-tmp/
```

## Security Considerations

### ⚠️ Docker Socket Mount

The runner mounts `/var/run/docker.sock` to support Docker-in-Docker (DinD) workflows. This gives the container **root access to the host Docker daemon**.

**Security implications:**
- Container can create/modify/delete any Docker resource on the host
- Potential for container escape attacks
- Suitable for trusted repositories and workflows

**Mitigation options:**
1. **Use Ephemeral Mode** (already enabled) - Runner is destroyed after each job
2. **Network isolation** - Run on a dedicated host or VM
3. **Use sysbox runtime** - Provides better container isolation:
   ```yaml
   # In docker-compose.yml, add to the service:
   runtime: sysbox-runc
   ```
   Then run: `docker compose up -d`
   
   Install sysbox: https://github.com/nestybox/sysbox
4. **GitHub App Authentication** - Auto-rotating tokens (production recommended)

### 🔐 Ephemeral Mode

**Enabled by default** (`EPHEMERAL=true`). Benefits:
- Runner is deleted from GitHub after completing each job
- Fresh environment for every workflow run
- Reduces risk of persistent compromises
- Prevents stale runners accumulating

### 🔑 Token Security

- **Never commit `.env` file** - Already in `.gitignore`
- **Use Fine-Grained PATs** - Limit scope to specific repository
- **Rotate tokens regularly** - GitHub recommends 90-day rotation
- **Consider GitHub App auth** for production - Provides auto-rotating tokens

### 🛡️ Additional Recommendations

1. **Restrict repository access** - Use private repositories when possible
2. **Review workflow permissions** - Use `permissions:` in workflows
3. **Enable branch protection** - Require reviews for workflow changes
4. **Monitor runner activity** - Check https://github.com/pv-udpv/pplx-sdk/settings/actions/runners
5. **Use secrets for sensitive data** - Never hardcode credentials in workflows

## Troubleshooting

### Runner Not Appearing in GitHub

1. Check logs: `docker-compose logs`
2. Verify `GH_PAT` has correct permissions
3. Ensure token hasn't expired
4. Check repository URL is correct

### Runner Shows "Offline"

1. Check container status: `docker-compose ps`
2. Restart runner: `docker-compose restart`
3. Check Docker daemon is running: `docker info`

### Jobs Not Running on Self-Hosted Runner

1. Verify workflow uses correct labels: `runs-on: [self-hosted, linux, x64, docker]`
2. Check runner is "Idle" in GitHub settings
3. Ensure runner container is running: `docker-compose ps`

### Permission Denied Errors

1. Verify Docker socket permissions: `ls -l /var/run/docker.sock`
2. Add user to docker group: `sudo usermod -aG docker $USER`
3. Restart Docker daemon

### Container Won't Start

1. Check port conflicts: `docker ps -a`
2. Verify Docker Compose version: `docker-compose --version` (need v2.0+)
3. Check environment variables: `docker-compose config`

## Advanced Configuration

### Multiple Runners

To run multiple runners for parallel jobs, create separate compose files or use Docker run commands:

**Option 1: Multiple compose files**
```bash
# Copy docker-compose.yml for each runner
cp docker-compose.yml docker-compose-runner2.yml
# Edit RUNNER_NAME in each file to be unique
# Start each separately
docker compose -f docker-compose.yml up -d
docker compose -f docker-compose-runner2.yml up -d
```

**Option 2: Docker run commands**
```bash
docker run -d --name runner1 \
  -e REPO_URL=https://github.com/pv-udpv/pplx-sdk \
  -e ACCESS_TOKEN=${GH_PAT} \
  -e RUNNER_NAME=docker-runner-1 \
  -e EPHEMERAL=true \
  -e LABELS=self-hosted,linux,x64,docker \
  -v /var/run/docker.sock:/var/run/docker.sock \
  myoung34/github-runner:2.321.0
```

Note: Each runner must have a unique `RUNNER_NAME`.

### Custom Labels

Edit `docker-compose.yml`:

```yaml
LABELS: self-hosted,linux,x64,docker,python,pytest,custom-label
```

Then use in workflows:

```yaml
runs-on: [self-hosted, custom-label]
```

### GitHub App Authentication (Production)

For production use, consider GitHub App authentication:

1. Create GitHub App: https://github.com/settings/apps/new
2. Install app on repository
3. Update `docker-compose.yml`:
   ```yaml
   environment:
     APP_ID: ${GITHUB_APP_ID}
     APP_PRIVATE_KEY: ${GITHUB_APP_PRIVATE_KEY}
     # Remove ACCESS_TOKEN
   ```

See: https://github.com/myoung34/docker-github-actions-runner#usage-with-github-app

## Resources

- [myoung34/docker-github-actions-runner Documentation](https://github.com/myoung34/docker-github-actions-runner)
- [GitHub Self-Hosted Runners](https://docs.github.com/en/actions/hosting-your-own-runners)
- [Fine-Grained Personal Access Tokens](https://docs.github.com/en/authentication/keeping-your-account-and-data-secure/managing-your-personal-access-tokens#creating-a-fine-grained-personal-access-token)
- [GitHub Actions Security](https://docs.github.com/en/actions/security-guides/security-hardening-for-github-actions)

## Support

For issues specific to:
- **pplx-sdk**: Open issue at https://github.com/pv-udpv/pplx-sdk/issues
- **Docker runner image**: https://github.com/myoung34/docker-github-actions-runner/issues
- **GitHub Actions**: https://github.com/actions/runner/issues
