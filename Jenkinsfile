pipeline {
    agent any
    
    tools {
        // 根据你的Jenkins中配置的工具名称调整
        maven 'Maven-3.9.9'  // 修改为你的 Maven 工具名称
        jdk 'JDK-17'          // 修改为你的 JDK 工具名称
    }
    
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
                    // 发布测试报告
                    publishTestResults testResultsPattern: 'target/surefire-reports/*.xml'
                    
                    // 发布 TestNG HTML 报告
                    try {
                        publishHTML([
                            reportDir: 'target/surefire-reports',
                            reportFiles: 'index.html',
                            reportName: 'TestNG 测试报告',
                            keepAll: true
                        ])
                    } catch (Exception e) {
                        echo "HTML Publisher Plugin 未安装，跳过 HTML 报告发布: ${e.message}"
                    }
                    
                    // 归档测试报告
                    archiveArtifacts artifacts: 'target/surefire-reports/**/*', fingerprint: true
                }
            }
        }
    }
    
    post {
        always {
            script {
                echo '=== 解析测试结果并发送邮件 ==='
                
                // 解析TestNG XML报告并生成邮件内容
                def emailBody = generateEmailBody()
                
                // 发送邮件
                emailext(
                    subject: "[Jenkins] ${env.JOB_NAME} - Build #${env.BUILD_NUMBER} - ${currentBuild.currentResult}",
                    body: emailBody,
                    to: '17381915093@163.com',
                    mimeType: 'text/html',
                    attachLog: false
                )
            }
        }
    }
}

/**
 * 生成邮件内容
 * 包含构建信息和测试用例详细信息
 */
def generateEmailBody() {
    def buildInfo = getBuildInfo()
    def testSummary = getTestSummary()
    def testCases = getTestCasesDetails()
    
    def html = """
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="UTF-8">
        <style>
            body { font-family: Arial, sans-serif; line-height: 1.6; color: #333; }
            .container { max-width: 900px; margin: 0 auto; padding: 20px; }
            h1 { color: #2c3e50; border-bottom: 3px solid #3498db; padding-bottom: 10px; }
            h2 { color: #34495e; margin-top: 30px; border-left: 4px solid #3498db; padding-left: 10px; }
            .info-box { background-color: #f8f9fa; border: 1px solid #dee2e6; border-radius: 5px; padding: 15px; margin: 15px 0; }
            .info-row { margin: 8px 0; }
            .info-label { font-weight: bold; color: #495057; display: inline-block; width: 150px; }
            .summary-box { background-color: #e7f3ff; border-left: 4px solid #2196F3; padding: 15px; margin: 15px 0; }
            .summary-item { margin: 5px 0; font-size: 16px; }
            .success { color: #28a745; font-weight: bold; }
            .failure { color: #dc3545; font-weight: bold; }
            .skipped { color: #ffc107; font-weight: bold; }
            table { width: 100%; border-collapse: collapse; margin: 20px 0; }
            th { background-color: #3498db; color: white; padding: 12px; text-align: left; }
            td { padding: 10px; border-bottom: 1px solid #ddd; }
            tr:hover { background-color: #f5f5f5; }
            .status-pass { color: #28a745; font-weight: bold; }
            .status-fail { color: #dc3545; font-weight: bold; }
            .status-skip { color: #ffc107; font-weight: bold; }
            .footer { margin-top: 30px; padding-top: 20px; border-top: 1px solid #ddd; color: #6c757d; font-size: 12px; text-align: center; }
        </style>
    </head>
    <body>
        <div class="container">
            <h1>📧 Jenkins 测试报告</h1>
            
            <h2>📋 构建信息</h2>
            <div class="info-box">
                <div class="info-row"><span class="info-label">构建编号:</span> #${buildInfo.buildNumber}</div>
                <div class="info-row"><span class="info-label">构建状态:</span> <span class="${buildInfo.status == 'SUCCESS' ? 'success' : 'failure'}">${buildInfo.status}</span></div>
                <div class="info-row"><span class="info-label">触发用户:</span> ${buildInfo.triggerUser}</div>
                <div class="info-row"><span class="info-label">构建时间:</span> ${buildInfo.buildTime}</div>
                <div class="info-row"><span class="info-label">构建时长:</span> ${buildInfo.duration}</div>
                <div class="info-row"><span class="info-label">构建链接:</span> <a href="${buildInfo.buildUrl}">${buildInfo.buildUrl}</a></div>
                <div class="info-row"><span class="info-label">作业链接:</span> <a href="${buildInfo.jobUrl}">${buildInfo.jobUrl}</a></div>
                <div class="info-row"><span class="info-label">Git 分支:</span> ${buildInfo.gitBranch}</div>
                <div class="info-row"><span class="info-label">Git 提交:</span> ${buildInfo.gitCommit}</div>
            </div>
            
            <h2>📊 测试摘要</h2>
            <div class="summary-box">
                <div class="summary-item"><strong>总测试数:</strong> ${testSummary.total}</div>
                <div class="summary-item"><span class="success">✅ 通过:</span> ${testSummary.passed}</div>
                <div class="summary-item"><span class="failure">❌ 失败:</span> ${testSummary.failed}</div>
                <div class="summary-item"><span class="skipped">⏭️ 跳过:</span> ${testSummary.skipped}</div>
                <div class="summary-item"><strong>通过率:</strong> ${testSummary.passRate}%</div>
            </div>
            
            <h2>📝 测试用例详细信息</h2>
            ${testCases.table}
            
            <div class="footer">
                <p>此邮件由 Jenkins 自动发送，请勿回复。</p>
                <p>生成时间: ${new Date().format("yyyy-MM-dd HH:mm:ss")}</p>
            </div>
        </div>
    </body>
    </html>
    """
    
    return html
}

