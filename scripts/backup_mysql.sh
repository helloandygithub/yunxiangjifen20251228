#!/bin/bash
# MySQL自动备份脚本
# 用法: ./backup_mysql.sh
# 建议添加到crontab: 0 3 * * * /home/ubuntu/points-platform/scripts/backup_mysql.sh

# 配置
BACKUP_DIR="/home/ubuntu/backups/mysql"
CONTAINER_NAME="points_mysql"
DB_NAME="points_platform"
DB_USER="points_user"
DB_PASS="YunXiangPoints2025DB"
RETENTION_DAYS=7

# 创建备份目录
mkdir -p $BACKUP_DIR

# 生成备份文件名
TIMESTAMP=$(date +%Y%m%d_%H%M%S)
BACKUP_FILE="$BACKUP_DIR/${DB_NAME}_${TIMESTAMP}.sql.gz"

# 执行备份
echo "[$(date)] 开始备份数据库..."
docker exec $CONTAINER_NAME mysqldump -u$DB_USER -p$DB_PASS $DB_NAME 2>/dev/null | gzip > $BACKUP_FILE

# 检查备份结果
if [ $? -eq 0 ] && [ -s $BACKUP_FILE ]; then
    SIZE=$(du -h $BACKUP_FILE | cut -f1)
    echo "[$(date)] 备份成功: $BACKUP_FILE ($SIZE)"
else
    echo "[$(date)] 备份失败!"
    rm -f $BACKUP_FILE
    exit 1
fi

# 清理过期备份
echo "[$(date)] 清理${RETENTION_DAYS}天前的备份..."
find $BACKUP_DIR -name "*.sql.gz" -mtime +$RETENTION_DAYS -delete

# 显示当前备份列表
echo "[$(date)] 当前备份文件:"
ls -lh $BACKUP_DIR/*.sql.gz 2>/dev/null || echo "无备份文件"

echo "[$(date)] 备份任务完成"
