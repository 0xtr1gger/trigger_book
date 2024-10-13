In the current fast-paced software development environment, the ability to deliver high-quality code quickly and efficiently is paramount. Continuous Integration (CI) and Continuous Deployment (CD) are two essential practices that facilitate this goal by automating the processes of code integration, testing, and deployment; CI/CD is one of the fundamental tenets of the DevOps process, a set of principles designed to deliver applications and services faster than with a traditional software development approach, while maintaining or improving the quality of the products. 

## CI/CD

>Continuous Integration and Continuous Delivery (CI/CD) is a software development practice that combines Continuous Integration (CI) and Continuous Delivery (CD) to automate the integration, testing, and deployment of code changes. 

Alright, let's break this down. 
#### Continuous Delivery 

>Continuous Integration (CI) is a practice of frequently committing code changes to a shared repository and then testing and verifying that these changes can be safely merged into a project.

- In essence, developers follow the CI approach by regularly implementing small changes in the code, which are automatically tested and verified before being merged into the project.

This means that a developer, instead of uploading large bulks of code once in a while, frequently pushes new functionality and changes into a shared repository, where they can be built and tested. This helps to identify conflicts and issues during the early development stages. Additionally, CI facilitates collaboration, since developers working on the project can inspect the changes made to the shared repository, which leads to a more transparent development process.

---

For example, a project repository might have several branches, one of them being the main line of the development, the `main` branch, and the other dedicated for designing new functionality and fixing issues, for example, `feature`. 

Changes made to the source code trigger automatic tests run against these changes. 

While one developer is working on the feature, the others might continue to commit changes to the `main` branch. CI conventionally encourages to regularly merge changes made to the `main` branch back into the `feature` branch through the process called pull requests. This helps to stay up-to-date with the main project and minimizes potential merge conflicts in the future. 

Changes made to the source code trigger automatic tests running on different levels, such as unit and functional tests. Tests can also be scheduled to run on a regular basis, such as once a day, rather than every commit.

Once the functionality is complete and tested on the `feature` branch (taking into account any modifications made to the main branch), it can be merged into the `main` branch.

Upon the merge, automatic tests are run again to ensure that the software is working properly with the new functionality integrated.

---

- CI ensures that code changes are regularly merged into the main branch. Therefore, CI is a solution to the problem of having too many branches of an app in development at once that might conflict with each other.

Key takeaways:

- It is recommended to merge changes from `main` into the `feature` branch regularly to keep it updated with the latest code changes made to `main`.
- Once the feature is complete and tested, the changes from the `feature` branch should be merged into the `main` branch.

#### CD: Continuous Deployment and Continuous Delivery

>Continuous Deployment (CD) is a practice to automatically deploying code changes to production after the changes have passed through an automated testing phase. 

This allows developers to produce software in short cycles, introducing updates frequently. 

>Continuous Delivery (CD) is a practice of frequently delivering code changes to a QA and Ops for testing. With this approach, software is tested manually in a staging area, and is accepted to production only after a manual review. 

The key difference between Continuous Deployment and Continuous Delivery lies in automation. 

Continuous Delivery automates the build and testing, as well as deployment, however, there is always someone who is responsible for approving the changes before deploying them into production. In contrast, in Continuous Deployment, changes are immediately deployed into production after passing through automated tests and verification, with minimal human interaction.  

- Continuous Delivery ensures that software is always ready for release by automating the build, testing, and deployment processes. However, human approval is still required before changes are deployed to production. 
- Continuous Deployment, in contrast, automatically releases changes to production once they pass automated tests and verification, with minimal human interaction.

