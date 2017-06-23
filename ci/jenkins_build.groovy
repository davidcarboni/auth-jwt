node("slave") {

    stage("Checkout code") {
        checkout scm
    }
}