/**
 * 获取构建信息
 */
def getBuildInfo() {
    def buildNumber = env.BUILD_NUMBER ?: 'N/A'
    def buildStatus = currentBuild.currentResult ?: 'UNKNOWN'
    def triggerUser = env.BUILD_USER ?: (currentBuild.getBuildCauses('hudson.model.Cause$UserIdCause')?.first()?.userId ?: '系统触发')
    def buildTime = new Date(currentBuild.startTimeInMillis).format("yyyy-MM-dd HH:mm:ss")
    def duration = currentBuild.durationString ?: 'N/A'
    def buildUrl = env.BUILD_URL ?: 'N/A'
    def jobUrl = env.JOB_URL ?: 'N/A'
    
    // 获取Git信息
    def gitBranch = 'N/A'
    def gitCommit = 'N/A'
    try {
        gitBranch = sh(script: 'git rev-parse --abbrev-ref HEAD', returnStdout: true).trim()
        gitCommit = sh(script: 'git rev-parse --short HEAD', returnStdout: true).trim()
    } catch (Exception e) {
        echo "无法获取Git信息: ${e.message}"
    }
    
    return [
        buildNumber: buildNumber,
        status: buildStatus,
        triggerUser: triggerUser,
        buildTime: buildTime,
        duration: duration,
        buildUrl: buildUrl,
        jobUrl: jobUrl,
        gitBranch: gitBranch,
        gitCommit: gitCommit
    ]
}

/**
 * 获取测试摘要信息
 */
def getTestSummary() {
    def total = 0
    def passed = 0
    def failed = 0
    def skipped = 0
    
    try {
        // 读取TestNG XML报告
        def testngXml = readFile('target/surefire-reports/testng-results.xml')
        def xml = new XmlParser().parseText(testngXml)
        
        // 解析统计信息
        def suite = xml.suite[0]
        if (suite) {
            total = (suite.'@total-tests' ?: '0').toInteger()
            passed = (suite.'@passed' ?: '0').toInteger()
            failed = (suite.'@failed' ?: '0').toInteger()
            skipped = (suite.'@skipped' ?: '0').toInteger()
        }
    } catch (Exception e) {
        echo "解析测试摘要失败: ${e.message}"
        // 尝试从JUnit报告解析
        try {
            def junitFiles = sh(script: 'find target/surefire-reports -name "*.xml" -type f', returnStdout: true).trim()
            if (junitFiles) {
                def lines = junitFiles.split('\n')
                for (def file : lines) {
                    try {
                        def xmlContent = readFile(file)
                        def xml = new XmlParser().parseText(xmlContent)
                        xml.testsuite.each { suite ->
                            total += (suite.'@tests' ?: '0').toInteger()
                            passed += (suite.'@passed' ?: '0').toInteger()
                            failed += (suite.'@failures' ?: '0').toInteger()
                            skipped += (suite.'@skipped' ?: '0').toInteger()
                        }
                    } catch (Exception ex) {
                        echo "解析文件 ${file} 失败: ${ex.message}"
                    }
                }
            }
        } catch (Exception ex) {
            echo "无法读取测试报告: ${ex.message}"
        }
    }
    
    def passRate = total > 0 ? String.format("%.2f", (passed * 100.0 / total)) : "0.00"
    
    return [
        total: total,
        passed: passed,
        failed: failed,
        skipped: skipped,
        passRate: passRate
    ]
}

