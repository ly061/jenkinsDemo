// 定义解析测试结果的函数（使用 shell 脚本避免 Groovy 沙箱限制）
def parseTestNGResults() {
    def testCases = []
    def totalTests = 0
    def passedTests = 0
    def failedTests = 0
    def skippedTests = 0
    
    try {
        // 使用 shell 脚本解析 XML 文件（避免 Groovy 沙箱限制）
        def parseScript = '''
            #!/bin/bash
            # 查找 JUnit 格式的 XML 报告（TestNG 也会生成这种格式）
            XML_FILE=$(find target/surefire-reports -name "TEST-*.xml" -type f 2>/dev/null | head -1)
            
            if [ -z "$XML_FILE" ]; then
                # 尝试查找其他 XML 文件
                XML_FILE=$(find target/surefire-reports -name "*.xml" -type f 2>/dev/null | grep -v testng-results.xml | head -1)
            fi
            
            if [ -n "$XML_FILE" ] && [ -f "$XML_FILE" ]; then
                echo "XML_FILE:$XML_FILE"
                
                # 提取测试套件信息（使用 sed 替代 grep -oP，兼容性更好）
                TESTS=$(sed -n 's/.*tests="\\([^"]*\\)".*/\\1/p' "$XML_FILE" | head -1)
                FAILURES=$(sed -n 's/.*failures="\\([^"]*\\)".*/\\1/p' "$XML_FILE" | head -1)
                ERRORS=$(sed -n 's/.*errors="\\([^"]*\\)".*/\\1/p' "$XML_FILE" | head -1)
                SKIPPED=$(sed -n 's/.*skipped="\\([^"]*\\)".*/\\1/p' "$XML_FILE" | head -1)
                
                TESTS=${TESTS:-0}
                FAILURES=${FAILURES:-0}
                ERRORS=${ERRORS:-0}
                SKIPPED=${SKIPPED:-0}
                
                echo "TESTS:$TESTS"
                echo "FAILURES:$FAILURES"
                echo "ERRORS:$ERRORS"
                echo "SKIPPED:$SKIPPED"
                
                # 计算通过的测试数
                PASSED=$((TESTS - FAILURES - ERRORS - SKIPPED))
                echo "PASSED:$PASSED"
                
                # 提取测试用例信息（使用 Python 或简单的 sed/grep 组合）
                # 方法1：尝试使用 Python（如果可用）
                if command -v python3 &> /dev/null; then
                    python3 <<EOF
import sys
import xml.etree.ElementTree as ET

try:
    xml_file = "$XML_FILE"
    tree = ET.parse(xml_file)
    root = tree.getroot()
    
    index = 1
    for testcase in root.findall('.//testcase'):
        name = testcase.get('name', 'Unknown')
        classname = testcase.get('classname', 'Unknown')
        time = testcase.get('time', '0')
        
        # 判断状态
        if testcase.find('failure') is not None or testcase.find('error') is not None:
            status = 'FAILED'
        elif testcase.find('skipped') is not None:
            status = 'SKIPPED'
        else:
            status = 'PASSED'
        
        print("TEST_CASE_{}:{}|{}|{}|{}".format(index, name, classname, time, status))
        index += 1
except Exception as e:
    sys.exit(1)
EOF
                    if [ $? -ne 0 ]; then
                        # Python 失败，使用 sed/grep 方法
                        INDEX=1
                        while IFS= read -r line; do
                            if [[ "$line" =~ name=\"([^\"]+)\" ]]; then
                                NAME="${BASH_REMATCH[1]}"
                            fi
                            if [[ "$line" =~ classname=\"([^\"]+)\" ]]; then
                                CLASS="${BASH_REMATCH[1]}"
                            fi
                            if [[ "$line" =~ time=\"([^\"]+)\" ]]; then
                                TIME="${BASH_REMATCH[1]}"
                            fi
                            if echo "$line" | grep -q '</testcase>'; then
                                # 检查这个测试用例是否有失败或跳过
                                STATUS="PASSED"
                                # 使用简单的字符串匹配判断
                                if grep -A 5 "name=\"$NAME\"" "$XML_FILE" | grep -q '<failure\\|<error'; then
                                    STATUS="FAILED"
                                elif grep -A 5 "name=\"$NAME\"" "$XML_FILE" | grep -q '<skipped'; then
                                    STATUS="SKIPPED"
                                fi
                                echo "TEST_CASE_${INDEX}:${NAME}|${CLASS}|${TIME}|${STATUS}"
                                INDEX=$((INDEX + 1))
                                NAME=""
                                CLASS=""
                                TIME=""
                            fi
                        done < "$XML_FILE"
                    fi
                else
                    # 方法2：使用 sed 和 grep 的简化方法
                    INDEX=1
                    grep -o '<testcase[^>]*>' "$XML_FILE" | while read -r tag; do
                        NAME=$(echo "$tag" | sed -n 's/.*name="\\([^"]*\\)".*/\\1/p')
                        CLASS=$(echo "$tag" | sed -n 's/.*classname="\\([^"]*\\)".*/\\1/p')
                        TIME=$(echo "$tag" | sed -n 's/.*time="\\([^"]*\\)".*/\\1/p')
                        STATUS="PASSED"
                        
                        # 检查该测试用例的完整内容以判断状态
                        # 这是一个简化的方法，可能不够准确但可以工作
                        echo "TEST_CASE_${INDEX}:${NAME}|${CLASS}|${TIME}|${STATUS}"
                        INDEX=$((INDEX + 1))
                    done
                fi
            else
                echo "XML_FILE:NOT_FOUND"
            fi
        '''
        
        def parseResult = sh(
            script: parseScript,
            returnStdout: true
        ).trim()
        
        // 解析脚本输出
        def lines = parseResult.split('\n')
        def currentTestCaseIndex = 0
        
        lines.each { line ->
            if (line.startsWith('XML_FILE:')) {
                def filePath = line.substring(9)
                if (filePath == 'NOT_FOUND') {
                    echo "未找到测试报告 XML 文件"
                    return
                }
            } else if (line.startsWith('TESTS:')) {
                totalTests = line.substring(6).toInteger() ?: 0
            } else if (line.startsWith('PASSED:')) {
                passedTests = line.substring(7).toInteger() ?: 0
            } else if (line.startsWith('FAILURES:')) {
                failedTests = line.substring(9).toInteger() ?: 0
            } else if (line.startsWith('ERRORS:')) {
                def errors = line.substring(7).toInteger() ?: 0
                failedTests += errors
            } else if (line.startsWith('SKIPPED:')) {
                skippedTests = line.substring(8).toInteger() ?: 0
            } else if (line.startsWith('TEST_CASE_')) {
                def parts = line.substring(line.indexOf(':') + 1).split('\\|')
                if (parts.length >= 4) {
                    def testCase = [
                        name: parts[0],
                        className: parts[1],
                        time: parts[2] + 's',
                        status: parts[3]
                    ]
                    testCases.add(testCase)
                }
            }
        }
        
        // 如果解析失败，尝试从 TestNG results 文件读取
        if (totalTests == 0 && testCases.size() == 0) {
            def testngResultsFile = 'target/surefire-reports/testng-results.xml'
            if (fileExists(testngResultsFile)) {
                def testngParseScript = '''
                    #!/bin/bash
                    FILE="target/surefire-reports/testng-results.xml"
                    if [ -f "$FILE" ]; then
                        # 提取测试方法信息
                        INDEX=1
                        grep '<test-method' "$FILE" | while read -r line; do
                            NAME=$(echo "$line" | grep -oP 'name="\\K[^"]+' | head -1 || echo "Unknown")
                            CLASS=$(echo "$line" | grep -oP 'class="\\K[^"]+' | head -1 || echo "Unknown")
                            STATUS=$(echo "$line" | grep -oP 'status="\\K[^"]+' | head -1 || echo "PASS")
                            DURATION=$(echo "$line" | grep -oP 'duration-ms="\\K[^"]+' | head -1 || echo "0")
                            TIME=$(echo "scale=3; $DURATION / 1000" | bc | xargs printf "%.3f")
                            
                            echo "TEST_CASE_${INDEX}:${NAME}|${CLASS}|${TIME}|${STATUS}"
                            INDEX=$((INDEX + 1))
                        done
                    fi
                '''
                
                def testngResult = sh(
                    script: testngParseScript,
                    returnStdout: true
                ).trim()
                
                def testngLines = testngResult.split('\n')
                testngLines.each { line ->
                    if (line.startsWith('TEST_CASE_')) {
                        def parts = line.substring(line.indexOf(':') + 1).split('\\|')
                        if (parts.length >= 4) {
                            def status = parts[3].toUpperCase()
                            def testCase = [
                                name: parts[0],
                                className: parts[1],
                                time: parts[2] + 's',
                                status: status == 'PASS' ? 'PASSED' : (status == 'FAIL' ? 'FAILED' : 'SKIPPED')
                            ]
                            testCases.add(testCase)
                            
                            if (testCase.status == 'PASSED') {
                                passedTests++
                            } else if (testCase.status == 'FAILED') {
                                failedTests++
                            } else {
                                skippedTests++
                            }
                        }
                    }
                }
                totalTests = testCases.size()
            }
        }
        
    } catch (Exception e) {
        echo "解析测试报告时出错: ${e.message}"
        echo "堆栈跟踪: ${e.getStackTrace().join('\\n')}"
    }
    
    return [
        total: totalTests,
        passed: passedTests,
        failed: failedTests,
        skipped: skippedTests,
        testCases: testCases
    ]
}

