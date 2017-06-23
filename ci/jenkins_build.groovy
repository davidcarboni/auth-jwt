node("slave") {

    stage("Checkout code") {
        checkout scm
    }

    stage("Build container image") {
        dockerBuild()
    }

}

def dockerBuild() {
    sh "sudo docker build --tag auth ."
}