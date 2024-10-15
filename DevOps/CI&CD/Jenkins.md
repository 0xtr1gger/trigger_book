In the contemporary landscape of software development, the demand for efficient and reliable Continuous Integration and Continuous Deployment (CI/CD) processes has grown significantly. 

Jenkins, an open-source automation server, has emerged as a pivotal tool in facilitating these processes. Originally developed by Kohsuke Kawaguchi in 2011, Jenkins enables developers to automate the building, testing, and deployment of applications.
With its robust architecture and principles of operation, Jenkins exemplifies the key objectives that CI/CD systems strive to achieve.

Jenkins is primary used to automate building, testing, and deployment of software using CI/CD pipelines. However, it is not just limited to creating pipelines: Jenkins can be used to automate any task. 

This article aims to explore the foundational principles of Jenkins and architecture. It seeks to provide both theoretical understanding and practical guidance for leveraging the tool for CI/CD automation.
## Jenkins

>[Jenkins](https://www.jenkins.io) is an open-source automation server written in Java. It is primarily used to automate the building, testing, and deployment of software with CI/CD (Continuous Integration and Continuous Delivery/Deployment) pipelines.

- Jenkins provides a web-based GUI that can be used to create jobs and customize all necessary functionality, including source control management, pre- and post-build actions, as well as build triggers. This allows to configure pipelines to be triggered automatically, or run tasks by demand just by clicking a button.

Jenkins comes with several advantages that make it stand out among its competitors, such as Travis, Bamboo, and CircleCI. To name a few,
- Open-source and free
	- Jenkins is available without any cost, allowing anyone to use, modify, and distribute it. Jenkins GitHub repository is available [here](https://github.com/jenkinsci/jenkins).
- Customizable and flexible
- Highly extendable with plugins
	- Jenkins supports a vast array of plugins, allowing for integration with many external tools and services. 
- Has an active and supportive community
	- A large and vibrant community contributes to ongoing improvements and offers support.

Thanks to plugins, Jenkins can integrate seamlessly with numerous industry tools, including source code management systems (like Git and GitHub), containerization platforms (like Docker), cloud services (AWS, GCP, Azure), and configuration management tools (like Ansible, Chef, Puppet).

Jenkins has innumerable use-cases provided by an extensive set of community-driven plugins. Even beyond CI/CD, it can be utilized to automate almost any task. For example,

- Continuous Integration and Continuous Delivery/Deployment (CI/CD)
	- Automating of the entire CI/CD workflow with automatic deployment of applications to various environments, including development, testing, and production.

- Automated testing
	- Scheduling and running various types of tests (unit, integration, performance) and automatically reporting results.

- Monitoring and reporting
	- Integrating with monitoring tools to collect metrics and generate reports on application performance during the build, test, and deployment stages.

- Infrastructure as Code (IaC)
	- Automating infrastructure configuration, management, and provisioning using tools like Terraform or Ansible

- Scheduled jobs 
	- Automating routine tasks, such as backups, data migrations, or report generation.

- Container management
	- Integrating with Docker to automate the building, testing, and deployment of containerized applications.

- Machine Learning (ML) pipelines
	- Automating the training, evaluation, and deployment of ML models by integrating with tools like TensorFlow or PyTorch.

- Static code analysis
	- Performing static code analysis by running tools like SonarQube to ensure code quality and adherence to standards.

Jenkins can be installed on various platforms, including Linux, Windows, and macOS, and is also available as a Docker image.
## Jenkins infrastructure and the principles of work

Jenkins infrastructure consists of two primary components:
- Master Server
- Agents

The Master Server is responsible for controlling pipelines and schedule builds, tests, and other tasks to Agents, and then Agents execute these tasks. All the configuration, scripts, commands, and CI/CD pipelines are stored on the Jenkins Master.

- Master Node
	- A Master Node (also referred to as the Controller) is the primary node responsible for managing and coordinating the build process.
	- It serves as the central point of control for all tasks and workflows, and provides a web interface for managing and monitoring builds.

- Agents/Minions
	- A Jenkins Agents, or a Node, is a worker node that executes tasks and builds assigned by the Jenkins Master, and then reports the results back.

There are two ways for the Master Node and Agents to communicate:

- Via SSH on port `22`, where the Master initiates the connection.
- Via JNLP (Java Network Launch Protocol) on port `50000`, where Agents initiate the connection.
## Jobs

- Jenkins uses project, also known as jobs, to perform its work. Projects are defined and run by Jenkins users.
	- [Documentation](https://www.jenkins.io/doc/book/using/working-with-projects/)

>In Jenkins, job, or a project, is a specific task or a series of tasks that Jenkins can execute, such as compiling source code, running tests, building packages, or deploying applications. 

There are several different types of Jobs in Jenkins. The two of most commonly used ones include Freestyle jobs and Pipeline jobs.

- Freestyle Jobs
	- A Jenkins Freestyle Job is a traditional, script-based job that executes a series of steps, such as building, testing, and deploying a project.
	- Freestyle jobs are defined using a Groovy script, which specifies the steps to be executed. Steps are used sequentially, with no supported parallelism.  
	- Freestyle jobs are easy-to-use for single, simple tasks, however limited in configuration options. They are not suitable for complex projects, and are error-prone due to manual scripting.

- Pipeline Jobs
	- A Jenkins Pipeline is a declarative, YAML-based configuration that defines a CI/CD workflow. Pipeline steps and their dependencies are defined in a YAML file, and can be executed in parallel. 
	- Pipelines offer extensive configuration options, making it easier to manage complex workflows and integrate with various tools.

## Pipelines

- Jenkins Pipeline is a suite of plugins which supports implementing and integrating continuous delivery pipelines into Jenkins. 
	- [Documentation](https://www.jenkins.io/doc/book/pipeline/)

>A Pipeline is a set of automated processes that define how software is build, tested, and deployed. A pipeline in Jenkins consists of a series of jobs.

- In other words, a pipeline is a series of steps the Jenkins server will execute to complete the necessary tasks of the CI/CD process. 

An example of a Jenkins CI/CD pipeline workflow, correlated to a standard CI/CD pipeline, may look like this:

1. Source code
	- The Jenkins CI server continuously monitors the source code repository developers work on for new commits. Modifications to the source, i.e., commits, serve as build triggers.

>Pipeline triggers are events or conditions that initiate the execution of a CI/CD pipeline. Triggers automate the deployment process by responding to specific actions or changes, such as changes in source code repository. Builds can also be triggered manually, using the GUI. 

2. Build
	- Upon detecting a new commit, Jenkins pulls the changes from the repository and assigns an Agent to build the new code version. If successful, the build generates necessary executables/containers; in case of a failure, feedback is provided through logs or a messaging system.
	
3. Test
	- The newly built version undergoes a series of automated tests. In the case of test failures, developers are immediately alerted.

4. Deploy
	- If all tests are passed, the code is typically deployed to a staging or production environment, depending on the deployment practices a developer team uses. 

Pipelines are saved in text files called Jenkinsfiles. The Jenkinsfile utilizes a syntax similar to JSON, with curly brackets demarcating pipeline steps.

Jenkins supports two types of pipelines: scripted and declarative pipelines. Both achieve the same goal, but differ in syntax, flexibility, and usage. 

- Scripted pipelines
	- Scripted Pipelines use Groovy syntax for defining workflows (a JVM-based programming language); Groovy code can be injected into the pipelines anytime. Scripted pipelines are considered more complex due to implementing imperative programming approach, but provide a lot of flexibility and control compared to Declarative Pipelines.

```Groovy
node {  
    stage('Build') {  
        // Build the application  
        sh 'mvn clean install'  
    }  
    stage('Test') {  
        // Run the tests  
        sh 'mvn test'  
    }  
    stage('Deploy') {  
        // Deploy the application  
        sh 'deploy.sh'  
    }  
}
```

- Declarative pipelines
	- Declarative Pipelines are newer in Jenkins. They are easier to use and understand because of their simple and structured syntax. Declarative pipelines use declarative programming approach. Such pipelines are configured in a manner that clearly outlines the stages and steps.

```Groovy
pipeline {  
    agent any  
    stages {  
        stage('Build') {  
            steps {  
                // Build the application  
                sh 'mvn clean install'  
            }  
        }  
        stage('Test') {  
            steps {  
                // Run the tests  
                sh 'mvn test'  
            }  
        }  
        stage('Deploy') {  
            steps {  
                // Deploy the application  
                sh 'deploy.sh'  
            }  
        }  
    }  
}
```

For simplicity, the declarative syntax is often preferred when creating Jenkins pipelines.

- Jenkinsfiles may either be generated using a web Graphical User Interface (GUI) or manually writing code.
## Jenkins plugins

>Jenkins plugins are extensions that enhance the functionality of the Jenkins CI/CD automation server. With over 1800 community-contributed plugins, Jenkins provides a vast array of features and integrations to support building, deploying, and automating any project.

Examples of common plugins include:
- Git Plugin
- Kubernetes Plugin
- Docker Plugin
- Jira Plugin
- And more

For example, the AWS Jenkins plugin can be used to integrate AWS CLI with Jenkins and upload files to an S3 bucket automatically as a part of a Jenkins pipeline.

- [Jenkins Plugins Index](https://plugins.jenkins.io/)
	- The Plugin Index is a comprehensive list of all published plugins. 

>Jenkins plugins are generally located in the `/var/lib/jenkins` directory on the Master Node.

Jenkins files can be installed with a command line, by copying them into the plugin directory, or using a Jenkins Web GUI.

>Jenkins provides a web-based interface allows users to create jobs, configure settings, and monitor builds. Users can easily view build history, logs, and results via this interface.
## Working with Jenkins

#### Installation and configuration

Jenkins may operate as a server on various operating systems, including Windows, macOS, and, most notably, Linux. Jenkins requires a Java 8 virtual machine or higher; it can also run on Oracle JRE or OpenJDK. Jenkins can also be installed in a Docker container or run in a Kubernetes cluster.

Jenkins Documentation includes a comprehensive guidance on how to install Jenkins on different platforms and solutions. It can be found here: https://www.jenkins.io/doc/book/installing/linux/.
###### Installing and running Jenkins in Docker

The easiest way to install and run Jenkins is by using Docker. This solution is cross-platform and suitable for use in containerized environments.

- The official Jenkins Docker image can be found by the name [`jenkins/jenkins` (DockerHub)](https://hub.docker.com/r/jenkins/jenkins) . This image contains the current LTS (Long-Term Support) Jenkins release. 

A Docker container with a Jenkins server can be created in two ways: either by specifying all the necessary arguments in the command line, including the Jenkins Docker image, or by building a new container image from a Dockerfile. 

A Jenkins container can be run with just one command:

```bash
docker run --name jenkins-container -p 8080:8080 -p 50000:50000 -d -v jenkins-data:/var/jenkins jenkins/jenkins
```

- `--name jenkins-container` sets a name for the container.
- `-p host_port:container_port` maps, or publishes, a host port to a container port, providing access to the application inside the container.

- Port `8080`
	- The default port Jenkins runs on. The Jenkins dashboard, the web GUI, listens on this port.
- Port `50000`
	- The default port used for communication between the Jenkins master and agents.

- `-v jenkins-data:/var/jenkins_home` binds a volume named `jenkins-data` to the `/var/jenkins_home` directory inside the container. The volume will be automatically created. 
- `jenkins/jenkins` specifies the Jenkins Docker image.

>The `/var/jenkins_home` directory is the directory where all the Jenkins builds and configurations will be stored. 

After the above command, the Jenkins container should be up and running.

```bash
docker ps
```

```bash
CONTAINER ID   IMAGE             COMMAND                  CREATED         STATUS         PORTS                                                                                      NAMES
a59be68f440c   jenkins/jenkins   "/usr/bin/tini -- /u…"   4 seconds ago   Up 3 seconds   0.0.0.0:8080->8080/tcp, :::8080->8080/tcp, 0.0.0.0:50000->50000/tcp, :::50000->50000/tcp   jenkins-container

```

---

In order to install additional software inside the Jenkins container, it is more convenient to build a separate Docker container image, based on `jenkins:jenkins`, and specify all the necessary packages to be installed during the image build in the Dockerfile.

```Dockerfile
FROM jenkins/jenkins
RUN apt update
RUN jenkins-plugin-cli --plugins git
```

- After the build, the image above will contain the Git plugin installed with the `jenkins-plugin-cli` command.

To build the image:

```bash
docker build -t jenkins-image .
```

---
#### Accessing Jenkins dashboard

After Jenkins container is launched, the GUI web interface is accessible from the localhost IP address (`127.0.0.1` or `localhost`) on port `8080`:

```bash
http://127.0.0.1
```

Upon accessing, Jenkins will prompt for a password. 

![jenkins_login](https://github.com/user-attachments/assets/880a4e15-f70d-4253-8ab6-3aac8957ec0e)

The password can be found at `/var/jenkins_home/secrets/initialAdminPassword`:

```bash
docker exec -it jenkins-container cat /var/jenkins_home/secrets/initialAdminPassword
```
```
<the password will be displayed>
```

After authorization, the dashboard displays a panel which allows the user to choose either to install suggested plugins or choose what to install manually. For a general setup, the former options is usually suitable.  

![customize_jenkins](https://github.com/user-attachments/assets/ed7f57d0-ab2c-4222-990f-62d8e0cb80db)

With `Install suggested plugins` selected, Jenkins will start the installation of commonly used software.

![installing_plugins_jenkins](https://github.com/user-attachments/assets/0cf2eb75-0775-46f9-a23d-df904a0bb2a2)

Then, Jenkins will suggest to create an admin user.

![jenkins_dashboard_create_user](https://github.com/user-attachments/assets/86ead062-bc84-4f9d-b55b-e1e83c141091)

After the user has been created, Jenkins allows to customize the URL used to access the dashboard:.

![instance_configuration](https://github.com/user-attachments/assets/f257cb48-0f2d-4dd1-8941-3005ba8d1314)

After the above configuration, the Jenkins setup is complete and the dashboard ready for use.

![jenkins_is_ready](https://github.com/user-attachments/assets/8a50e704-ef11-43ff-95d1-c01335eba025)
![jenkins_dashboard](https://github.com/user-attachments/assets/6d19e4b5-1db5-4908-a06e-3dc32a93044b)

