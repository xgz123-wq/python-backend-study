#!/usr/bin/env bash
# ============================================================================
# 部署脚本示例：Python 后端服务自动化部署
# ============================================================================
# 功能：拉取最新代码 → 安装依赖 → 运行测试 → 构建 Docker 镜像 → 启动服务
#       → 健康检查 → 失败自动回滚
#
# 用法：
#   chmod +x deploy.sh
#   ./deploy.sh                    # 正常部署
#   ./deploy.sh --rollback         # 手动回滚到上一版本
#   ./deploy.sh --skip-tests       # 跳过测试（不推荐，仅用于紧急修复）
#
# 前置条件：
#   - 服务器已安装 Docker 和 Docker Compose
#   - 已配置好 Git 仓库访问权限
#   - .env 文件已准备好（包含数据库连接、密钥等）
# ============================================================================

set -euo pipefail
# set -e: 任何命令失败立即退出（不要继续执行后续步骤）
# set -u: 引用未定义变量时报错退出
# set -o pipefail: 管道中任一命令失败则整个管道失败

# ========================= 配置区域 =========================

# 项目配置
APP_NAME="my-python-backend"           # 应用名称
APP_DIR="/opt/app"                     # 应用部署目录
GIT_BRANCH="main"                      # 部署的 Git 分支
DOCKER_COMPOSE_FILE="docker-compose.yml" # Docker Compose 配置文件

# 健康检查配置
HEALTH_URL="http://localhost:8000/health"  # 健康检查 URL
HEALTH_RETRIES=10                         # 健康检查重试次数
HEALTH_INTERVAL=5                         # 每次重试间隔（秒）

# 回滚配置
MAX_BACKUP_IMAGES=3                     # 保留最近的镜像数量

# 日志颜色
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# ========================= 工具函数 =========================

# 打印带时间戳的日志
log_info() {
    echo -e "${BLUE}[INFO]${NC} $(date '+%Y-%m-%d %H:%M:%S') $*"
}

log_success() {
    echo -e "${GREEN}[OK]${NC} $(date '+%Y-%m-%d %H:%M:%S') $*"
}

log_warn() {
    echo -e "${YELLOW}[WARN]${NC} $(date '+%Y-%m-%d %H:%M:%S') $*"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $(date '+%Y-%m-%d %H:%M:%S') $*"
}

# 记录当前部署信息（用于回滚）
save_deploy_info() {
    local image_tag="$1"
    local commit_sha="$2"
    # 将当前部署信息写入文件，回滚时读取
    cat > "${APP_DIR}/.deploy_info" <<EOF
IMAGE_TAG=${image_tag}
COMMIT_SHA=${commit_sha}
DEPLOY_TIME=$(date '+%Y-%m-%d %H:%M:%S')
EOF
    log_info "部署信息已保存: image_tag=${image_tag}, commit=${commit_sha}"
}

# 读取上一次部署信息
read_prev_deploy_info() {
    if [[ -f "${APP_DIR}/.deploy_info" ]]; then
        # source 会加载文件中的变量到当前 shell
        source "${APP_DIR}/.deploy_info"
        echo "${IMAGE_TAG}"
    else
        echo ""
    fi
}

# ========================= 回滚函数 =========================

rollback() {
    log_warn "========== 开始回滚 =========="

    local prev_tag
    prev_tag=$(read_prev_deploy_info)

    if [[ -z "${prev_tag}" ]]; then
        log_error "未找到上一次部署信息，无法回滚"
        log_error "请手动指定镜像标签: docker compose up -d --no-deps <service> <tag>"
        exit 1
    fi

    log_info "回滚到镜像标签: ${prev_tag}"

    # 停止当前服务
    log_info "停止当前服务..."
    cd "${APP_DIR}"
    docker compose -f "${DOCKER_COMPOSE_FILE}" down --timeout 30

    # 使用上一个镜像标签启动服务
    log_info "使用旧镜像启动服务..."
    IMAGE_TAG="${prev_tag}" docker compose -f "${DOCKER_COMPOSE_FILE}" up -d

    # 验证回滚是否成功
    log_info "验证回滚后的服务状态..."
    if health_check; then
        log_success "回滚成功！服务已恢复"
    else
        log_error "回滚后健康检查仍然失败，请人工介入！"
        log_error "检查日志: docker compose -f ${DOCKER_COMPOSE_FILE} logs"
        exit 1
    fi
}

# ========================= 健康检查函数 =========================

health_check() {
    log_info "开始健康检查: ${HEALTH_URL}"

    local attempt=1
    while [[ ${attempt} -le ${HEALTH_RETRIES} ]]; do
        # curl 发送 GET 请求，-s 静默模式，-o /dev/null 丢弃响应体
        # -w "%{http_code}" 只输出 HTTP 状态码
        local status_code
        status_code=$(curl -s -o /dev/null -w "%{http_code}" "${HEALTH_URL}" 2>/dev/null || echo "000")

        if [[ "${status_code}" == "200" ]]; then
            log_success "健康检查通过 (HTTP ${status_code})，第 ${attempt}/${HEALTH_RETRIES} 次尝试"
            return 0
        fi

        log_warn "健康检查失败 (HTTP ${status_code})，第 ${attempt}/${HEALTH_RETRIES} 次，${HEALTH_INTERVAL}秒后重试..."
        sleep "${HEALTH_INTERVAL}"
        attempt=$((attempt + 1))
    done

    log_error "健康检查在 ${HEALTH_RETRIES} 次尝试后仍然失败"
    return 1
}

