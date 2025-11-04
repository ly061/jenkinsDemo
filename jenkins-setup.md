# Jenkins 配置指南 - TestNG 测试自动化

本指南将帮助您在 Jenkins 中配置 Job 来运行 TestNG 测试用例。

## 方式一：使用 Jenkins Pipeline（推荐）

### 1. 创建 Pipeline Job

1. 登录 Jenkins
2. 点击 "新建任务" (New Item)
3. 输入任务名称，选择 "流水线" (Pipeline)
4. 点击 "确定"

### 2. 配置 Pipeline

有两种方式配置 Pipeline：

#### 方式 A：从 SCM 读取（推荐，如果代码在 Git 仓库中）

1. 在 Pipeline 配置页面，选择 "Pipeline script from SCM"
2. SCM 选择 Git
3. 填写 Repository URL（你的 Git 仓库地址）
4. 分支选择 `*/main` 或 `*/master`
5. Script Path 填写 `Jenkinsfile`
6. 保存配置

#### 方式 B：直接编写 Pipeline 脚本

1. 在 Pipeline 配置页面，选择 "Pipeline script"
2. 将 `Jenkinsfile` 的内容复制粘贴到脚本框中
3. 保存配置

### 3. 配置工具（JDK 和 Maven）- 可选

**方式 A：使用系统默认工具（推荐，更简单）**

如果 Jenkins 节点上已安装 Maven 和 Java 并在 PATH 中可用，可以直接使用，无需额外配置。

当前 `Jenkinsfile` 已配置为使用系统默认工具，可以直接运行。

**方式 B：在 Jenkins 中配置工具（可选）**

如果需要使用特定版本的工具，可以在 Jenkins 中配置：

1. 进入 **系统管理** (Manage Jenkins) → **全局工具配置** (Global Tool Configuration)
2. 配置 JDK：
   - 点击 "JDK 安装" 的 "新增 JDK"
   - 名称：`JDK-17`（或其他名称）
   - JAVA_HOME：`/path/to/jdk`（根据你的实际路径调整）
3. 配置 Maven：
   - 点击 "Maven 安装" 的 "新增 Maven"
   - 名称：`Maven-3.9.9`（或其他名称）
   - MAVEN_HOME：`/path/to/maven`（根据你的实际路径调整）
4. 保存配置
5. 在 `Jenkinsfile` 中取消注释 `tools` 部分，并修改工具名称为你配置的名称
6. 或者使用 `Jenkinsfile-with-tools` 文件

### 4. 安装必要的插件

确保安装以下 Jenkins 插件：

- **HTML Publisher Plugin** - 用于发布 TestNG HTML 报告
- **TestNG Results Plugin** - 用于解析 TestNG 测试结果（可选）
- **Pipeline Plugin** - Pipeline 支持（通常已安装）

安装方法：
1. 系统管理 → 插件管理
2. 搜索并安装上述插件
3. 重启 Jenkins

### 5. 运行 Pipeline

1. 在 Jenkins 首页找到你创建的 Pipeline Job
2. 点击 "立即构建" (Build Now)
3. 查看构建日志和测试报告

---

## 方式二：使用 Freestyle Project（传统方式）

### 1. 创建 Freestyle Job

1. 登录 Jenkins
2. 点击 "新建任务"
3. 输入任务名称，选择 "自由风格的软件项目"
4. 点击 "确定"

### 2. 配置源码管理（如果使用 Git）

1. 在 "源码管理" 部分选择 Git
2. 填写 Repository URL
3. 分支选择 `*/main` 或 `*/master`

### 3. 配置构建步骤

在 "构建" 部分，点击 "增加构建步骤" → "执行 shell"（Linux/Mac）或 "执行 Windows 批处理命令"（Windows）

**Linux/Mac 脚本：**
```bash
#!/bin/bash
echo "=== 清理构建 ==="
mvn clean

echo "=== 编译项目 ==="
mvn compile test-compile

echo "=== 运行测试 ==="
mvn test
```

**Windows 脚本：**
```batch
echo === 清理构建 ===
call mvn clean

echo === 编译项目 ===
call mvn compile test-compile

echo === 运行测试 ===
call mvn test
```

### 4. 配置构建后操作

在 "构建后操作" 部分：

1. **发布测试结果报告**
   - 点击 "增加构建后操作步骤" → "Publish test results"
   - Test results XML files: `target/surefire-reports/*.xml`

2. **发布 HTML 报告**
   - 点击 "增加构建后操作步骤" → "Publish HTML reports"
   - HTML directory to archive: `target/surefire-reports`
   - Index page[s]: `index.html`
   - Report title: `TestNG 测试报告`

