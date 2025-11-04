# TestNG 测试用例示例

本项目包含三个使用 TestNG 框架编写的测试用例。

## 文件说明

- `src/test/java/TestNGTestCases.java` - 包含三条测试用例的 Java 测试类
- `src/test/resources/testng.xml` - TestNG 配置文件
- `pom.xml` - Maven 项目配置文件
- `Jenkinsfile` - Jenkins Pipeline 配置文件（完整版）
- `Jenkinsfile-simple` - Jenkins Pipeline 配置文件（简化版）
- `jenkins-setup.md` - Jenkins 配置详细指南

## 测试用例

1. **测试用例1**: 验证字符串相等
   - 测试两个字符串是否相等

2. **测试用例2**: 验证数字计算
   - 测试基本的数学运算

3. **测试用例3**: 验证数组不为空
   - 测试数组的 null 检查和长度验证

## 运行方式

### 方式1: 使用 Maven

```bash
# 编译项目
mvn clean compile

# 运行测试
mvn test
```

### 方式2: 使用 IDE (IntelliJ IDEA / Eclipse)

1. 右键点击 `TestNGTestCases.java`
2. 选择 "Run 'TestNGTestCases'"

### 方式3: 使用命令行

```bash
# 编译
javac -cp ".:testng-7.8.0.jar" TestNGTestCases.java

# 运行（需要先下载 TestNG jar 包）
java -cp ".:testng-7.8.0.jar:jcommander-1.82.jar" org.testng.TestNG testng.xml
```

## 依赖

- TestNG 7.8.0 或更高版本
- Java 11 或更高版本

## Jenkins 集成

### 快速开始

1. **创建 Pipeline Job**
   - 在 Jenkins 中创建新的 Pipeline 任务
   - 选择 "Pipeline script from SCM" 或直接使用 `Jenkinsfile`

2. **配置工具**
   - 在 Jenkins 全局工具配置中设置 JDK 和 Maven
   - 确保工具名称与 `Jenkinsfile` 中的配置一致

3. **运行测试**
   - 点击 "立即构建" 触发测试
   - 查看构建日志和测试报告

详细配置说明请参考 [jenkins-setup.md](jenkins-setup.md)

### Jenkins Pipeline 文件

- **Jenkinsfile** - 完整版 Pipeline，包含详细的阶段和报告发布
- **Jenkinsfile-simple** - 简化版 Pipeline，适合快速配置

## 注意事项

- 确保已安装 Java 开发环境（Java 11+）
- 如果使用 Maven，确保已安装 Maven
- 测试用例按优先级（priority）顺序执行
- Jenkins 需要安装以下插件：
  - HTML Publisher Plugin（用于发布测试报告）
  - Pipeline Plugin（通常已默认安装）

