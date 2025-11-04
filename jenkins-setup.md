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

### 3. 配置工具（JDK 和 Maven）

在 Jenkins 中配置工具：

1. 进入 **系统管理** (Manage Jenkins) → **全局工具配置** (Global Tool Configuration)
2. 配置 JDK：
   - 点击 "JDK 安装" 的 "新增 JDK"
   - 名称：`JDK-17`
   - JAVA_HOME：`/Users/joe/Documents/tools/jdk-17.0.2.jdk/Contents/Home`（根据你的实际路径调整）
3. 配置 Maven：
   - 点击 "Maven 安装" 的 "新增 Maven"
   - 名称：`Maven-3.9.9`
   - MAVEN_HOME：`/Users/joe/Documents/tools/apache-maven-3.9.9`（根据你的实际路径调整）
4. 保存配置

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
- 确保在 Jenkins 中正确配置了 Maven
- 或者在构建步骤中使用完整路径：`/path/to/maven/bin/mvn test`

### 问题2：找不到 JDK
- 确保在 Jenkins 中正确配置了 JDK
- 检查 JAVA_HOME 环境变量

### 问题3：测试报告无法显示
- 确保安装了 HTML Publisher Plugin
- 检查报告路径是否正确
- 查看构建日志确认报告文件是否生成

### 问题4：权限问题
- 确保 Jenkins 用户有执行 Maven 和访问项目目录的权限

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