3. **归档构建产物**
   - 点击 "增加构建后操作步骤" → "归档成品"
   - 要归档的文件: `target/surefire-reports/**/*`

### 5. 配置环境变量

在 "构建环境" 部分，可以设置：

- **JAVA_HOME**: `/Users/joe/Documents/tools/jdk-17.0.2.jdk/Contents/Home`
- **M2_HOME**: `/Users/joe/Documents/tools/apache-maven-3.9.9`
- **PATH**: `$M2_HOME/bin:$JAVA_HOME/bin:$PATH`

---

## 查看测试报告

构建完成后，可以通过以下方式查看测试报告：

1. **Jenkins 构建页面**
   - 在构建历史中点击构建号
   - 查看 "TestNG 测试报告" 链接（如果安装了 HTML Publisher Plugin）

2. **测试结果摘要**
   - 在构建页面左侧可以看到测试结果摘要
   - 显示通过的测试数、失败的测试数等

3. **控制台输出**
   - 点击 "控制台输出" 查看详细的构建和测试日志

---

## 定时触发（可选）

### 在 Pipeline 中配置定时触发

在 `Jenkinsfile` 的 `options` 部分添加：

```groovy
triggers {
    // 每天凌晨2点运行
    cron('H 2 * * *')
    // 或者每小时运行一次
    // cron('H * * * *')
}
```

### 在 Freestyle Job 中配置定时触发

1. 在 Job 配置页面，勾选 "构建触发器" → "定时构建"
2. 输入 Cron 表达式，例如：`H 2 * * *`（每天凌晨2点）

---

## 参数化构建（可选）

如果需要参数化构建，可以在 Pipeline 中添加：

```groovy
parameters {
    choice(
        name: 'TEST_SUITE',
        choices: ['all', 'smoke', 'regression'],
        description: '选择要运行的测试套件'
    )
}
```

然后在测试阶段使用：
```groovy
stage('Test') {
    steps {
        script {
            if (params.TEST_SUITE == 'all') {
                sh 'mvn test'
            } else {
                sh "mvn test -DsuiteXmlFile=src/test/resources/testng-${params.TEST_SUITE}.xml"
            }
        }
    }
}
```

---

## 故障排查

### 问题1：找不到 Maven 命令
- 确保 Jenkins 节点上已安装 Maven 并在 PATH 中可用
- 检查构建日志中的 "Environment Check" 阶段输出
- 如果使用工具配置，确保在 Jenkins 中正确配置了 Maven 工具名称
- 或者使用完整路径：`/path/to/maven/bin/mvn test`

### 问题2：找不到 JDK
- 确保 Jenkins 节点上已安装 Java 并在 PATH 中可用
- 检查构建日志中的 "Environment Check" 阶段输出
- 如果使用工具配置，确保在 Jenkins 中正确配置了 JDK 工具名称
- 检查 JAVA_HOME 环境变量

### 问题6：工具配置错误（Tool type "maven" does not have an install configured）

**错误信息：**
```
Tool type "maven" does not have an install of "Maven-3.9.9" configured
```

**解决方案：**

#### 方案1：使用系统默认工具（推荐）

当前 `Jenkinsfile` 已配置为使用系统默认的 Maven 和 Java，无需在 Jenkins 中配置工具。

**前提条件：**
- Jenkins 节点上已安装 Maven 和 Java
- Maven 和 Java 在系统 PATH 中可用

**验证方法：**
在 Jenkins 节点上执行：
```bash
which mvn
which java
mvn -version
java -version
```

#### 方案2：配置 Jenkins 工具

如果需要在 Jenkins 中配置工具：

1. **配置工具：**
   - 系统管理 → 全局工具配置
   - 添加 Maven 和 JDK，并记录工具名称

2. **修改 Jenkinsfile：**
   - 取消注释 `tools` 部分
   - 修改工具名称为你配置的名称
   - 或者使用 `Jenkinsfile-with-tools` 并修改工具名称

3. **工具名称必须完全匹配：**
   - 工具名称区分大小写
   - 必须与 Jenkins 中配置的名称完全一致

### 问题3：测试报告无法显示
- 确保安装了 HTML Publisher Plugin
- 检查报告路径是否正确
- 查看构建日志确认报告文件是否生成

### 问题4：权限问题
- 确保 Jenkins 用户有执行 Maven 和访问项目目录的权限

### 问题5：GitHub 连接失败（HTTPS 无法连接）

**错误信息：**
```
fatal: unable to access 'https://github.com/ly061/jenkinsDemo.git/': 
Failed to connect to github.com port 443 after 75000 ms: Couldn't connect to server
```

**解决方案：**

