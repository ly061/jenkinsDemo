pipeline {
    agent any
    
    // 方案1：使用 Jenkins 配置的工具（推荐）
    // 如果 Jenkins 中已配置 Maven 和 JDK 工具，取消下面的注释并修改工具名称
    // tools {
    //     maven 'Maven-3.9.9'  // 请根据你的Jenkins配置调整
    //     jdk 'JDK-17'          // 请根据你的Jenkins配置调整
    // }
    
    options {
        buildDiscarder(logRotator(numToKeepStr: '10'))
        timeout(time: 30, unit: 'MINUTES')
        timestamps()
    }
    
    environment {
        EMAIL_RECIPIENTS = '17381915093@163.com'
        PROJECT_NAME = 'WEAZL TestNG 自动化测试'
        // 使用环境变量指定 Maven 和 Java 路径（已自动检测并配置）
        MAVEN_HOME = '/Users/joe/Documents/tools/apache-maven-3.9.9'
        JAVA_HOME = '/Users/joe/Documents/tools/jdk-17.0.2.jdk/Contents/Home'
        PATH = "${MAVEN_HOME}/bin:${JAVA_HOME}/bin:${env.PATH}"
    }
    
    stages {
        stage('环境检查') {
            steps {
                script {
                    echo '=== 检查环境 ==='
                    sh 'java -version'
                    sh 'mvn -version'
                }
            }
        }
        
        stage('清理') {
            steps {
                script {
                    echo '=== 清理构建目录 ==='
                    sh 'mvn clean'
                }
            }
        }
        
        stage('编译') {
            steps {
                script {
                    echo '=== 编译项目 ==='
                    sh 'mvn compile test-compile'
                }
            }
        }
        
        stage('执行测试') {
            steps {
                script {
                    echo '=== 运行 TestNG 测试 ==='
                    // 即使测试失败也继续执行
                    sh 'mvn test || true'
                }
            }
            post {
                always {
                    script {
                        // 发布JUnit测试结果
                        junit allowEmptyResults: true, testResults: 'target/surefire-reports/*.xml'
                        
                        // 发布HTML报告（如果有HTML Publisher插件）
                        try {
                            publishHTML([
                                reportDir: 'target/surefire-reports',
                                reportFiles: 'index.html',
                                reportName: 'TestNG HTML报告',
                                alwaysLinkToLastBuild: true,
                                allowMissing: true,
                                keepAll: true
                            ])
                        } catch (Exception e) {
                            echo "HTML Publisher插件未安装，跳过HTML报告发布"
                        }
                        
                        // 归档测试报告
                        archiveArtifacts artifacts: 'target/surefire-reports/**/*', allowEmptyArchive: true
                    }
                }
            }
        }
        
        stage('生成测试报告') {
            steps {
                script {
                    echo '=== 生成详细测试报告 ==='
                    // 创建解析TestNG结果的脚本
                    writeFile file: 'parse_testng_results.groovy', text: '''
import groovy.xml.XmlSlurper
import java.text.SimpleDateFormat

def parseTestNGResults() {
    def reportData = [
        totalTests: 0,
        passed: 0,
        failed: 0,
        skipped: 0,
        totalTime: 0,
        testCases: []
    ]
    
    try {
        // 查找所有XML测试结果文件
        def xmlFiles = new File('target/surefire-reports').listFiles().findAll { 
            it.name.endsWith('.xml') && it.name.startsWith('TEST-')
        }
        
        xmlFiles.each { xmlFile ->
            def xml = new XmlSlurper().parse(xmlFile)
            
            xml.testcase.each { testcase ->
                def testInfo = [
                    id: testcase.@name.text(),
                    className: testcase.@classname.text(),
                    name: testcase.@name.text(),
                    time: testcase.@time.text(),
                    status: 'PASSED'
                ]
                
                // 检查是否失败
                if (testcase.failure.size() > 0) {
                    testInfo.status = 'FAILED'
                    testInfo.errorMessage = testcase.failure.@message.text()
                    testInfo.errorDetail = testcase.failure.text()
                    reportData.failed++
                }
                // 检查是否跳过
                else if (testcase.skipped.size() > 0) {
                    testInfo.status = 'SKIPPED'
                    testInfo.skipReason = testcase.skipped.@message.text()
                    reportData.skipped++
                }
                else {
                    reportData.passed++
                }
                
                reportData.testCases << testInfo
                reportData.totalTests++
                reportData.totalTime += (testcase.@time.text() as Double)
            }
        }
    } catch (Exception e) {
        println "解析测试结果时出错: ${e.message}"
        e.printStackTrace()
    }
    
    return reportData
}

// 执行解析
def results = parseTestNGResults()

// 保存为JSON供后续使用
def jsonOutput = new groovy.json.JsonBuilder(results).toPrettyString()
new File('test-results.json').text = jsonOutput

println "测试结果已保存到 test-results.json"
return results
'''
                    
                    // 执行解析脚本
                    def results = load 'parse_testng_results.groovy'
                    
                    // 保存测试结果供邮件使用
                    env.TEST_RESULTS = groovy.json.JsonOutput.toJson(results)
                }
            }
        }
    }
    
    post {
        always {
            script {
                echo '=== 发送测试报告邮件 ==='
                sendDetailedEmailReport()
            }
        }
    }
}

