# Jenkins 邮件配置指南

## 功能说明

当构建成功时，Jenkins 会自动发送邮件到 `605402932@qq.com`，邮件包含：

### 📋 构建信息
- 构建编号（Build Number）
- 触发用户（谁触发的构建）
- 构建链接（Build URL）
- 作业链接（Job URL）
- 构建时间

### 📊 测试摘要
- 总测试数
- 通过/失败/跳过数量
- 通过率

### 📝 测试用例详情
- 每个测试用例的名称
- 类名
- 执行时间
- 执行结果（通过/失败/跳过）

## 安装 Email Extension Plugin

1. 进入 **系统管理** → **插件管理**
2. 搜索 "Email Extension Plugin"
3. 点击 "立即安装"
4. 安装完成后重启 Jenkins

## 配置邮件服务器

### 方式一：使用 QQ 邮箱 SMTP（推荐）

1. 进入 **系统管理** → **系统配置**
2. 找到 "Extended E-mail Notification" 部分
3. 配置以下信息：

```
SMTP 服务器: smtp.qq.com
SMTP 端口: 465（SSL）或 587（TLS）
使用 SSL: 是（如果使用 465 端口）
使用 TLS: 是（如果使用 587 端口）

用户名: 你的QQ邮箱（如：605402932@qq.com）
密码: QQ邮箱授权码（不是登录密码！）

默认用户电子邮件后缀: @qq.com
```

4. 点击 "高级" 展开更多选项
5. 配置：
   - **Default Subject**: `[Jenkins] ${PROJECT_NAME} - Build #${BUILD_NUMBER} - ${BUILD_STATUS}!`
   - **Default Content**: 可以留空，使用 Pipeline 中的内容
   - **Default Recipients**: `605402932@qq.com`

6. 点击 "测试配置" 发送测试邮件
7. 保存配置

### 获取 QQ 邮箱授权码

1. 登录 QQ 邮箱：https://mail.qq.com
2. 点击 "设置" → "账户"
3. 找到 "POP3/IMAP/SMTP/Exchange/CardDAV/CalDAV服务"
4. 开启 "POP3/SMTP服务" 或 "IMAP/SMTP服务"
5. 点击 "生成授权码"
6. 按照提示发送短信验证
7. 复制生成的授权码（16位字符）

### 方式二：使用其他邮件服务

**Gmail:**
```
SMTP 服务器: smtp.gmail.com
SMTP 端口: 587
使用 TLS: 是
```

**163 邮箱:**
```
SMTP 服务器: smtp.163.com
SMTP 端口: 465
使用 SSL: 是
```

**企业邮箱:**
请咨询企业 IT 管理员获取 SMTP 配置信息

## 测试邮件发送

1. 在 Jenkins 中配置好邮件后，点击 "测试配置"
2. 如果测试成功，你会收到测试邮件
3. 如果失败，检查：
   - SMTP 服务器地址和端口是否正确
   - 用户名和密码（授权码）是否正确
   - 防火墙是否阻止了连接
   - 是否启用了 SSL/TLS

## 邮件内容示例

邮件将包含以下内容：

### 构建信息
- 构建编号: #8
- 触发用户: root
- 构建链接: http://localhost:8080/job/pipeline/8/
- 作业链接: http://localhost:8080/job/pipeline/
- 构建时间: 2025-11-04 20:50:00

### 测试摘要
- 总测试数: 3
- 通过: 3
- 失败: 0
- 跳过: 0
- 通过率: 100.0%

### 测试用例详情
| 序号 | 测试用例名称 | 类名 | 执行时间 | 执行结果 |
|------|-------------|------|---------|---------|
| 1 | testCase1_StringEquals | TestNGTestCases | 0.001s | ✅ 通过 |
| 2 | testCase2_NumberCalculation | TestNGTestCases | 0.002s | ✅ 通过 |
| 3 | testCase3_ArrayNotEmpty | TestNGTestCases | 0.001s | ✅ 通过 |

## 故障排查

### 问题1：邮件未发送

**检查清单：**
- [ ] Email Extension Plugin 是否已安装
- [ ] 邮件服务器配置是否正确
- [ ] 是否点击了 "测试配置" 并成功
- [ ] 构建是否真的成功了（只有成功时才会发送）
- [ ] 查看构建日志中是否有邮件发送的错误信息

### 问题2：邮件发送失败

**常见错误：**

1. **"Authentication failed"**
   - 检查用户名和密码（授权码）是否正确
   - 确认使用的是授权码而不是登录密码

2. **"Connection timeout"**
   - 检查 SMTP 服务器地址和端口
   - 检查防火墙设置
   - 尝试使用不同的端口（465 或 587）

3. **"SSL/TLS error"**
   - 确保正确启用了 SSL 或 TLS
   - 尝试关闭 SSL 验证（仅用于测试）

### 问题3：邮件内容不完整

**可能原因：**
- 测试报告文件未生成
- 测试报告格式不正确
- 解析函数遇到错误

**解决方法：**
- 查看构建日志中的错误信息
- 检查 `target/surefire-reports/` 目录下是否有报告文件
- 确认测试确实执行了

## 自定义邮件内容

如果需要修改邮件内容，可以编辑 `Jenkinsfile` 中的 `generateEmailBody()` 函数。

## 注意事项

1. **邮件发送频率**: 当前配置只在构建成功时发送邮件
2. **邮件地址**: 收件人地址硬编码在 Pipeline 中为 `605402932@qq.com`
3. **HTML 格式**: 邮件使用 HTML 格式，支持富文本显示
4. **权限要求**: Jenkins 需要有网络访问权限以连接 SMTP 服务器

## 相关链接

- [Email Extension Plugin 文档](https://plugins.jenkins.io/email-ext/)
- [Jenkins 邮件配置指南](https://www.jenkins.io/doc/book/system-administration/email/)