/**
 * 获取测试用例详细信息
 */
def getTestCasesDetails() {
    def testCases = []
    
    try {
        // 读取TestNG XML报告
        def testngXml = readFile('target/surefire-reports/testng-results.xml')
        def xml = new XmlParser().parseText(testngXml)
        
        def caseId = 1
        xml.suite.test.class.testMethod.each { method ->
            def className = method.parent().'@name' ?: 'N/A'
            def methodName = method.'@name' ?: 'N/A'
            def status = method.'@status' ?: 'UNKNOWN'
            def duration = method.'@duration-ms' ?: '0'
            def durationSeconds = String.format("%.3f", (duration.toDouble() / 1000))
            
            // 获取描述信息
            def description = method.'@description' ?: ''
            if (!description && methodName.contains('_')) {
                description = methodName.replace('_', ' ')
            }
            
            testCases.add([
                id: caseId++,
                name: methodName,
                className: className,
                description: description,
                duration: durationSeconds + 's',
                status: status
            ])
        }
    } catch (Exception e) {
        echo "解析TestNG报告失败，尝试解析JUnit报告: ${e.message}"
        
        // 尝试从JUnit报告解析
        try {
            def junitFiles = sh(script: 'find target/surefire-reports -name "TEST-*.xml" -type f', returnStdout: true).trim()
            if (junitFiles) {
                def caseId = 1
                def lines = junitFiles.split('\n')
                for (def file : lines) {
                    try {
                        def xmlContent = readFile(file)
                        def xml = new XmlParser().parseText(xmlContent)
                        xml.testsuite.testcase.each { testcase ->
                            def className = testcase.'@classname' ?: 'N/A'
                            def methodName = testcase.'@name' ?: 'N/A'
                            def duration = testcase.'@time' ?: '0'
                            
                            // 判断状态
                            def status = 'PASS'
                            if (testcase.failure.size() > 0) {
                                status = 'FAIL'
                            } else if (testcase.skipped.size() > 0) {
                                status = 'SKIP'
                            }
                            
                            testCases.add([
                                id: caseId++,
                                name: methodName,
                                className: className,
                                description: methodName.replace('_', ' '),
                                duration: duration + 's',
                                status: status
                            ])
                        }
                    } catch (Exception ex) {
                        echo "解析文件 ${file} 失败: ${ex.message}"
                    }
                }
            }
        } catch (Exception ex) {
            echo "无法读取测试报告: ${ex.message}"
            // 如果无法解析，至少返回一个提示
            testCases.add([
                id: 1,
                name: '无法解析测试报告',
                className: 'N/A',
                description: '请检查测试报告文件是否存在',
                duration: 'N/A',
                status: 'UNKNOWN'
            ])
        }
    }
    
    // 生成HTML表格
    def tableHtml = """
    <table>
        <thead>
            <tr>
                <th>序号</th>
                <th>测试用例ID</th>
                <th>测试用例名称</th>
                <th>类名</th>
                <th>描述</th>
                <th>执行时间</th>
                <th>执行结果</th>
            </tr>
        </thead>
        <tbody>
    """
    
    if (testCases.isEmpty()) {
        tableHtml += """
            <tr>
                <td colspan="7" style="text-align: center; color: #6c757d;">暂无测试用例数据</td>
            </tr>
        """
    } else {
        testCases.each { testCase ->
            def statusClass = 'status-pass'
            def statusText = '✅ 通过'
            def statusEmoji = '✅'
            
            if (testCase.status == 'FAIL' || testCase.status == 'FAILURE') {
                statusClass = 'status-fail'
                statusText = '❌ 失败'
                statusEmoji = '❌'
            } else if (testCase.status == 'SKIP' || testCase.status == 'SKIPPED') {
                statusClass = 'status-skip'
                statusText = '⏭️ 跳过'
                statusEmoji = '⏭️'
            }
            
            tableHtml += """
            <tr>
                <td>${testCase.id}</td>
                <td>TC-${String.format("%03d", testCase.id)}</td>
                <td>${testCase.name}</td>
                <td>${testCase.className}</td>
                <td>${testCase.description}</td>
                <td>${testCase.duration}</td>
                <td class="${statusClass}">${statusText}</td>
            </tr>
            """
        }
    }
    
    tableHtml += """
        </tbody>
    </table>
    """
    
    return [table: tableHtml, cases: testCases]
}