def sendDetailedEmailReport() {
    // 解析测试结果
    def testResults = null
    try {
        def jsonText = readFile('test-results.json')
        testResults = new groovy.json.JsonSlurper().parseText(jsonText)
    } catch (Exception e) {
        echo "无法读取测试结果: ${e.message}"
        testResults = [
            totalTests: 0,
            passed: 0,
            failed: 0,
            skipped: 0,
            totalTime: 0,
            testCases: []
        ]
    }
    
    // 构建状态
    def buildStatus = currentBuild.currentResult
    def buildColor = buildStatus == 'SUCCESS' ? '#28a745' : (buildStatus == 'UNSTABLE' ? '#ffc107' : '#dc3545')
    def statusEmoji = buildStatus == 'SUCCESS' ? '✅' : (buildStatus == 'UNSTABLE' ? '⚠️' : '❌')
    
    // 构建详细的测试用例表格
    def testCasesTableRows = ''
    testResults.testCases.eachWithIndex { testCase, index ->
        def statusIcon = testCase.status == 'PASSED' ? '✅' : (testCase.status == 'SKIPPED' ? '⏭️' : '❌')
        def statusColor = testCase.status == 'PASSED' ? '#28a745' : (testCase.status == 'SKIPPED' ? '#6c757d' : '#dc3545')
        def executionTime = String.format("%.3f", testCase.time as Double)
        
        def errorInfo = ''
        if (testCase.status == 'FAILED' && testCase.errorMessage) {
            errorInfo = """<br/><small style="color: #dc3545;">错误: ${testCase.errorMessage}</small>"""
        } else if (testCase.status == 'SKIPPED' && testCase.skipReason) {
            errorInfo = """<br/><small style="color: #6c757d;">跳过原因: ${testCase.skipReason}</small>"""
        }
        
        testCasesTableRows += """
            <tr>
                <td style="padding: 12px; border: 1px solid #dee2e6; text-align: center;">${index + 1}</td>
                <td style="padding: 12px; border: 1px solid #dee2e6;"><code>${testCase.id}</code></td>
                <td style="padding: 12px; border: 1px solid #dee2e6;">${testCase.name}${errorInfo}</td>
                <td style="padding: 12px; border: 1px solid #dee2e6;">${testCase.className}</td>
                <td style="padding: 12px; border: 1px solid #dee2e6; text-align: center;">${executionTime}s</td>
                <td style="padding: 12px; border: 1px solid #dee2e6; text-align: center;">
                    <span style="padding: 4px 12px; border-radius: 4px; background-color: ${statusColor}; color: white; font-weight: bold;">
                        ${statusIcon} ${testCase.status}
                    </span>
                </td>
            </tr>
        """
    }
    
    // 计算总执行时间
    def totalTimeFormatted = String.format("%.3f", testResults.totalTime)
    def passRate = testResults.totalTests > 0 ? 
        String.format("%.2f", (testResults.passed / testResults.totalTests) * 100) : '0.00'
    
    // 构建HTML邮件内容
    def emailBody = """
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <style>
        body {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            line-height: 1.6;
            color: #333;
            max-width: 1200px;
            margin: 0 auto;
            padding: 20px;
            background-color: #f5f5f5;
        }
        .container {
            background-color: white;
            border-radius: 8px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
            padding: 30px;
        }
        .header {
            background: linear-gradient(135deg, ${buildColor} 0%, ${buildColor}dd 100%);
            color: white;
            padding: 20px;
            border-radius: 8px 8px 0 0;
            margin: -30px -30px 30px -30px;
        }
        .header h1 {
            margin: 0;
            font-size: 28px;
        }
        .header p {
            margin: 10px 0 0 0;
            opacity: 0.9;
        }
        .section {
            margin-bottom: 30px;
        }
        .section h2 {
            color: #333;
            border-bottom: 2px solid ${buildColor};
            padding-bottom: 10px;
            margin-bottom: 20px;
        }
        .info-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
            gap: 15px;
            margin-bottom: 20px;
        }
        .info-card {
            background-color: #f8f9fa;
            padding: 15px;
            border-radius: 6px;
            border-left: 4px solid ${buildColor};
        }
        .info-card .label {
            font-size: 12px;
            color: #6c757d;
            text-transform: uppercase;
            letter-spacing: 0.5px;
            margin-bottom: 5px;
        }
        .info-card .value {
            font-size: 20px;
            font-weight: bold;
            color: #333;
        }
        .stats-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(150px, 1fr));
            gap: 15px;
            margin-bottom: 30px;
        }
        .stat-card {
            text-align: center;
            padding: 20px;
            border-radius: 8px;
            background-color: #f8f9fa;
        }
        .stat-card.total { border-top: 4px solid #007bff; }
        .stat-card.passed { border-top: 4px solid #28a745; }
        .stat-card.failed { border-top: 4px solid #dc3545; }
        .stat-card.skipped { border-top: 4px solid #6c757d; }
        .stat-card .number {
            font-size: 36px;
            font-weight: bold;
            margin: 10px 0;
        }
        .stat-card .label {
            font-size: 14px;
            color: #6c757d;
            text-transform: uppercase;
        }
        table {
            width: 100%;
            border-collapse: collapse;
            margin-top: 20px;
            background-color: white;
        }
        th {
            background-color: ${buildColor};
            color: white;
            padding: 12px;
            text-align: left;
            font-weight: 600;
        }
        .footer {
            margin-top: 30px;
            padding-top: 20px;
            border-top: 1px solid #dee2e6;
            text-align: center;
            color: #6c757d;
            font-size: 12px;
        }
        .footer a {
            color: ${buildColor};
            text-decoration: none;
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>${statusEmoji} ${env.PROJECT_NAME}</h1>
            <p>构建 #${env.BUILD_NUMBER} - ${buildStatus}</p>
        </div>
        
        <div class="section">
            <h2>📊 构建信息</h2>
            <div class="info-grid">
                <div class="info-card">
                    <div class="label">项目名称</div>
                    <div class="value">${env.JOB_NAME}</div>
                </div>
                <div class="info-card">
                    <div class="label">构建编号</div>
                    <div class="value">#${env.BUILD_NUMBER}</div>
                </div>
                <div class="info-card">
                    <div class="label">构建状态</div>
                    <div class="value" style="color: ${buildColor};">${statusEmoji} ${buildStatus}</div>
                </div>
                <div class="info-card">
                    <div class="label">构建时长</div>
                    <div class="value">${currentBuild.durationString.replace(' and counting', '')}</div>
                </div>
                <div class="info-card">
                    <div class="label">构建时间</div>
                    <div class="value">${new Date(currentBuild.startTimeInMillis).format('yyyy-MM-dd HH:mm:ss')}</div>
                </div>
                <div class="info-card">
                    <div class="label">构建节点</div>
                    <div class="value">${env.NODE_NAME}</div>
                </div>
            </div>
        </div>
        
        <div class="section">
            <h2>📈 测试统计</h2>
            <div class="stats-grid">
                <div class="stat-card total">
                    <div class="label">总用例数</div>
                    <div class="number" style="color: #007bff;">${testResults.totalTests}</div>
                </div>
                <div class="stat-card passed">
                    <div class="label">通过</div>
                    <div class="number" style="color: #28a745;">${testResults.passed}</div>
                </div>
                <div class="stat-card failed">
                    <div class="label">失败</div>
                    <div class="number" style="color: #dc3545;">${testResults.failed}</div>
                </div>
                <div class="stat-card skipped">
                    <div class="label">跳过</div>
                    <div class="number" style="color: #6c757d;">${testResults.skipped}</div>
                </div>
            </div>
            
            <div class="info-grid">
                <div class="info-card">
                    <div class="label">总执行时间</div>
                    <div class="value">${totalTimeFormatted} 秒</div>
                </div>
                <div class="info-card">
                    <div class="label">通过率</div>
                    <div class="value" style="color: ${testResults.failed > 0 ? '#dc3545' : '#28a745'};">${passRate}%</div>
                </div>
            </div>
        </div>
        
        <div class="section">
            <h2>📋 测试用例明细</h2>
            <table>
                <thead>
                    <tr>
                        <th style="text-align: center; width: 60px;">序号</th>
                        <th style="width: 200px;">用例ID</th>
                        <th>用例名称</th>
                        <th>测试类</th>
                        <th style="text-align: center; width: 100px;">执行时间</th>
                        <th style="text-align: center; width: 120px;">执行结果</th>
                    </tr>
                </thead>
                <tbody>
                    ${testCasesTableRows ?: '<tr><td colspan="6" style="text-align: center; padding: 20px; color: #6c757d;">暂无测试用例数据</td></tr>'}
                </tbody>
            </table>
        </div>
        
        <div class="footer">
            <p>
                <a href="${env.BUILD_URL}">查看完整构建日志</a> | 
                <a href="${env.BUILD_URL}testReport/">查看测试报告</a> | 
                <a href="${env.BUILD_URL}console">查看控制台输出</a>
            </p>
            <p>此邮件由 Jenkins 自动生成 - ${new Date().format('yyyy-MM-dd HH:mm:ss')}</p>
        </div>
    </div>
</body>
</html>
"""
    
    // 发送邮件
    try {
        emailext(
            to: env.EMAIL_RECIPIENTS,
            subject: "${statusEmoji} ${env.PROJECT_NAME} - 构建 #${env.BUILD_NUMBER} ${buildStatus}",
            body: emailBody,
            mimeType: 'text/html',
            attachLog: true,
            compressLog: true,
            attachmentsPattern: 'target/surefire-reports/*.xml'
        )
        echo "✅ 测试报告邮件已发送至 ${env.EMAIL_RECIPIENTS}"
    } catch (Exception e) {
        echo "❌ 发送邮件失败: ${e.message}"
        echo "请确保Jenkins已安装并配置了 Email Extension Plugin"
        echo "详细信息: https://plugins.jenkins.io/email-ext/"
    }
}