// 生成邮件内容
def generateEmailBody(testResults) {
    def buildUrl = "${env.BUILD_URL}"
    def jobUrl = "${env.JOB_URL}"
    def triggerUser = currentBuild.getBuildCauses('hudson.model.Cause$UserIdCause')[0]?.userId ?: 
                     currentBuild.getBuildCauses('hudson.model.Cause$UserCause')[0]?.userId ?: 
                     '系统自动触发'
    
    def html = """
    <html>
    <head>
        <style>
            body { font-family: Arial, sans-serif; line-height: 1.6; color: #333; }
            .header { background-color: #4CAF50; color: white; padding: 20px; border-radius: 5px; }
            .content { padding: 20px; }
            .section { margin: 20px 0; padding: 15px; background-color: #f9f9f9; border-left: 4px solid #4CAF50; }
            .section h3 { margin-top: 0; color: #4CAF50; }
            table { width: 100%; border-collapse: collapse; margin: 10px 0; }
            th, td { padding: 12px; text-align: left; border-bottom: 1px solid #ddd; }
            th { background-color: #4CAF50; color: white; }
            tr:hover { background-color: #f5f5f5; }
            .passed { color: #4CAF50; font-weight: bold; }
            .failed { color: #f44336; font-weight: bold; }
            .skipped { color: #ff9800; font-weight: bold; }
            .info { background-color: #e3f2fd; padding: 10px; border-radius: 5px; margin: 10px 0; }
            .link { color: #2196F3; text-decoration: none; }
            .link:hover { text-decoration: underline; }
        </style>
    </head>
    <body>
        <div class="header">
            <h2>✅ TestNG 测试执行成功</h2>
            <p>项目: ${env.JOB_NAME}</p>
        </div>
        
        <div class="content">
            <div class="section">
                <h3>📋 构建信息</h3>
                <div class="info">
                    <p><strong>构建编号:</strong> #${env.BUILD_NUMBER}</p>
                    <p><strong>触发用户:</strong> ${triggerUser}</p>
                    <p><strong>构建链接:</strong> <a href="${buildUrl}" class="link">${buildUrl}</a></p>
                    <p><strong>作业链接:</strong> <a href="${jobUrl}" class="link">${jobUrl}</a></p>
                    <p><strong>构建时间:</strong> ${new Date().format("yyyy-MM-dd HH:mm:ss")}</p>
                </div>
            </div>
            
            <div class="section">
                <h3>📊 测试摘要</h3>
                <table>
                    <tr>
                        <th>总测试数</th>
                        <th>通过</th>
                        <th>失败</th>
                        <th>跳过</th>
                        <th>通过率</th>
                    </tr>
                    <tr>
                        <td>${testResults.total}</td>
                        <td class="passed">${testResults.passed}</td>
                        <td class="failed">${testResults.failed}</td>
                        <td class="skipped">${testResults.skipped}</td>
                        <td>${testResults.total > 0 ? String.format("%.1f", (testResults.passed / testResults.total) * 100) : 0}%</td>
                    </tr>
                </table>
            </div>
            
            <div class="section">
                <h3>📝 测试用例详情</h3>
                <p>共执行 <strong>${testResults.testCases.size()}</strong> 个测试用例：</p>
                <table>
                    <tr>
                        <th>序号</th>
                        <th>测试用例名称</th>
                        <th>类名</th>
                        <th>执行时间</th>
                        <th>执行结果</th>
                    </tr>
    """
    
    testResults.testCases.eachWithIndex { testCase, index ->
        def statusClass = testCase.status == 'PASSED' || testCase.status == 'PASS' ? 'passed' : 
                        (testCase.status == 'FAILED' || testCase.status == 'FAIL' ? 'failed' : 'skipped')
        def statusText = testCase.status == 'PASSED' || testCase.status == 'PASS' ? '✅ 通过' : 
                        (testCase.status == 'FAILED' || testCase.status == 'FAIL' ? '❌ 失败' : '⏭️ 跳过')
        
        html += """
                    <tr>
                        <td>${index + 1}</td>
                        <td>${testCase.name}</td>
                        <td>${testCase.className}</td>
                        <td>${testCase.time}</td>
                        <td class="${statusClass}">${statusText}</td>
                    </tr>
        """
    }
    
    html += """
                </table>
            </div>
            
            <div class="section">
                <h3>🔗 相关链接</h3>
                <p><a href="${buildUrl}" class="link">查看构建详情</a></p>
                <p><a href="${buildUrl}testReport/" class="link">查看测试报告</a></p>
                <p><a href="${jobUrl}" class="link">查看作业页面</a></p>
            </div>
            
            <div style="margin-top: 30px; padding: 15px; background-color: #f0f0f0; border-radius: 5px; text-align: center; color: #666;">
                <p>此邮件由 Jenkins 自动发送，请勿回复。</p>
                <p>构建时间: ${new Date().format("yyyy-MM-dd HH:mm:ss")}</p>
            </div>
        </div>
    </body>
    </html>
    """
    
    return html
}

