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

![jenkins_is_ready](https://github.com/user-attachments/assets/8a50e704-ef11-43ff-95d1-c01335eba025)
![jenkins_dashboard](https://github.com/user-attachments/assets/6d19e4b5-1db5-4908-a06e-3dc32a93044b)

## Conclusion

In conclusion, Jenkins stands out as a powerful and versatile automation server that is crucial for organizations seeking to enhance their software development practices through CI/CD pipelines. Its robust architecture, extensive plugin ecosystem, and strong community support enable teams to not only automate the building, testing, and deployment of applications but also to streamline various other tasks, paving the way for improved efficiency and reliability in software delivery.

By leveraging Jenkins effectively, developers can create complex workflows tailored to their specific needs, allowing for rapid iterations and faster time-to-market. Understanding the foundational principles of Jenkins, from its master-agent structure to the nuances of job types and pipelines, equips teams with the knowledge necessary to harness this tool's full potential. As we continue to transition towards more automated and DevOps-centric methodologies, Jenkins remains a critical asset in achieving excellence in modern software development practices. Thus, embracing Jenkins not only fosters a culture of continuous improvement but also positions organizations to thrive in a highly competitive landscape.


