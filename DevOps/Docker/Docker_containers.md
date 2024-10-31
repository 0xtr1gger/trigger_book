Containerization has emerged as a revolutionary technology, enabling developers to build, ship, and run applications in a consistent and efficient manner. At the heart of this shift is Docker, a powerful platform that leverages the concept of containers to isolate applications and their dependencies from the underlying operating system. 

This article aims to explore the essential aspects of Docker containers, including their operation, principles of work, and the commands used to run and manage them effectively.

## Docker containers

>A Docker container is a lightweight, portable, and stand-alone runtime environment that isolates an application along with its dependencies, libraries, and configurations from the rest of the system. This isolation enables containers to run uniformly and consistently across various environments.

- Containers share the kernel with the host operating system and use the same system resources. However, applications inside the containers are isolated from any other processes running on the host.

Docker containers are instantiated from container images which specify the code that will be executed inside the container, along with its libraries and dependencies.

>A container image is a read-only static file used to create a container. It includes executable code and all the dependencies necessary to run an application in a containerized environment, such as Docker.

Images can be layered and typically consist of a base image (like Ubuntu, Alpine, etc.) and additional layers representing user-specific applications and dependencies. 
## Architecture

Docker utilizes a client-server architecture, centered around the Docker Engine.

>The Docker Engine is an open-source client-server application written in Go, responsible for running and managing Docker containers.

The Docker Engine has three main components:

- Docker daemon (`dockerd`)
	- The server-side component that manages Docker containers, images, networks, and volumes. It runs in a background as a system process and listens for API requests from clients. 

- Docker CLI (`docker`)
	- The command-line interface used to interact with the Docker Daemon. The Docker CLI represents a Docker client, which allows users to issue commands for managing Docker containers.

- API (Application Programming Interface)
	- The RESTful API provides an interface to programmatically interact with the Docker daemon, thereby opening up the possibility of automation.

An end user interacts with a Docker client, a CLI or, sometimes, a GUI (Graphical User Interface) application, by sending commands to it.
The Docker client communicates with the Docker daemon through the Docker API, either over UNIX sockets or via a network interface. 
The daemon then performs requested actions, such as creating, starting, stopping, or removing containers, as well as retrieving information about them, by communicating with the underlying host OS.

- Docker client and daemon can run either on a single machine and communicate over UNIX sockets, or on different machines and communicate over a network.
- A single Docker client can communicate with more than one daemon.