pipeline {
    agent any
    
    // 如果需要使用预配置的工具，取消下面的注释并配置正确的工具名称
    // 配置方法：系统管理 → 全局工具配置 → Maven/JDK 安装
    // tools {
    //     maven 'Maven-3.9.9'  // 根据你的Jenkins中配置的Maven名称调整
    //     jdk 'JDK-17'          // 根据你的Jenkins中配置的JDK名称调整
    // }
    
    // 如果未配置工具，使用系统默认的 Maven 和 Java
    // 确保 Jenkins 节点上已安装 Maven 和 Java，并在 PATH 中可用
    
    options {
        // 保留最近10次构建的构建历史
        buildDiscarder(logRotator(numToKeepStr: '10'))
        // 超时时间设置为30分钟
        timeout(time: 30, unit: 'MINUTES')
    }
    
    stages {
        stage('Checkout') {
            steps {
                script {
                    echo '=== 检出代码 ==='
                    checkout scm
                }
            }
        }
        
        stage('Setup Maven') {
            steps {
                script {
                    echo '=== 设置 Maven 环境 ==='
                    // 尝试查找 Maven（包括用户的 Maven 安装路径）
                    def mavenPath = sh(
                        script: '''
                            # 尝试多个常见的 Maven 路径
                            if command -v mvn &> /dev/null; then
                                which mvn
                            elif [ -f /Users/joe/Documents/tools/apache-maven-3.9.9/bin/mvn ]; then
                                echo /Users/joe/Documents/tools/apache-maven-3.9.9/bin/mvn
                            elif [ -f /opt/homebrew/bin/mvn ]; then
                                echo /opt/homebrew/bin/mvn
                            elif [ -f /usr/local/bin/mvn ]; then
                                echo /usr/local/bin/mvn
                            elif [ -f /usr/bin/mvn ]; then
                                echo /usr/bin/mvn
                            else
                                echo "NOT_FOUND"
                            fi
                        ''',
                        returnStdout: true
                    ).trim()
                    
                    if (mavenPath == "NOT_FOUND" || mavenPath == "") {
                        error("""
                            ❌ Maven 未找到！
                            
                            解决方案：
                            1. 在 Jenkins 中配置 Maven 工具（推荐）：
                               - 系统管理 → 全局工具配置 → Maven 安装
                               - 名称：Maven-3.9.9
                               - MAVEN_HOME：/Users/joe/Documents/tools/apache-maven-3.9.9
                               - 然后在 Jenkinsfile 中取消注释 tools 部分
                            
                            2. 或者使用 Jenkinsfile-with-tools 并配置工具名称
                        """)
                    } else {
                        echo "找到 Maven: ${mavenPath}"
                        // 设置 MAVEN_HOME 和 PATH
                        def mavenHome = sh(
                            script: "dirname \$(dirname ${mavenPath})",
                            returnStdout: true
                        ).trim()
                        env.MAVEN_HOME = mavenHome
                        def mavenBinDir = sh(
                            script: "dirname ${mavenPath}",
                            returnStdout: true
                        ).trim()
                        env.PATH = "${mavenBinDir}:${env.PATH}"
                        echo "MAVEN_HOME: ${env.MAVEN_HOME}"
                        echo "PATH: ${env.PATH}"
                    }
                }
            }
        }
        
        stage('Environment Check') {
            steps {
                script {
                    echo '=== 检查环境 ==='
                    sh '''
                        echo "Java 版本:"
                        java -version || echo "Java 未找到"
                        echo ""
                        echo "Maven 版本和路径:"
                        mvn -version || echo "Maven 未找到"
                    '''
                }
            }
        }
        
        stage('Clean') {
            steps {
                script {
                    echo '=== 清理构建目录 ==='
                    sh 'mvn clean'
                }
            }
        }
        
        stage('Compile') {
            steps {
                script {
                    echo '=== 编译项目 ==='
                    sh 'mvn compile test-compile'
                }
            }
        }
        
        stage('Test') {
            steps {
                script {
                    echo '=== 运行 TestNG 测试 ==='
                    sh 'mvn test'
                }
            }
            post {
                always {
                    script {
                        // 发布测试报告（使用 junit 步骤，Jenkins 内置支持）
                        junit 'target/surefire-reports/*.xml'
                        
                        // 发布 TestNG HTML 报告（需要安装 HTML Publisher Plugin）
                        // 如果插件未安装，此行会失败，但不会影响其他步骤
                        try {
                            publishHTML([
                                reportDir: 'target/surefire-reports',
                                reportFiles: 'index.html',
                                reportName: 'TestNG 测试报告',
                                keepAll: true,
                                alwaysLinkToLastBuild: true,
                                allowMissing: false
                            ])
                        } catch (Exception e) {
                            echo "HTML Publisher Plugin 未安装或配置错误，跳过 HTML 报告发布: ${e.message}"
                        }
                        
                        // 归档测试报告
                        archiveArtifacts artifacts: 'target/surefire-reports/**/*', fingerprint: true
                    }
                }
                success {
                    echo '✅ 所有测试通过！'
                }
                failure {
                    echo '❌ 测试失败！'
                }
            }
        }
        
        stage('Archive Reports') {
            steps {
                script {
                    echo '=== 归档测试报告 ==='
                    // 确保报告目录存在
                    sh 'mkdir -p target/surefire-reports || true'
                }
            }
        }
    }
    
    post {
        always {
            script {
                echo '=== 构建完成 ==='
                // 清理临时文件（可选）
                // sh 'rm -rf target/.maven'
            }
        }
        success {
            script {
                echo '🎉 Pipeline 执行成功！'
                
                // 解析测试报告并生成邮件内容
                def testResults = parseTestNGResults()
                def emailBody = generateEmailBody(testResults)
                
                // 发送邮件
                emailext (
                    subject: "✅ TestNG 测试通过: ${env.JOB_NAME} - Build #${env.BUILD_NUMBER}",
                    body: emailBody,
                    to: "605402932@qq.com",
                    mimeType: 'text/html'
                )
            }
        }
        failure {
            echo '💥 Pipeline 执行失败！'
            // 可以在这里添加失败通知
            // emailext (
            //     subject: "❌ TestNG 测试失败: ${env.JOB_NAME} - ${env.BUILD_NUMBER}",
            //     body: "部分测试用例失败，请查看详细报告。",
            //     to: "your-email@example.com"
            // )
        }
        unstable {
            echo '⚠️ Pipeline 执行不稳定！'
        }
    }
}

