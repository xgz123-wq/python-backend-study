#!/bin/bash
# ============================================================
# 生产部署脚本示例
# ============================================================
#
# 功能：
#   1. 服务器初始化（安装 Python、Nginx、Git）
#   2. 拉取代码、安装依赖
#   3. 配置 Gunicorn + systemd
#   4. 配置 Nginx 反向代理
#   5. 配置 HTTPS（Let's Encrypt）
#   6. 健康检查
#   7. 回滚机制
#
# 使用方法：
#   chmod +x deploy.sh
#   sudo ./deploy.sh
#
# 注意：此脚本仅供学习参考，实际使用前请修改下方配置变量
# ============================================================

set -euo pipefail  # 遇到错误立即退出，未定义变量报错

# ============================================================
# 配置变量（部署前必须修改）
# ============================================================

# 应用名称
APP_NAME="myapp"

# 部署用户（不要用 root）
APP_USER="www-data"

# 部署目录
APP_DIR="/opt/${APP_NAME}"

# Git 仓库地址
GIT_REPO="https://github.com/your-username/your-repo.git"

# Git 分支
GIT_BRANCH="main"

# 域名
DOMAIN="yourdomain.com"

# 管理员邮箱（Let's Encrypt 用于证书过期提醒）
ADMIN_EMAIL="admin@example.com"

# Gunicorn 监听端口
GUNICORN_PORT="8000"

# Python 版本
PYTHON_VERSION="3.11"

# 日志目录
LOG_DIR="/var/log/${APP_NAME}"

# ============================================================
# 颜色输出
# ============================================================

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

log_info() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

