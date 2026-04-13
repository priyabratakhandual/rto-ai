pipeline {
    agent any

    environment {
        DOCKER_IMAGE = "priyabratakhandual/rto-ai"
        BUILD_TAG = "${BUILD_NUMBER}"
        CONTAINER_NAME = "rto-ai"
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

        stage('Deploy Locally') {
            steps {
                sh '''
                echo "Pull latest image"
                docker pull $DOCKER_IMAGE:latest

                echo "Stop and remove old container"
                docker stop $CONTAINER_NAME || true
                docker rm $CONTAINER_NAME || true

                echo "Run new container"
                docker run -d \
                -p 5000:5000 \
                --name $CONTAINER_NAME \
                $DOCKER_IMAGE:latest
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