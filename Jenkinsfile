pipeline {
    agent any

    options {
        skipDefaultCheckout(true)
    }

    environment {
        DOCKER_IMAGE = "priyabratakhandual/rto-ai"
        BUILD_TAG = "${BUILD_NUMBER}"
    }

    stages {

        stage('Checkout Code') {
            steps {
                git branch: 'main', url: 'https://github.com/priyabratakhandual/rto-ai.git'
            }
        }

        stage('Build Docker Image') {
            steps {
                sh '''
                docker build --no-cache -t $DOCKER_IMAGE:latest .
                docker tag $DOCKER_IMAGE:latest $DOCKER_IMAGE:$BUILD_TAG
                '''
            }
        }

        stage('Login to Docker Hub') {
            steps {
                withCredentials([usernamePassword(
                    credentialsId: 'dockerhub-cred-id',
                    usernameVariable: 'DOCKER_USER',
                    passwordVariable: 'DOCKER_PASS'
                )]) {
                    sh '''
                    echo $DOCKER_PASS | docker login -u $DOCKER_USER --password-stdin
                    '''
                }
            }
        }

        stage('Push Image') {
            steps {
                sh '''
                docker push $DOCKER_IMAGE:latest
                docker push $DOCKER_IMAGE:$BUILD_TAG
                '''
            }
        }

        stage('Deploy with Docker Compose') {
            steps {
                sh '''
                echo "Stopping old single container (if exists)"
                docker stop rto-ai || true
                docker rm rto-ai || true

                echo "Stopping old compose setup"
                docker-compose down || true

                echo "Building and starting services (app + nginx)"
                docker-compose up -d --build
                '''
            }
        }

        stage('Verify Deployment') {
            steps {
                sh '''
                echo "Running containers:"
                docker ps
                '''
            }
        }

        stage('Cleanup') {
            steps {
                sh '''
                docker logout
                docker image prune -f
                '''
            }
        }
    }
}