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
            echo '🎉 Pipeline 执行成功！'
            // 可以在这里添加通知，如发送邮件、Slack通知等
            // emailext (
            //     subject: "✅ TestNG 测试通过: ${env.JOB_NAME} - ${env.BUILD_NUMBER}",
            //     body: "所有测试用例都已通过。",
            //     to: "your-email@example.com"
            // )
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

