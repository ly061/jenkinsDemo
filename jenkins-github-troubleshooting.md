# Jenkins GitHub 连接问题排查指南

## 问题描述

Jenkins 在尝试从 GitHub 拉取代码时出现连接失败错误：

```
fatal: unable to access 'https://github.com/ly061/jenkinsDemo.git/': 
Failed to connect to github.com port 443 after 75000 ms: Couldn't connect to server
```

## 快速解决方案

### ✅ 方案1：使用 SSH 连接（最推荐）

**步骤：**

1. **在 Jenkins 服务器上生成 SSH 密钥**

   ```bash
   # 切换到 Jenkins 用户
   sudo su - jenkins
   
   # 生成 SSH 密钥（如果还没有）
   ssh-keygen -t rsa -b 4096 -C "jenkins@your-server"
   # 按 Enter 使用默认路径，可以选择不设置密码短语
   
   # 查看公钥
   cat ~/.ssh/id_rsa.pub
   ```

2. **将公钥添加到 GitHub**

   - 访问：https://github.com/settings/keys
   - 点击 "New SSH key"
   - Title: `Jenkins Server`
   - Key: 粘贴刚才复制的公钥内容
   - 点击 "Add SSH key"

3. **测试 SSH 连接**

   ```bash
   ssh -T git@github.com
   # 应该看到：Hi ly061! You've successfully authenticated...
   ```

4. **在 Jenkins 中配置**

   - 进入 Pipeline Job 配置页面
   - Pipeline script from SCM → Repository URL
   - 改为：`git@github.com:ly061/jenkinsDemo.git`
   - 保存并重新构建

### ✅ 方案2：使用 GitHub 个人访问令牌

**步骤：**

1. **创建 GitHub 访问令牌**

   - 访问：https://github.com/settings/tokens
   - 点击 "Generate new token (classic)"
   - Note: `Jenkins Access`
   - 选择权限：勾选 `repo`（完整仓库访问权限）
   - 点击 "Generate token"
   - **重要**：立即复制令牌（只显示一次）

2. **在 Jenkins 中配置凭据**

   - 系统管理 → Manage Credentials → 全局 → Add Credentials
   - 类型：Username with password
   - Username：`ly061`（你的 GitHub 用户名）
   - Password：`ghp_xxxxxxxxxxxxx`（刚才生成的令牌）
   - ID：`github-token`
   - Description：`GitHub Personal Access Token`
   - 点击 "OK"

3. **在 Pipeline 中使用凭据**

   - Pipeline script from SCM
   - Repository URL：`https://github.com/ly061/jenkinsDemo.git`
   - Credentials：选择刚才创建的 `github-token`
   - 保存并重新构建

### ✅ 方案3：配置代理服务器

如果 Jenkins 服务器在内网，需要通过代理访问 GitHub：

1. **配置 Jenkins 全局代理**

   - 系统管理 → 系统配置 → 代理配置
   - 填写代理信息：
     ```
     代理主机名：proxy.company.com
     代理端口：8080
     用户名：your-username（如果需要）
     密码：your-password（如果需要）
     ```
   - No Proxy Host：`localhost,127.0.0.1,github.com`
   - 保存

2. **或者配置 Git 代理（在 Pipeline 中）**

   ```groovy
   pipeline {
       agent any
       
       stages {
           stage('Setup') {
               steps {
                   sh '''
                   git config --global http.proxy http://proxy-host:port
                   git config --global https.proxy http://proxy-host:port
                   '''
               }
           }
           
           stage('Checkout') {
               steps {
                   checkout scm
               }
           }
           
           // ... 其他阶段
       }
   }
   ```

## 诊断步骤

### 1. 检查网络连接

在 Jenkins 服务器上执行：

```bash
# 测试 GitHub 可访问性
ping github.com

# 测试 HTTPS 端口
telnet github.com 443

# 测试 SSH 端口
telnet github.com 22

# 测试 DNS 解析
nslookup github.com
```

### 2. 检查防火墙规则

```bash
# 检查防火墙状态
sudo ufw status
# 或
sudo iptables -L

# 如果需要，开放端口
sudo ufw allow 22/tcp  # SSH
sudo ufw allow 443/tcp # HTTPS
```

### 3. 检查 Git 配置

```bash
# 查看 Git 全局配置
git config --global --list

# 检查代理设置
git config --global http.proxy
git config --global https.proxy

# 如果需要清除代理设置
git config --global --unset http.proxy
git config --global --unset https.proxy
```

### 4. 测试 Git 操作

```bash
# 测试 HTTPS 克隆
git clone https://github.com/ly061/jenkinsDemo.git /tmp/test-https

# 测试 SSH 克隆
git clone git@github.com:ly061/jenkinsDemo.git /tmp/test-ssh
```

## 常见问题

### Q1: SSH 密钥已添加但 still 无法连接？

**A:** 检查 SSH 配置：
```bash
# 测试 SSH 连接
ssh -vT git@github.com

# 查看详细错误信息
# 可能需要检查 ~/.ssh/config 文件
```

### Q2: 使用 HTTPS 时提示需要认证？

**A:** 确保：
- 使用个人访问令牌而不是密码
- 凭据已正确配置在 Jenkins 中
- 令牌有正确的权限（repo 权限）

### Q3: 代理配置后仍然无法连接？

**A:** 检查：
- 代理服务器是否正常运行
- 代理是否需要认证
- No Proxy Host 列表是否包含需要的域名
- 尝试在 Pipeline 中直接配置 Git 代理

### Q4: 如何验证配置是否成功？

**A:** 在 Jenkins 中：
1. 进入 Pipeline Job 配置页面
2. 点击 "立即构建"
3. 查看控制台输出
4. 应该看到类似信息：
   ```
   Cloning the remote Git repository
   Cloning repository https://github.com/ly061/jenkinsDemo.git
   ```

## 推荐配置

**最佳实践：使用 SSH 方式**

**优点：**
- 不需要每次输入凭据
- 更安全
- 不受 HTTPS 代理限制
- 配置一次，长期使用

**配置要点：**
- Repository URL: `git@github.com:ly061/jenkinsDemo.git`
- 不需要配置 Credentials（使用 SSH 密钥）
- 确保 Jenkins 服务器可以访问 GitHub（端口 22）

## 联系支持

如果以上方案都无法解决问题，请检查：
1. Jenkins 服务器网络配置
2. 公司防火墙策略
3. GitHub 访问状态：https://www.githubstatus.com/