|                         | Continuous Delivery                                                                             | Continuous Deployment                                                          |
| ----------------------- | ----------------------------------------------------------------------------------------------- | ------------------------------------------------------------------------------ |
| **Automation**          | Automates build, testing, and deployment processes                                              | Automates deployment to production                                             |
| **Human Intervention**  | Requires manual approval before production deployment                                           | Minimal human intervention                                                     |
| **Release Frequency**   | Regularly scheduled intervals                                                                   | Frequently, often multiple times a day                                         |
| **Scope of Deployment** | Can be a subset of features or components                                                       | Entire application or system                                                   |
| **Risk Management**     | Emphasizes rigorous testing and quality assurance                                               | Requires robust automated testing and quality assurance                        |
| **Customer Feedback**   | Feedback loops may be slower due to controlled releases                                         | Enables faster feedback loops from users                                       |
| **Rollback Capability** | May require manual intervention for rollbacks                                                   | Easy to roll back changes due to automated deployment                          |
| **Team Collaboration**  | Collaboration is important, but with more coordination and validation                           | Close collaboration between teams is crucial                                   |
| **Adoption Complexity** | Easier to adopt, with gradual automation                                                        | Requires a mature and well-automated development and deployment infrastructure |
| **Use Cases**           | Suitable for organizations with regular release cycles and a focus on stability and reliability | Ideal for organizations with high demand for rapid changes and innovation      |

## CI/CD pipelines

>A CI/CD pipeline is a series of automated processes that streamline the creation, testing, and deployment of software. 

- A CI/CD pipeline is a series of automated steps that enable software development teams to deliver code faster, safer, and more reliably.

CI/CD pipelines are the backbone of automation in the CI/CD process. The main objective is to minimize human error and maintain a consistent workflow for software testing and release.

This automated pipeline may employ different tools, with each responsible for its part of the workflow, such as:
- Compiling and building code
- Running unit, integration, or other types of tests
- Analyzing code quality and security
- Deploying to staging or production-like environments
- For containerized environments, building container images and deploying across cloud or hybrid cloud platforms

Each step of a CI/CD pipeline represents a subset of tasks grouped into coherent  pipeline stages.

Although CI/CD processes vary heavily depending on the technologies used in the project, a typical CI/CD pipeline consists of the following four stages, executed in order:

 - Source code
	 - The development process begins with the code. A pipeline is usually triggered by changes made to a source code repository, e.g., a `git push` or `git merge`.
	 - Pipelines may also be triggered by scheduled events (cron jobs) or the results of other pipelines or processes.

 - Build
	 - The build stage is responsible for building software from the shared repository to a testing environment.
	 - This step is crucial for languages that require compilation, such as Go, Java, or C/C++. However, for interpreted languages like Python, Ruby, or JavaScript, this may involve just packaging the code rather than full compilation.
	 - In containerized environments, regardless of the programming language in use, this stage includes building necessary Docker images (or using other container runtimes) to prepare cloud-native software for deployment.


 - Test
	 - In the testing stage, the code undergoes various automated tests to validate its functionality and identify issues. This includes unit tests, integration tests, functional tests, and load tests. 
	 - Code analysis tools may also be utilized to ensure code quality and security standards are met.

 - Deploy
	 - In the deployment phase, the software is released to a staging or production environment, making it available for testers or users.
	 - This stage ensures that the application is correctly deployed and that all configuration settings are accurate for the target environment.

>**Building vs. Compiling**
>
>Compiling refers to the process of translating human-readable source code written in programming languages like C/C++ into low-level machine code (binary). This process is performed by a compiler.
>
>In contrast, building encompasses a broader range of activities involved in preparing software for deployment. Building can include pre-processing, compiling, linking, converting data files, running automated tests, and packaging the software.

## Jenkins

Various tools are used to automate the creation and execution of CI/CD pipelines. Jenkins is one of the most popular such tools.

With its robust architecture and principles of operation, Jenkins exemplifies the key objectives that CI/CD systems strive to achieve.