The `docker` CLI is the most commonly used Docker client utility. 
However, a GUI known as the [Docker Desktop](https://www.docker.com/products/docker-desktop/) is also available.
## Running containers

The `docker run` command is used to create and start Docker containers:

```bash
docker run [OPTIONS] IMAGE [ARG...] 
```

>Images are stored in the image registries, with Docker Hub serving as the default. When an image is specified for the `docker run` command, Docker first looks for this image locally. If not found, it automatically searches for the image on Docker Hub and downloads it.

For instance, the following command launches an `ubuntu` container:

```bash
docker run ubuntu
```

If the image is not found locally, Docker will pull it from Docker Hub and display output indicating the download status:

```
Unable to find image 'ubuntu:latest' locally
latest: Pulling from library/ubuntu
ff65ddf9395b: Pull complete 
Digest: sha256:99c35190e22d294cdace2783ac55effc69d32896daaa265f0bbedbcde4fbe3e5
Status: Downloaded newer image for ubuntu:latest
```

Currently running can be listed with the `docker ps` or `docker container ps` commands:

```bash
docker ps
```

```
CONTAINER ID   IMAGE     COMMAND   CREATED   STATUS    PORTS     NAMES
```

In this case, however, nothing is displayed. The reason is that the `ubuntu` container hasn't been instructed to execute anything - there there were no processes to run, causing it to exit.

>After a container finishes its specified tasks, it exists. 

To list all containers on the system, including terminated ones, the `-a` (`--all`) option is used:

```bash
docker ps -a
```
```
CONTAINER ID   IMAGE     COMMAND       CREATED         STATUS            l          PORTS     NAMES
c722db54bda3   ubuntu    "/bin/bash"   2 minutes ago   Exited (0) 2 minutes ago             elegant_shaw
```

- Containers can be referred either by their container ID or name, which is listed in the output of `docker ps`. 
#### Keeping containers running

One of the ways to hold the container running is to attach a terminal to it with the `-t` (`--tty`) option:

```bash
docker run -t ubuntu
```
```
root@0199d230673e:/# 
```

Now the container executes a shell process that keeps Ubuntu running. However, the container is still inaccessible: it responds with silence to any command. 
This is because, although a terminal has been attached to the container, it hasn't been instructed to accept any input from `STDIN`; this must also be specified explicitly with the `-i` (`--interactive`) option, which will keep `STDIN` open:

```bash
docker run -it ubuntu
```

It is now possible to interact with the container by running commands through the given terminal:

```
root@3f2190b99410:/# ls
bin  boot  dev  etc  home  lib  lib64  media  mnt  opt  proc  root  run  sbin  srv  sys  tmp  usr  var

```

One way to stop a container is to issue a `SIGINT` signal terminal from the controlling terminal by pressing `Ctrl + C`.

---

The `docker run` command has a multitude of options, some of which will be discussed in this article. 
#### Detached containers

- The `-d`, `--detach` option detaches the container from the working terminal and runs it in the background. This allows the container to continue executing without occupying the terminal:

```bash
docker run -it -d ubuntu
```

- A detached container has no active terminal to receive commands or send output to (the TTY  has indeed been attached with `-it`, but it runs the background). Instead, its output (`STDIN` and `STDERR` streams) is redirected to a container log file managed by a logging driver. 
- Container logs can be accessed with the `docker logs <container_name>` command.

- Commands to the container can still be issued with the `docker exec` command, which is used to execute commands in running containers (including detached ones):

```bash
docker exec -it reverent_pascal ls
```

Options for `docker exec`:

| Option                | Description                            |
| --------------------- | -------------------------------------- |
| `-d`, `--detach`      | Run command in the background          |
| `-i`, `--interactive` | Keep `STDIN` open even if not attached |
| `-t`, `--tty`         | Attach a pseudo-TTY                    |

- It also possible to execute an interactive shell command, `sh`, to effectively hand over the control over a detached container to the current terminal. The `-it` options ensure that the container will accept `STDIN` from the terminal, which allows to effectively attach a terminal to a detached container:

```bash
docker exec -it reverent_pascal sh
```

However, in this case, exiting from the terminal won't stop the container, since there the original terminal process, started with the `docker run -it ...`, is still running in the background.

- Another way to attach a terminal to a detached container is to use a `docker attach` command:

```bash
docker attach reverent_pascal
```

This attaches the container;s `STDOUT`/`STDERR`, along with `STDIN`, to the current terminal.

>In contrast to the `docker exec` command, `docker attach` doesn't add any new processes to the container, but instead attaches a terminal to existing processes, allowing control over them. Therefore, exiting the terminal that controls the processes inside the container is equivalent to exiting the container. 
>Simpy speaking, the container will exit in response to `SIGINT` form the terminal attached with `docker attach`.

---
Below is a simple demonstration of how `docker attach` works. 

The `docker run` command in the first terminal creates a `datetime` container that executes a simple script that displays current date and time every second. After attaching the second terminal to the `timedate` container using the `docker attach` command, logs begin to appear in both terminals simultaneously.

```bash
docker run -it --name datetime ubuntu sh -c 'while true; do date; sleep 1; done'
```

```bash
docker attach datetime
```

![datetime_attach_1](https://github.com/user-attachments/assets/9044bb6b-2be9-4c6f-80f2-cdfd555eabf9)


When a `SIGINT` signal is sent to the container from either terminal (via `Ctrl + C`) the container exits, stopping logs in both terminals.

![datetime_attach_2](https://github.com/user-attachments/assets/e724082e-0673-49ef-8069-befb23d3233e)


---

Here is a small cheatsheet summarizing how containers respond to a `SIGINT` signal sent by a terminal in response to `Ctrl + C`, depending on how the terminal has been attached to that container:

| `docker run -it ...`                                                                                              | `docker exec -it ... sh`                                                                                                                                                                                                                        | `docker attach ...`                                                                                    |
| ----------------------------------------------------------------------------------------------------------------- | ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | ------------------------------------------------------------------------------------------------------ |
| Exits                                                                                                             | Does not exit                                                                                                                                                                                                                                   | Exits                                                                                                  |
| The container exits in response to `Ctrl + C`, because the attached terminal is the only terminal controlling it. | The shell process terminates, but the container continues running since another process is holding the container active. `docker exec` only executes commands and redirects output streams, but does not take over the control of the terminal. | The container exits because `docker attach` connects the current terminal to its controlling terminal. |
#### Naming containers

By default, Docker generates random (and often amusing) names for containers. It is possible to override this behavior by specifying a custom name using the `--name` option of the `docker run` command:

```bash
docker run -it -d --name ubuntu_container ubuntu
```

>Container names must be unique across the system.

```bash
docker ps
```
```
```bash
CONTAINER ID   IMAGE     COMMAND       CREATED         STATUS         PORTS     NAMES
0317f6f2b973   ubuntu    "/bin/bash"   5 seconds ago   Up 5 seconds             ubuntu_container
```

>For the name of a container to be reused, the old container must be stopped and removed first. 

It's possible to rename already running containers as well. For this, Docker has the `docker rename` command.
For example, to rename the container `reverent_pascal` to `new_pascal`:

```bash
docker rename reverent_pascal new_pascal
```

But honestly, I want my `reverent_pascal` back.

```bash
docker rename new_pascal reverent_pascal.
```

#### Stopping and removing containers

A running container can be stopped with the `docker stop` command followed by the container ID or name:

```bash
docker stop reverent_pascal
# or, rquivalently,
docker stop 9c11aab44fbe
```

Docker commands can not only accept the full container ID, but also just one or a few first characters of a container ID:

```bash
docker stop 9c
```

- If there are multiple containers with IDs starting with the same characters, Docker will print a warning, and neither containers will be deleted:

```bash
docker stop d
```
```
Error response from daemon: multiple IDs found with provided prefix: d
```

- More characters of the container ID will solve this. 

```bash
docker stop da
```
```
da
```

>Another command used to stop a container is `docker kill`. 
>The difference between `docker stop` and `docker kill` is that the former, `docker stop`, gracefully shuts containers down by sending a `SIDTERM` signal, while latter, `docker kill`. terminates a container immediately with the `SIGKILL` signal. 
>`docker kill` should be used with caution, as it can potentially lead to data corruption or unexpected behavior, which may lead to problems with the next run of the container. Nevertheless, if the container will never be used again, killing it is most likely a safe option.
>`docker kill` may come useful when a container is stuck or unresponsive, but `docker stop` is generally a preferred method.

>A stopped container loses all its data unless a volume is attached.

---

Stopped containers are still visible with `ps -a`. To permanently remove containers from the system, the `docker rm` command is used:

```bash
docker rm reverent_pascal
```

---

- Trying to remove a running container will result in the following error:

```
Error response from daemon: cannot remove container "/reverent_pascal": container is running: stop the container before removing or force remove
```

- A running container can not be removed directly. It must be stopped first. 

```bash
docker stop reverent_pascal
docker rm reverent_pascal
```

However, there is a way to combine these commands into one with the `-f` (`--force`) option with `docker rm`:

```bash
docker rm --force reverent_pascal 
```

---

To remove all of the stopped containers from the system at once, the `docker container prune` command can be used:

```bash
docker container prune
```

#### Removing containers automatically

The `--rm` option for the `docker run` command sets Docker to automatically remove the container once it terminates:

```bash
docker run -it --rm ubuntu
```

![[--rm_demonstration_docker_run.png]]
`--rm` ensures that there are no garbage containers left behind. It also means that `docker start` can not be used to start the removed container.
#### Starting stopped containers

It is possible to start one or more stopped (but not yet removed) containers with the `docker start` command, providing one or more container names or IDs as arguments:

```bash
docker start -a -i reverent_pascal
```

- The `-a` (`--attach`) option attaches `STDOUT`/`STDERR` of the container to the current terminal, while `-i` (`--interactive`) option keeps the container's `STDIN` open.

>Again, stopped containers lose their data unless a persistent volume is attached. Thus, a container started anew without a volume behaves as it is its first run.
#### Container restarts 

By default, if a container stops, it does not restart automatically. However, the restart policy can be changed using the `--restart` option with `docker run`. 

```bash
docker run -it --restart always ubuntu_container
```

The accepted values are:

- `no` (default)
	- If a container stops, it will not be started automatically.

- `always`
	- The container will always be restarted regardless of how it was stopped (unless explicitly removed). 

- `unless-stopped`
	- Similar to `always`, but if the container is manually stopped with `docker stop`, it will not be restarted unless the Docker daemon is restarted.

- `on-failure[:max-retries]`
	- The container restarts only if it exits with a non-zero exit status. The maximum number of restart attempts can also be specified, e.g., `on-failure:5` will tell Docker to try to restart the container up to five times before giving up.

```bash
docker run -it --restart on-failure:5 ubuntu_container
```

It is also possible to change the restart policy of a running container with the `docker update` command, which is used to update containers' runtime configuration. For example,

```bash
docker update --restart="always" ubuntu_container
```

>If the host system shuts down, all running containers will stop, and their state will not be preserved. Containers will not restart upon the next system boot unless they have an appropriate restart policy defined. (i.e., `unless-stopped` or `always`).

>A stopped container looses its data unless a persistent volume is attached.
#### Pausing & unpausing containers

The `docker pause` command suspends all processes within a container without stopping it entirely.

```bash 
docker pause ubuntu_container
```

The command sends a `SIGSTOP` signal to all processes within the container, effectively suspending them. The container enters the `Paused` state and stops executing any code or handling requests. The CPU usage drops to zero, although the container will still consume memory.

```bash
docker ps
```
```
CONTAINER ID   IMAGE     COMMAND       CREATED        STATUS                 PORTS     NAMES
0317f6f2b973   ubuntu    "/bin/bash"   1 hour ago   Up 1 hour (Paused)             ubuntu_container
```

To resume the container from the same point at which it has been paused, the `docker unpause` command is used:

```bash
docker unpause ubuntu_container
```

>It is impossible to remove a container with the `Paused` state. The container must be stopped first.

## `docker run` option reference

- General options

| Option                | Description                                                                                              |
| --------------------- | -------------------------------------------------------------------------------------------------------- |
| `--help`              | Print usage statement                                                                                    |
| `--init`              | Run an init inside the container that forwards signals and reaps processes                               |
| `-d`, `--detach`      | Detached mode: run the container in the background and print the new container ID. The default is false. |
| `-i`, `--interactive` | Keep STDIN open even if not attached. The default is false.                                              |
| `-t`, `--tty`         | Allocate a pseudo-TTY. The default is false.                                                             |
| `--rm`                | Automatically remove the container when it exits. The default is false.                                  |
| `--sig-proxy`         | Proxy received signals to the process (non-TTY mode only). The default is true.                          |
| `--stop-signal`       | Signal to stop the container.                                                                            |
| `--stop-timeout`      | Timeout (in seconds) to stop a container, or `-1` to disable timeout.                                    |
| `--name`              | Assign a name to the container                                                                           |
| `--env`               | Set environment variables                                                                                |
| `--env-file`          | Read in a line delimited file of environment variables                                                   |

- Limiting container resources

| Option                 | Description                                                                                        |
| ---------------------- | -------------------------------------------------------------------------------------------------- |
| `-c`, `--cpu-shares`   | CPU shares (relative weight)                                                                       |
| `--cpus`               | Number of CPUs. The default is 0.0 which means no limit.                                           |
| `--cpu-count`          | Limit the number of CPUs available for execution by the container.                                 |
| `--cpu-percent`        | Limit the percentage of CPU available for execution by a container running on a Windows daemon.    |
| `--cpu-period`         | Limit the CPU CFS (Completely Fair Scheduler) period                                               |
| `--cpu-quota`          | Limit the CPU CFS (Completely Fair Scheduler) quota                                                |
| `--cpu-rt-period`      | Limit the CPU real-time period in microseconds                                                     |
| `--cpu-rt-runtime`     | Limit the CPU real-time runtime in microseconds                                                    |
| `--cpuset-cpus`        | CPUs in which to allow execution (0-3, 0,1)                                                        |
| `--cpuset-mems`        | Memory nodes (MEMs) in which to allow execution (0-3, 0,1). Only effective on NUMA systems.        |
| `--memory`             | Memory limit; S is an optional suffix which can be one of b, k, m, or g.                           |
| `--memory-reservation` | Memory soft limit; S is an optional suffix which can be one of b, k, m, or g.                      |
| `--memory-swap`        | Combined memory plus swap limit; S is an optional suffix which can be one of b, k, m, or g.        |
| `--kernel-memory`      | Kernel memory limit; S is an optional suffix which can be one of b, k, m, or g.                    |
| `--pids-limit`         | Tune the container's pids (process IDs) limit. Set to -1 to have unlimited pids for the container. |
| `--memory-swappiness`  | Tune a container's memory swappiness behavior. Accepts an integer between 0 and 100.               |

- Network options

| Option            | Description                                                                        |
| ----------------- | ---------------------------------------------------------------------------------- |
| `--network-alias` | Add network-scoped alias for the container                                         |
| `--dns`           | Set custom DNS servers                                                             |
| `--dns-option`    | Set custom DNS options                                                             |
| `--dns-search`    | Set custom DNS search domains                                                      |
| `--link`          | Add link to another container.                                                     |
| `--link-local-ip` | Add one or more link-local IPv4/IPv6 addresses to the container's interface        |
| `--ipc`           | Set the IPC mode for the container.                                                |
| `--pid`           | Set the PID mode for the container                                                 |
| `--userns`        | Set the user namespace mode for the container when userns-remap option is enabled. |
| `--net`           | Set the network mode for the container.                                            |
| `--mac-address`   | Container MAC address (e.g., `92:d0:c6:0a:29:33`)                                  |
| `--hostname`      | Container host name.                                                               |
| `--domainname`    | Container NIS domain name                                                          |

- Storage options

| Option            | Description                                   |
| ----------------- | --------------------------------------------- |
| `-v`, `--volume`  | Create a bind mount.                          |
| `--volume-driver` | Container's volume driver.                    |
| `--volumes-from`  | Mount volumes from the specified container(s) |
| `--tmpfs`         | Create a tmpfs mount                          |

- Security options

| Option           | Description                                                                                          |
| ---------------- | ---------------------------------------------------------------------------------------------------- |
| `--cap-add`      | Add Linux capabilities                                                                               |
| `--cap-drop`     | Drop Linux capabilities                                                                              |
| `--privileged`   | Give extended privileges to this container. A "privileged" container is given access to all devices. |
| `--security-opt` | Security Options for the container.                                                                  |
| `--isolation`    | Isolation specifies the type of isolation technology used by containers.                             |
| `--user`         | Sets the username or UID used and optionally the group name or GID for the specified command.        |

- Logging

| Option         | Description                                                                         |
| -------------- | ----------------------------------------------------------------------------------- |
| `--log-driver` | Logging driver for the container. Default is defined by daemon` --log-driver `flag. |
| `--log-opt`    | Logging driver-specific options.                                                    |
- Other

| Option          | Description                                                                                                             |
| --------------- | ----------------------------------------------------------------------------------------------------------------------- |
| `--entrypoint`  | Overwrite the default `ENTRYPOINT` of the image                                                                         |
| `--workdir`     | Working directory inside the container                                                                                  |
| `--label`       | Set metadata on the container (for example, `--label com.example.key=value`).                                           |
| `--label-file`  | Read in a line delimited file of labels                                                                                 |
| `--init`        | Run an `init` inside the container that forwards signals and reaps processes                                            |
| `--restart`     | Restart policy to apply when a container exits.                                                                         |
| `--read-only`   | Mount the container's root filesystem as read-only.                                                                     |
| `--shm-size`    | Size of `/dev/shm`. The format is `<number><unit>`.                                                                     |
| `--detach-keys` | Override the key sequence for detaching a container; key is a single character from the `[a-Z]` range, or `ctrl`-value. |
|                 |                                                                                                                         |



## Conclusion

In conclusion, Docker containers provide a powerful, lightweight, and portable solution for deploying applications in isolated environments. Docker offers a multitude of useful commands to effectively manage containers and their lifecycle, including `docker run`, `docker exec`, `docker ps`, and others.
However, `docker run`, along with commands for stopping, starting, restarting, pausing, and unpausing containers, is only a tip of the iceberg. There is much more left to cover.
