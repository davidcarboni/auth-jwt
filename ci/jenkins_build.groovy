node("slave") {

    stage("Checkout code") {
        checkout scm
    }

    stage("Build container image") {
        dockerBuild()
    }

    stage("Build container image") {
        dockerRun()
    }

}

def dockerBuild() {
    sh "sudo docker build --tag auth ."
}

def dockerBuild() {
    sh "sudo docker rm -f auth || echo No instance running."
    sh "sudo docker run -d --name auth -p 5000:5000 auth"
}