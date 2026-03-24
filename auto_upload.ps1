# PLM-BOM Getter Skill 自动上传脚本
# 使用前请修改 GITHUB_USERNAME 为您的 GitHub 用户名

$GITHUB_USERNAME = "65629293@qq.com"  # GitHub 用户名
$REPO_NAME = "plm-bom-getter"
$SKILL_DIR = "C:\Users\Administrator\openclaw\product_director_work\skills\plm-bom-getter"
$TEMP_DIR = "C:\Users\Administrator\openclaw\product_director_work\skills\plm-bom-getter-git"

Write-Host "====================================" -ForegroundColor Cyan
Write-Host "PLM-BOM Getter Skill 上传到 GitHub" -ForegroundColor Cyan
Write-Host "====================================" -ForegroundColor Cyan
Write-Host ""

# 检查 GitHub 用户名是否已修改
if ($GITHUB_USERNAME -eq "YOUR_USERNAME") {
    Write-Host "错误：请先修改脚本中的 GITHUB_USERNAME" -ForegroundColor Red
    Write-Host "编辑文件：$PSCommandPath" -ForegroundColor Yellow
    Write-Host "将 YOUR_USERNAME 替换为您的 GitHub 用户名" -ForegroundColor Yellow
    exit 1
}

$REPO_URL = "https://github.com/$GITHUB_USERNAME/$REPO_NAME.git"

Write-Host "步骤 1: 检查技能目录..." -ForegroundColor Green
if (Test-Path $SKILL_DIR) {
    Write-Host "  ✓ 技能目录存在：$SKILL_DIR" -ForegroundColor Green
} else {
    Write-Host "  ✗ 技能目录不存在" -ForegroundColor Red
    exit 1
}

Write-Host ""
Write-Host "步骤 2: 准备临时目录..." -ForegroundColor Green
if (Test-Path $TEMP_DIR) {
    Remove-Item $TEMP_DIR -Recurse -Force
    Write-Host "  ✓ 清理旧目录" -ForegroundColor Green
}
New-Item -ItemType Directory -Path $TEMP_DIR | Out-Null
Write-Host "  ✓ 创建临时目录：$TEMP_DIR" -ForegroundColor Green

Write-Host ""
Write-Host "步骤 3: 复制技能文件..." -ForegroundColor Green
Copy-Item "$SKILL_DIR\*" -Destination $TEMP_DIR -Recurse
Write-Host "  ✓ 文件已复制" -ForegroundColor Green

Write-Host ""
Write-Host "步骤 4: 初始化 Git 仓库..." -ForegroundColor Green
Set-Location $TEMP_DIR
git init | Out-Null
Write-Host "  ✓ Git 仓库已初始化" -ForegroundColor Green

Write-Host ""
Write-Host "步骤 5: 添加文件..." -ForegroundColor Green
git add . | Out-Null
Write-Host "  ✓ 文件已添加到暂存区" -ForegroundColor Green

Write-Host ""
Write-Host "步骤 6: 创建提交..." -ForegroundColor Green
git commit -m "Initial commit: PLM-BOM Getter Skill" | Out-Null
Write-Host "  ✓ 提交已创建" -ForegroundColor Green

Write-Host ""
Write-Host "步骤 7: 设置主分支..." -ForegroundColor Green
git branch -M main | Out-Null
Write-Host "  ✓ 主分支已设置为 main" -ForegroundColor Green

Write-Host ""
Write-Host "步骤 8: 添加远程仓库..." -ForegroundColor Green
git remote add origin $REPO_URL 2>$null
if ($?) {
    Write-Host "  ✓ 远程仓库已添加：$REPO_URL" -ForegroundColor Green
} else {
    Write-Host "  ! 远程仓库可能已存在，继续..." -ForegroundColor Yellow
}

Write-Host ""
Write-Host "步骤 9: 推送到 GitHub..." -ForegroundColor Green
Write-Host "  提示：需要输入 GitHub 用户名和密码（或 Personal Access Token）" -ForegroundColor Yellow
Write-Host ""
git push -u origin main

if ($?) {
    Write-Host ""
    Write-Host "====================================" -ForegroundColor Cyan
    Write-Host "上传成功！" -ForegroundColor Green
    Write-Host "====================================" -ForegroundColor Cyan
    Write-Host ""
    Write-Host "仓库地址：https://github.com/$GITHUB_USERNAME/$REPO_NAME" -ForegroundColor Cyan
    Write-Host ""
    Write-Host "清理临时目录..." -ForegroundColor Green
    Set-Location $SKILL_DIR
    Remove-Item $TEMP_DIR -Recurse -Force
    Write-Host "  ✓ 临时目录已清理" -ForegroundColor Green
} else {
    Write-Host ""
    Write-Host "====================================" -ForegroundColor Red
    Write-Host "上传失败" -ForegroundColor Red
    Write-Host "====================================" -ForegroundColor Red
    Write-Host ""
    Write-Host "可能原因：" -ForegroundColor Yellow
    Write-Host "1. GitHub 用户名或密码错误" -ForegroundColor Yellow
    Write-Host "2. 仓库不存在（请先在 GitHub 上创建仓库）" -ForegroundColor Yellow
    Write-Host "3. 网络连接问题" -ForegroundColor Yellow
    Write-Host ""
    Write-Host "临时目录保留在：$TEMP_DIR" -ForegroundColor Yellow
    Write-Host "可以手动处理后删除该目录" -ForegroundColor Yellow
}

Set-Location $SKILL_DIR