# ========================= 清理旧镜像 =========================

cleanup_old_images() {
    log_info "清理旧镜像（保留最近 ${MAX_BACKUP_IMAGES} 个）..."

    # 列出指定应用的所有镜像标签，按创建时间排序
    local images
    images=$(docker images "${APP_NAME}" --format "{{.Tag}}" | head -n -${MAX_BACKUP_IMAGES} 2>/dev/null || true)

    if [[ -n "${images}" ]]; then
        for tag in ${images}; do
            log_info "删除旧镜像: ${APP_NAME}:${tag}"
            docker rmi "${APP_NAME}:${tag}" 2>/dev/null || true
        done
    else
        log_info "没有需要清理的旧镜像"
    fi
}

# ========================= 主部署流程 =========================

main() {
    # 解析命令行参数
    local skip_tests=false
    local do_rollback=false

    for arg in "$@"; do
        case ${arg} in
            --rollback)
                do_rollback=true
                ;;
            --skip-tests)
                skip_tests=true
                log_warn "将跳过测试步骤（不推荐）"
                ;;
            *)
                echo "用法: $0 [--rollback] [--skip-tests]"
                exit 1
                ;;
        esac
    done

    # 如果指定了 --rollback，直接执行回滚
    if [[ "${do_rollback}" == "true" ]]; then
        rollback
        exit 0
    fi

    log_info "========== 开始部署 ${APP_NAME} =========="
    local start_time
    start_time=$(date +%s)

    # 记录部署前的镜像标签（用于回滚）
    local prev_image_tag
    prev_image_tag=$(read_prev_deploy_info)
    log_info "当前运行版本: ${prev_image_tag:-无（首次部署）}"

    # -------------------- 阶段 1：拉取最新代码 --------------------
    log_info "[1/6] 拉取最新代码..."
    cd "${APP_DIR}"

    # git fetch 获取远程更新，git reset 确保本地与远程一致
    git fetch origin "${GIT_BRANCH}"
    git reset --hard "origin/${GIT_BRANCH}"

    # 获取最新的 commit SHA（用于打镜像标签）
    local commit_sha
    commit_sha=$(git rev-parse --short HEAD)
    log_success "代码已更新到 commit: ${commit_sha}"

    # -------------------- 阶段 2：安装依赖 --------------------
    log_info "[2/6] 安装 Python 依赖..."

    # 使用虚拟环境隔离依赖
    if [[ ! -d "venv" ]]; then
        python3 -m venv venv
    fi
    # 激活虚拟环境
    source venv/bin/activate

    # 升级 pip 并安装依赖
    pip install --upgrade pip -q
    pip install -r requirements.txt -q

    log_success "依赖安装完成"

    # -------------------- 阶段 3：运行测试 --------------------
    if [[ "${skip_tests}" == "false" ]]; then
        log_info "[3/6] 运行测试..."

        # 运行 pytest，-x 遇到第一个失败就停止
        if ! pytest tests/ -x -q; then
            log_error "测试失败！部署终止。"
            log_error "请修复测试后重新部署，或使用 --skip-tests 跳过（不推荐）"
            exit 1
        fi

        log_success "所有测试通过"
    else
        log_warn "[3/6] 跳过测试（--skip-tests 已启用）"
    fi

    # -------------------- 阶段 4：构建 Docker 镜像 --------------------
    local image_tag="${commit_sha}-$(date +%Y%m%d%H%M%S)"
    log_info "[4/6] 构建 Docker 镜像: ${APP_NAME}:${image_tag}"

    # 构建镜像，传入 build arg 用于内部配置
    docker build \
        -t "${APP_NAME}:${image_tag}" \
        -t "${APP_NAME}:latest" \
        --build-arg COMMIT_SHA="${commit_sha}" \
        --build-arg BUILD_TIME="$(date -u '+%Y-%m-%dT%H:%M:%SZ')" \
        .

    log_success "镜像构建完成: ${APP_NAME}:${image_tag}"

    # -------------------- 阶段 5：启动服务 --------------------
    log_info "[5/6] 启动服务..."

    # 先停止旧服务
    docker compose -f "${DOCKER_COMPOSE_FILE}" down --timeout 30 2>/dev/null || true

    # 使用新镜像启动服务
    IMAGE_TAG="${image_tag}" docker compose -f "${DOCKER_COMPOSE_FILE}" up -d

    log_success "服务已启动"

    # -------------------- 阶段 6：健康检查 --------------------
    log_info "[6/6] 执行健康检查..."

    if health_check; then
        # 健康检查通过：保存部署信息，清理旧镜像
        save_deploy_info "${image_tag}" "${commit_sha}"
        cleanup_old_images

        local end_time
        end_time=$(date +%s)
        local duration=$((end_time - start_time))

        log_success "========== 部署成功 =========="
        log_success "应用: ${APP_NAME}"
        log_success "版本: ${image_tag}"
        log_success "Commit: ${commit_sha}"
        log_success "耗时: ${duration} 秒"
    else
        # 健康检查失败：自动回滚
        log_error "健康检查失败，自动回滚到上一版本..."
        rollback
        exit 1
    fi
}

# 执行主函数，传递所有命令行参数
main "$@"
