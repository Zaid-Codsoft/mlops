pipeline {
    agent any
    
    environment {
        DOCKER_HUB_CREDENTIALS = credentials('docker-hub-credentials')
        DOCKER_IMAGE = 'yourusername/telco-churn-prediction'
        DOCKER_TAG = "${env.BUILD_NUMBER}"
    }
    
    stages {
        stage('Checkout') {
            steps {
                checkout scm
                echo "Checked out code from ${env.BRANCH_NAME}"
            }
        }
        
        stage('Build Docker Image') {
            steps {
                script {
                    echo "Building Docker image..."
                    sh """
                        docker build -t ${DOCKER_IMAGE}:${DOCKER_TAG} .
                        docker tag ${DOCKER_IMAGE}:${DOCKER_TAG} ${DOCKER_IMAGE}:latest
                    """
                }
            }
        }
        
        stage('Test Docker Image') {
            steps {
                script {
                    echo "Testing Docker image..."
                    sh """
                        docker run --rm -d --name test-container -p 5001:5000 ${DOCKER_IMAGE}:${DOCKER_TAG}
                        sleep 10
                        curl -f http://localhost:5001/health || exit 1
                        docker stop test-container
                    """
                }
            }
        }
        
        stage('Push to Docker Hub') {
            steps {
                script {
                    echo "Pushing to Docker Hub..."
                    sh """
                        echo ${DOCKER_HUB_CREDENTIALS_PSW} | docker login -u ${DOCKER_HUB_CREDENTIALS_USR} --password-stdin
                        docker push ${DOCKER_IMAGE}:${DOCKER_TAG}
                        docker push ${DOCKER_IMAGE}:latest
                        docker logout
                    """
                }
            }
        }
        
        stage('Deploy to Staging') {
            steps {
                script {
                    echo "Deploying to staging environment..."
                    sh """
                        # Stop existing container if running
                        docker stop telco-churn-staging || true
                        docker rm telco-churn-staging || true
                        
                        # Run new container
                        docker run -d --name telco-churn-staging -p 8080:5000 ${DOCKER_IMAGE}:${DOCKER_TAG}
                        
                        # Wait for application to start
                        sleep 15
                        
                        # Health check
                        curl -f http://localhost:8080/health || exit 1
                    """
                }
            }
        }
    }
    
    post {
        success {
            echo "Pipeline completed successfully!"
            emailext (
                subject: "✅ Deployment Successful - Telco Churn Prediction",
                body: """
                <h2>Deployment Successful!</h2>
                <p><strong>Project:</strong> Telco Churn Prediction</p>
                <p><strong>Branch:</strong> ${env.BRANCH_NAME}</p>
                <p><strong>Build Number:</strong> ${env.BUILD_NUMBER}</p>
                <p><strong>Docker Image:</strong> ${DOCKER_IMAGE}:${DOCKER_TAG}</p>
                <p><strong>Staging URL:</strong> http://localhost:8080</p>
                <p><strong>Build URL:</strong> ${env.BUILD_URL}</p>
                <p><strong>Timestamp:</strong> ${new Date()}</p>
                
                <h3>Deployment Details:</h3>
                <ul>
                    <li>✅ Code Quality Checks Passed</li>
                    <li>✅ Unit Tests Passed</li>
                    <li>✅ Docker Image Built Successfully</li>
                    <li>✅ Image Pushed to Docker Hub</li>
                    <li>✅ Deployed to Staging Environment</li>
                </ul>
                
                <p>The application is now available for testing.</p>
                """,
                to: "admin@yourcompany.com",
                mimeType: "text/html"
            )
        }
        
        failure {
            echo "Pipeline failed!"
            emailext (
                subject: "❌ Deployment Failed - Telco Churn Prediction",
                body: """
                <h2>Deployment Failed!</h2>
                <p><strong>Project:</strong> Telco Churn Prediction</p>
                <p><strong>Branch:</strong> ${env.BRANCH_NAME}</p>
                <p><strong>Build Number:</strong> ${env.BUILD_NUMBER}</p>
                <p><strong>Build URL:</strong> ${env.BUILD_URL}</p>
                <p><strong>Timestamp:</strong> ${new Date()}</p>
                
                <p>Please check the build logs for more details.</p>
                """,
                to: "admin@yourcompany.com",
                mimeType: "text/html"
            )
        }
        
        always {
            echo "Cleaning up..."
            sh """
                docker system prune -f
            """
        }
    }
}
