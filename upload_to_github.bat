@echo off
echo ====================================
echo PLM-BOM Getter Skill 上传到 GitHub
echo ====================================
echo.

set SKILL_DIR=C:\Users\Administrator\openclaw\product_director_work\skills\plm-bom-getter
set REPO_DIR=C:\Users\Administrator\openclaw\product_director_work\skills\plm-bom-getter-github

echo 步骤 1: 准备上传...
echo.
echo 请确认以下信息：
echo 1. GitHub 用户名：___________
echo 2. 仓库名称：plm-bom-getter
echo 3. 是否已创建仓库？(y/n): ___
echo.
pause

echo.
echo 步骤 2: 手动操作步骤
echo.
echo 1. 在 GitHub 上创建新仓库：
echo    https://github.com/new
echo    仓库名：plm-bom-getter
echo    可见性：Public 或 Private（根据您的选择）
echo.
echo 2. 复制仓库 URL:
echo    https://github.com/YOUR_USERNAME/plm-bom-getter.git
echo.
echo 3. 在本地执行以下命令：
echo    cd %SKILL_DIR%
echo    git init
echo    git add .
echo    git commit -m "Initial commit: PLM-BOM Getter Skill"
echo    git branch -M main
echo    git remote add origin https://github.com/YOUR_USERNAME/plm-bom-getter.git
echo    git push -u origin main
echo.
echo 4. 上传完成后，分享仓库链接给需要的人
echo.
pause

echo.
echo 或者直接复制技能文件夹：
echo %SKILL_DIR%
echo.
echo 通过 GitHub Desktop 或其他 Git 客户端上传
echo.
pause