log_warn() {
    echo -e "${YELLOW}[WARN]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# ============================================================
# 检查 root 权限
# ============================================================

check_root() {
    if [ "$EUID" -ne 0 ]; then
        log_error "请使用 sudo 运行此脚本"
        exit 1
    fi
}

# ============================================================
# 步骤 1：服务器初始化
# ============================================================

server_init() {
    log_info "========== 步骤 1：服务器初始化 =========="

    # 更新系统包
    log_info "更新系统包..."
    apt update && apt upgrade -y

    # 安装基础工具
    log_info "安装基础工具..."
    apt install -y \
        curl \
        wget \
        git \
        build-essential \
        software-properties-common \
        ufw

    # 安装 Python
    log_info "安装 Python ${PYTHON_VERSION}..."
    add-apt-repository -y ppa:deadsnakes/ppa
    apt update
    apt install -y \
        python${PYTHON_VERSION} \
        python${PYTHON_VERSION}-venv \
        python${PYTHON_VERSION}-dev

    # 安装 Nginx
    log_info "安装 Nginx..."
    apt install -y nginx

    # 安装 Certbot（HTTPS 证书）
    log_info "安装 Certbot..."
    apt install -y certbot python3-certbot-nginx

    log_info "服务器初始化完成"
}

# ============================================================
# 步骤 2：配置防火墙
# ============================================================

setup_firewall() {
    log_info "========== 步骤 2：配置防火墙 =========="

    # 允许 SSH
    ufw allow ssh

    # 允许 HTTP 和 HTTPS
    ufw allow http
    ufw allow https

    # 启用防火墙
    ufw --force enable

    log_info "防火墙配置完成"
    ufw status
}

# ============================================================
# 步骤 3：拉取代码
# ============================================================

deploy_code() {
    log_info "========== 步骤 3：拉取代码 =========="

    # 创建部署目录
    if [ ! -d "$APP_DIR" ]; then
        mkdir -p "$APP_DIR"
    fi

    # 备份当前版本（用于回滚）
    if [ -d "${APP_DIR}/.git" ]; then
        log_info "备份当前版本..."
        PREVIOUS_COMMIT=$(cd "$APP_DIR" && git rev-parse HEAD)
        echo "$PREVIOUS_COMMIT" > "${APP_DIR}/.previous_commit"
    fi

    # 克隆或更新代码
    if [ ! -d "${APP_DIR}/.git" ]; then
        log_info "克隆代码..."
        git clone -b "$GIT_BRANCH" "$GIT_REPO" "$APP_DIR"
    else
        log_info "更新代码..."
        cd "$APP_DIR"
        git fetch origin
        git reset --hard "origin/${GIT_BRANCH}"
    fi

    log_info "代码部署完成"
}

# ============================================================
# 步骤 4：安装依赖
# ============================================================

install_dependencies() {
    log_info "========== 步骤 4：安装依赖 =========="

    cd "$APP_DIR"

    # 创建虚拟环境
    if [ ! -d "venv" ]; then
        log_info "创建虚拟环境..."
        python${PYTHON_VERSION} -m venv venv
    fi

    # 激活虚拟环境
    source venv/bin/activate

    # 升级 pip
    pip install --upgrade pip

    # 安装依赖
    log_info "安装 Python 依赖..."
    pip install -r requirements.txt

    # 安装生产依赖
    pip install gunicorn uvicorn[standard]

    deactivate

    log_info "依赖安装完成"
}

# ============================================================
# 步骤 5：配置 Gunicorn
# ============================================================

setup_gunicorn() {
    log_info "========== 步骤 5：配置 Gunicorn =========="

    cd "$APP_DIR"

    # 如果项目中没有 gunicorn_config.py，创建默认配置
    if [ ! -f "gunicorn_config.py" ]; then
        log_info "创建 Gunicorn 配置文件..."
        cat > gunicorn_config.py << 'GUNICORN_EOF'
# Gunicorn 生产配置
import multiprocessing

bind = "127.0.0.1:8000"
workers = multiprocessing.cpu_count() * 2 + 1
worker_class = "uvicorn.workers.UvicornWorker"
timeout = 120
graceful_timeout = 30
keepalive = 5
max_requests = 1000
max_requests_jitter = 50
accesslog = "-"
errorlog = "-"
loglevel = "info"
GUNICORN_EOF
    fi

    log_info "Gunicorn 配置完成"
}

# ============================================================
# 步骤 6：配置 systemd 服务
# ============================================================

setup_systemd() {
    log_info "========== 步骤 6：配置 systemd 服务 =========="

    # 创建日志目录
    mkdir -p "$LOG_DIR"
    chown "${APP_USER}:${APP_USER}" "$LOG_DIR"

    # 创建 systemd 服务文件
    cat > "/etc/systemd/system/${APP_NAME}.service" << SERVICE_EOF
[Unit]
Description=${APP_NAME} - FastAPI Application
After=network.target
Wants=network-online.target

[Service]
User=${APP_USER}
Group=${APP_USER}
WorkingDirectory=${APP_DIR}
EnvironmentFile=${APP_DIR}/.env
ExecStart=${APP_DIR}/venv/bin/gunicorn -c ${APP_DIR}/gunicorn_config.py app.main:app
Restart=always
RestartSec=5
TimeoutStopSec=30
PrivateTmp=true
ProtectSystem=strict
ProtectHome=true
NoNewPrivileges=true
StandardOutput=journal
StandardError=journal

[Install]
WantedBy=multi-user.target
SERVICE_EOF

    # 重新加载 systemd
    systemctl daemon-reload

    # 启用开机启动
    systemctl enable "${APP_NAME}"

    # 启动服务
    systemctl restart "${APP_NAME}"

    log_info "systemd 服务配置完成"
    systemctl status "${APP_NAME}" --no-pager
}

# ============================================================
# 步骤 7：配置 Nginx 反向代理
# ============================================================

setup_nginx() {
    log_info "========== 步骤 7：配置 Nginx 反向代理 =========="

    # 创建 Nginx 配置
    cat > "/etc/nginx/sites-available/${APP_NAME}" << NGINX_EOF
server {
    listen 80;
    server_name ${DOMAIN};

    # 静态文件（由 Nginx 直接返回，不经过 Python）
    location /static/ {
        alias ${APP_DIR}/static/;
        expires 30d;
        add_header Cache-Control "public, immutable";
    }

    # 上传文件
    location /media/ {
        alias ${APP_DIR}/media/;
        expires 7d;
    }

    # API 请求转发给 Gunicorn
    location / {
        proxy_pass http://127.0.0.1:${GUNICORN_PORT};
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
        proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto \$scheme;

        # WebSocket 支持
        proxy_http_version 1.1;
        proxy_set_header Upgrade \$http_upgrade;
        proxy_set_header Connection "upgrade";

        # 超时设置
        proxy_connect_timeout 60s;
        proxy_send_timeout 60s;
        proxy_read_timeout 60s;
    }
}
NGINX_EOF

    # 启用站点
    ln -sf "/etc/nginx/sites-available/${APP_NAME}" "/etc/nginx/sites-enabled/${APP_NAME}"

    # 删除默认站点
    rm -f /etc/nginx/sites-enabled/default

    # 测试配置
    nginx -t

    # 重启 Nginx
    systemctl restart nginx

    log_info "Nginx 配置完成"
}

# ============================================================
# 步骤 8：配置 HTTPS
# ============================================================

setup_https() {
    log_info "========== 步骤 8：配置 HTTPS =========="

    # 使用 Certbot 自动配置 HTTPS
    log_info "申请 Let's Encrypt 证书..."
    certbot --nginx -d "$DOMAIN" --non-interactive --agree-tos -m "$ADMIN_EMAIL"

    # 验证自动续期
    log_info "测试证书自动续期..."
    certbot renew --dry-run

    log_info "HTTPS 配置完成"
}

# ============================================================
# 步骤 9：健康检查
# ============================================================

health_check() {
    log_info "========== 步骤 9：健康检查 =========="

    # 等待服务启动
    sleep 3

    # 检查 systemd 服务状态
    if systemctl is-active --quiet "${APP_NAME}"; then
        log_info "✅ systemd 服务运行正常"
    else
        log_error "❌ systemd 服务未运行"
        systemctl status "${APP_NAME}" --no-pager
        return 1
    fi

    # 检查 Nginx 状态
    if systemctl is-active --quiet nginx; then
        log_info "✅ Nginx 运行正常"
    else
        log_error "❌ Nginx 未运行"
        return 1
    fi

    # 检查应用健康端点
    HTTP_CODE=$(curl -s -o /dev/null -w "%{http_code}" "http://127.0.0.1:${GUNICORN_PORT}/health" || echo "000")
    if [ "$HTTP_CODE" = "200" ]; then
        log_info "✅ 应用健康检查通过（HTTP ${HTTP_CODE}）"
    else
        log_warn "⚠️ 应用健康检查失败（HTTP ${HTTP_CODE}）"
        log_warn "请确保应用有 /health 端点"
    fi

    log_info "健康检查完成"
}

# ============================================================
# 回滚机制
# ============================================================

rollback() {
    log_warn "========== 开始回滚 =========="

    if [ -f "${APP_DIR}/.previous_commit" ]; then
        PREVIOUS_COMMIT=$(cat "${APP_DIR}/.previous_commit")
        log_info "回滚到版本：${PREVIOUS_COMMIT}"

        cd "$APP_DIR"
        git reset --hard "$PREVIOUS_COMMIT"

        # 重新安装依赖
        install_dependencies

        # 重启服务
        systemctl restart "${APP_NAME}"

        log_info "回滚完成"
    else
        log_error "没有可回滚的版本"
        exit 1
    fi
}

# ============================================================
# 主流程
# ============================================================

main() {
    log_info "=========================================="
    log_info "开始部署 ${APP_NAME}"
    log_info "=========================================="

    check_root

    # 执行部署步骤
    server_init
    setup_firewall
    deploy_code
    install_dependencies
    setup_gunicorn
    setup_systemd
    setup_nginx

    # 健康检查
    if health_check; then
        # 可选：配置 HTTPS（需要域名已解析到服务器）
        # setup_https

        log_info "=========================================="
        log_info "✅ 部署完成！"
        log_info "=========================================="
        log_info "应用地址：http://${DOMAIN}"
        log_info "服务状态：sudo systemctl status ${APP_NAME}"
        log_info "查看日志：sudo journalctl -u ${APP_NAME} -f"
    else
        log_error "=========================================="
        log_error "❌ 部署失败，开始回滚"
        log_error "=========================================="
        rollback
    fi
}

# 执行主流程
main "$@"