>[Jenkins](https://www.jenkins.io) is an open-source automation server written in Java. It is primarily used to automate the building, testing, and deployment of software with Continuous Integration (CI) and Continuous Delivery/Deployment (CD) pipelines.

Jenkins integrates development lifecycle processes of all kinds, including build, document, test, package, stage, deploy, static code analysis and much more.

Jenkins comes with several advantages that make it stand out among its competitors, such as Travis, Bamboo, and CircleCI. To name a few,

- Open-source and free
	- Jenkins is available without any cost, allowing anyone to use, modify, and distribute it. Jenkins GitHub repository is available [here](https://github.com/jenkinsci/jenkins).
- Customizable and flexible
- Highly extendable with plugins
	- Jenkins supports a vast array of plugins, allowing for integration with many external tools and services. 
- Has an active and supportive community
	- A large and vibrant community contributes to ongoing improvements and offers support.

Thanks to plugins, Jenkins can integrate seamlessly with numerous industry tools, including source code management systems (like Git and GitHub), containerization platforms (like Docker), cloud services (AWS, GCP, Azure), and configuration management tools (like Ansible, Chef, Puppet).

Jenkins has innumerable use-cases provided by an extensive set of community-driven plugins. Even beyond CI/CD, it can be used to automate almost any task. For example,

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
## Jenkins architecture and the principles of work

###### Master Node and Agents

Jenkins follows a client-server architecture consisting of a central server known as the Master Node and multiple worker nodes called Agents. 

Commands and scripts are sent from the Master Node to called Agents, for the latter to perform the hard work of the specified tasks, such as running builds and tests. All the configuration, scripts, commands, and CI/CD pipelines are stored on the Jenkins Master Node.


- Jenkins Master Node
	- The primary application that runs Jenkins and orchestrates CI/CD workflows.
	- Provides a web interface for users to interact with Jenkins.
	- The Jenkins master node is responsible for: 
		- Scheduling and monitoring jobs
		- Specifying build settings and plugins’ configurations
		- Monitoring agent nodes
		- Storing build history and logs
		- User management and security
		- Plugin installation, management, and execution.

- Jenkins Agents/Minions
	- The worker nodes that actually execute tasks assigned by the Master Node, such as running builds and tests.
	- Jenkins agents are responsible for:
		- Executing build scripts and commands
		- Reporting build results back to the Master

There are two ways for the Master Node and Agents to communicate:

- Via SSH on port `22`, where the Master initiates the connection.
- Via JNLP (Java Network Launch Protocol) on port `50000`, where Agents initiate the connection.
###### Jobs and Pipelines

In Jenkins, tasks executed on Agents are known as jobs. 

>A job is a specific task or a series of tasks that Jenkins can execute, such as compiling source code, running tests, building packages, or deploying applications. 

>A Pipeline is a set of automated processes that define how software is build, tested, and deployed. A pipeline in Jenkins consists of a series of jobs.

- In other words, a pipeline is a series of steps the Jenkins server will execute to complete the necessary tasks of the CI/CD process. 

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

#### Jenkins CI/CD Pipeline Workflow

An example of a Jenkins CI/CD pipeline workflow, correlated to a standard CI/CD pipeline, may look like this:

- Source code
	- Developers work on a source code repository. Each time a modification is made, a new commit is created.
	- The Jenkins CI server continuously monitors the repository for new commits. The latter serve as build triggers.
	- 
	-When a commit is created, Jenkins server pulls the changes from the source code repository. Changes to the source code repository, in this case, serve as build triggers.

- Build
	- Upon detecting a new commit, Jenkins pulls the changes from the repository and assigns an Agent to build the new code version. If successful, the build generates necessary executables/containers; in case of a failure, feedback is provided through logs.

- Test
	- The newly built version undergoes a series of automated tests. In the case of test failures, developers are immediately alerted.

- Deploy
	- If all tests are passed, the code is typically deployed to a staging or production environment, depending on the deployment practices a developer team uses. 

>Pipeline triggers are events or conditions that initiate the execution of a CI/CD pipeline. Triggers automate the deployment process by responding to specific actions or changes, such as changes in source code repository. Builds can also be triggered manually, using the GUI.

###### Jenkins plugins

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
>
>To sum up, compiling is part of the build process, with the former translating source code into machine code and the latter referring to the complete process of creating a deployable software product.

## to be continued...