#### 方案1：使用 SSH 代替 HTTPS（推荐）

1. **在 Jenkins 服务器上配置 SSH 密钥：**
   ```bash
   # 以 Jenkins 用户身份登录服务器
   sudo su - jenkins
   
   # 生成 SSH 密钥（如果还没有）
   ssh-keygen -t rsa -b 4096 -C "jenkins@your-server"
   
   # 查看公钥
   cat ~/.ssh/id_rsa.pub
   ```

2. **将公钥添加到 GitHub：**
   - 登录 GitHub → Settings → SSH and GPG keys
   - 点击 "New SSH key"
   - 粘贴公钥内容并保存

3. **在 Jenkins 中更改仓库地址：**
   - 进入 Pipeline Job 配置页面
   - 在 "Pipeline script from SCM" 部分
   - 将 Repository URL 改为：`git@github.com:ly061/jenkinsDemo.git`
   - 保存并重新构建

#### 方案2：配置代理服务器

如果 Jenkins 服务器需要通过代理访问外网：

1. **配置 Jenkins 全局代理：**
   - 系统管理 → 系统配置 → 代理配置
   - 填写代理服务器信息：
     - 代理主机名：`your-proxy-host`
     - 代理端口：`8080`
     - 用户名和密码（如果需要）
   - 在 "No Proxy Host" 中添加：`localhost,127.0.0.1`

2. **配置 Git 使用代理：**
   - 在 Pipeline 的 Checkout 阶段之前添加：
   ```groovy
   stage('Setup Proxy') {
       steps {
           sh '''
           git config --global http.proxy http://proxy-host:port
           git config --global https.proxy http://proxy-host:port
           '''
       }
   }
   ```

#### 方案3：使用 GitHub 个人访问令牌（Personal Access Token）

1. **创建 GitHub 访问令牌：**
   - GitHub → Settings → Developer settings → Personal access tokens → Tokens (classic)
   - 点击 "Generate new token (classic)"
   - 选择权限：`repo`（完整仓库访问权限）
   - 生成并复制令牌

2. **在 Jenkins 中配置凭据：**
   - 系统管理 → Manage Credentials
   - 添加凭据：
     - 类型：Username with password
     - Username：你的 GitHub 用户名
     - Password：刚才生成的访问令牌
     - ID：`github-token`（或其他标识）

3. **在 Pipeline 配置中使用凭据：**
   - 在 "Pipeline script from SCM" 配置中
   - Credentials 选择刚才创建的凭据
   - Repository URL 使用 HTTPS：`https://github.com/ly061/jenkinsDemo.git`

#### 方案4：检查网络连接

在 Jenkins 服务器上测试连接：

```bash
# 测试 GitHub 连接
ping github.com

# 测试 HTTPS 连接
curl -I https://github.com

# 测试 SSH 连接
ssh -T git@github.com
```

#### 方案5：使用本地文件系统（临时方案）

如果网络问题暂时无法解决，可以：

1. **手动克隆仓库到 Jenkins 服务器：**
   ```bash
   cd /var/jenkins_home/workspace
   git clone https://github.com/ly061/jenkinsDemo.git
   ```

2. **修改 Jenkinsfile 使用本地路径：**
   ```groovy
   stage('Checkout') {
       steps {
           dir('jenkinsDemo') {
               // 使用本地代码
           }
       }
   }
   ```

#### 推荐配置（SSH 方式）

**Pipeline 配置示例：**
```
Repository URL: git@github.com:ly061/jenkinsDemo.git
Credentials: (选择 SSH 凭据或留空)
Branch Specifier: */main
Script Path: Jenkinsfile
```

**注意事项：**
- 确保 Jenkins 服务器可以访问 GitHub（端口 22 用于 SSH）
- 如果防火墙阻止 SSH，需要开放端口 22
- 使用 SSH 方式不需要配置用户名和密码

---

## 最佳实践

1. **使用 Pipeline**：Pipeline as Code 更易于版本控制和维护
2. **并行执行**：如果有多个测试套件，可以考虑并行执行以提高速度
3. **通知机制**：配置邮件或 Slack 通知，及时了解测试结果
4. **保留历史**：合理配置构建历史保留策略
5. **代码版本控制**：将 Jenkinsfile 提交到代码仓库

---

## 示例 Cron 表达式

- `H * * * *` - 每小时
- `H 2 * * *` - 每天凌晨2点
- `H 9 * * 1-5` - 工作日上午9点
- `H */4 * * *` - 每4小时

---

## 联系和支持

如有问题，请查看：
- Jenkins 官方文档：https://www.jenkins.io/doc/
- TestNG 文档：https://testng.org/doc/documentation-main.html

