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

## CI/CD tools

There are many CI/CD tools in the industry. Each aims to streamline software development by automating testing and deployment processes, and each has its own unique features that cater to different project requirements, team sizes, and preferred workflows. 

Here are some of the popular CI/CD tools:

- Jenkins
- GitHub Actions
- TeamCity
- Bamboo
- CircleCI
- ArgoCD

The choice depends on factors like existing infrastructure, team expertise, and specific project needs. 

Jenkins is no doubt one of the most common options thanks to its flexibility, ability to integrate with practically any languages and tools, and an open-source nature. 
