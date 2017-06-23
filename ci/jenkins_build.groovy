node("slave") {

    stage("Checkout code") {
        checkout scm
    }

    stage("Build container image") {
        dockerBuild()
    }

def dockerBuild() {
    sh "docker build --tag auth ."
}

}