# Claude Code Harness 项目规则手册
## 1. 项目基础信息
- 项目名称：PLM拉取产品成品料号
- 开发场景：为产品部服务，通过产品型号获取成品料号，再通过料号获取产品的所有完整BOM，以便PM可以高效识别BOM之间的差异
- 核心目标：输出可直接部署、低bug、易维护的工程化代码，高效解决开发与问题排查需求

## 2. 技术栈固定约束（根据项目的实际情况选择）
### 后端语言
- Python：3.10+，遵循PEP8规范，使用类型提示（typing模块），禁止全局变量、硬编码密钥
- Java：JDK8+/11，遵循Alibaba Java开发手册，SpringBoot/SpringCloud生态，分层架构
- JavaScript/TypeScript：Node.js16+，ES6+，TS严格模式，Airbnb JS/TS规范
- Go：1.18+，遵循Go官方规范，简洁高效，禁止过度封装

### 前端框架
- Vue2/3：Vue3+Vite，Composition API，Pinia状态管理，Element Plus UI
- React：18+，函数式组件+Hooks，Ant Design UI，TS语法

### 数据库&中间件
- 关系型：MySQL8.0+/PostgreSQL，SQLAlchemy/MyBatis操作，禁止裸SQL
- 非关系型：Redis/MongoDB，合理使用缓存，避免缓存穿透/击穿
- 接口规范：RESTful API，统一响应格式，JWT鉴权，状态码规范（200/400/401/500）

### 工具&测试
- 版本控制：Git，规范commit信息（feat/fix/refactor/docs）
- 代码检查：Python(mypy/flake8)、JS/TS(ESLint/Prettier)、Java(SonarQube)
- 测试要求：单元测试覆盖率≥70%，核心逻辑100%覆盖，边界场景测试

## 3. 架构分层约束（禁止违反）
### 通用分层规则
- 后端：Controller（接口层）→ Service（业务逻辑层）→ Dao/Repository（数据访问层）→ Model（实体层），单向依赖，禁止跨层调用
- 前端：Views（页面层）→ Components（组件层）→ Utils（工具层）→ API（接口层），逻辑与视图分离
- 禁止：业务逻辑写入接口层、数据层直接处理业务、硬编码配置、循环依赖

## 4. 代码质量禁止项
1. 禁止无异常处理的代码，所有接口、核心函数必须捕获异常并返回友好提示
2. 禁止冗余代码、重复逻辑，公共逻辑抽离为工具函数
3. 禁止使用废弃API、不安全的依赖、存在漏洞的第三方库
4. 禁止忽略边界条件（空值、超长参数、并发场景、权限校验）
5. 禁止代码无注释，核心逻辑、复杂函数、工具类必须添加注释说明

## 5. 输出质量门（必须全部通过）
1. 语法/类型检查：无错误、无警告
2. 代码规范：完全符合对应语言官方规范
3. 安全检查：无SQL注入、XSS、CSRF、密钥硬编码等漏洞
4. 运行验证：代码可直接运行，无启动报错
5. 测试验证：核心功能测试用例通过，无逻辑bug
