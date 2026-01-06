pipeline {
  agent any

  environment {
    BACKEND_DIR    = "enterprise_ka"
    FRONTEND_DIR   = "enterprise_ka_frontend"
    BACKEND_IMAGE  = "enterprise-ka-backend:${env.BUILD_NUMBER}"
    FRONTEND_IMAGE = "enterprise-ka-frontend:${env.BUILD_NUMBER}"
  }

  stages {
    stage("Checkout") {
      steps {
        checkout scm
      }
    }

    stage("Backend | Install & Test") {
      steps {
        dir(env.BACKEND_DIR) {
          sh """
            python -m venv .venv
            . .venv/bin/activate
            pip install --upgrade pip
            pip install -r requirements.txt
            python -m pytest
          """
        }
      }
    }

    stage("Backend | Docker Build") {
      steps {
        dir(env.BACKEND_DIR) {
          sh "docker build -t ${BACKEND_IMAGE} ."
        }
      }
    }

    stage("Frontend | Install & Build") {
      steps {
        dir(env.FRONTEND_DIR) {
          sh """
            npm ci || npm install
            npm run build
          """
        }
      }
    }

    stage("Frontend | Docker Build") {
      steps {
        dir(env.FRONTEND_DIR) {
          sh "docker build -t ${FRONTEND_IMAGE} ."
        }
      }
    }
  }

  post {
    always {
      echo "Backend image: ${BACKEND_IMAGE}"
      echo "Frontend image: ${FRONTEND_IMAGE}"
    }
  }
}
