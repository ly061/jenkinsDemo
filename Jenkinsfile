pipeline {
    agent any
    
    tools {
        // 配置 Maven 和 JDK
        maven 'Maven-3.9.9'  // 根据你的Jenkins中配置的Maven名称调整
        jdk 'JDK-17'          // 根据你的Jenkins中配置的JDK名称调整
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
                    // 如果使用Git，取消下面的注释
                    // checkout scm
                    // 如果是本地项目，可以跳过这一步或使用其他方式
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
                    publishHTML([
                        reportDir: 'target/surefire-reports',
                        reportFiles: 'index.html',
                        reportName: 'TestNG 测试报告',
                        keepAll: true
                    ])
                    
                    // 归档测试报告
                    archiveArtifacts artifacts: 'target/surefire-reports/**/*', fingerprint: true
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

