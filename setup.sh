#!/bin/bash

echo "=================================="
echo "AI営業支援システム セットアップ"
echo "=================================="
echo ""

# カラー定義
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# .envファイルの確認
if [ ! -f .env ]; then
    echo -e "${YELLOW}⚠ .envファイルが見つかりません。作成します...${NC}"
    cat > .env << 'EOF'
# Django Settings
DEBUG=True
SECRET_KEY=django-insecure-development-key-please-change-in-production
ALLOWED_HOSTS=localhost,127.0.0.1

# Database
POSTGRES_DB=proposal_db
POSTGRES_USER=postgres
POSTGRES_PASSWORD=postgres
DATABASE_URL=postgresql://postgres:postgres@db:5432/proposal_db

# Redis & Celery
REDIS_URL=redis://redis:6379/0
CELERY_BROKER_URL=redis://redis:6379/0
CELERY_RESULT_BACKEND=redis://redis:6379/0

# OpenAI API
OPENAI_API_KEY=your-openai-api-key-here

# Email (Optional)
EMAIL_BACKEND=django.core.mail.backends.console.EmailBackend
EOF
    echo -e "${GREEN}✓ .envファイルを作成しました${NC}"
    echo -e "${RED}※ OpenAI APIキーを設定してください！${NC}"
    echo ""
fi

# Dockerコンテナのビルドと起動
echo "Dockerコンテナをビルド・起動中..."
docker-compose up -d --build

# データベースの準備を待つ
echo "データベースの起動を待機中..."
sleep 10

# マイグレーション実行
echo "データベースマイグレーション実行中..."
docker-compose exec -T web python manage.py migrate

# 初期データ作成
echo "初期データを作成中..."
docker-compose exec -T web python manage.py setup_initial_data

echo ""
echo -e "${GREEN}=================================="
echo "✓ セットアップ完了！"
echo "==================================${NC}"
echo ""
echo "アクセス情報:"
echo "  メインアプリ: http://localhost:8000"
echo "  管理画面:     http://localhost:8000/admin"
echo ""
echo "ログイン情報:"
echo "  ユーザー名: admin"
echo "  パスワード: admin123"
echo ""
echo -e "${YELLOW}※本番環境では必ずパスワードを変更してください！${NC}"
echo ""
echo "ログ確認:"
echo "  docker-compose logs -f web"
echo ""
echo "停止:"
echo "  docker-compose down"
echo ""

