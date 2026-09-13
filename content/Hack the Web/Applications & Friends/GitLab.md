---
created: 2026-09-13
updated: 2026-09-13
---
>[!abstract]+ **Scope**: GitLab; fingerprinting and version discovery; hunting for secrets in repositories; account registration and username/email enumeration; password spraying; authenticated remote code execution.

- [ ] Confirm GitLab from the `/users/sign_in` login page.
- [ ] Browse `/explore` for public projects; inspect available repositories for secrets, keys, and other sensitive information.
- [ ] Attempt to register an account if self-registration is open; recheck `/explore` for internal projects if succeeded.
- [ ] Read the version from `/help` (requires login); if unavailable, attempt to infer the version through other means.
- [ ] Enumerate users through the registration page, if possible.
- [ ] Search for known exploits for the target instance version, if known.

## GitLab

- Self-hosted version control systems like GitLab, GitHub Enterprise, and Bitbucket instances often host proprietary source code and internal documentation.
- It's not uncommon to find hard-coded credentials and API keys embedded in scripts or configuration files and committed to repositories by mistake.
>**[GitLab](https://about.gitlab.com/)** is a web-based Git repository hosting platform that supports wiki, issue tracking, and CI/CD pipeline features, comparable to GitHub and Bitbucket.

>[!tip] GitLab Community Edition (CE) and Enterprise Edition (EE) are built mainly on Ruby on Rails and Go, with a Vue.js frontend and PostgreSQL database backend.

### Projects and visibility levels

- In GitLab, a **project** is the primary unit of organization; each project contains a **Git repository**, issue tracker, wiki, and CI/CD pipelines.

- A **group** organizes multiple related projects and subgroups under a single namespace, primarily used for centralized access control management.

- Projects and groups come in three visibility levels:
	- **Public** — Accessible to any user, including unauthenticated visitors; appears in the public directory under `/explore`; grants `Guest` permissions to signed-in users.
	- **Internal** — Accessible to authenticated users on self-managed instances; appears in `/explore` only for logged-in users.
	- **Private** — Accessible only to explicitly assigned project members; hidden from the directory for other users; users with the `Guest` role can't view or clone repository code.

>[!note] On GitLab.com (SaaS), internal visibility for new projects has been disabled since July 2019, but it remains available on self-managed instances.

>[!note] Public groups can contain public, internal, or private subgroups.

>[!note] See [`Project and group visibility — GitLab Docs`](https://docs.gitlab.com/user/public_access/).

### Authentication and registration

- Most enterprise instances restrict self-registration to corporate email domains or require an administrator to approve new accounts.
- A misconfigured instance with open self-registration allows anyone to create an account and immediately access all internal projects.

>[!note] Two-factor authentication is disabled by default on self-managed instances.

## Discovery & fingerprinting

- Browsing to the GitLab base URL redirects unauthenticated requests to `/users/sign_in`, which displays the GitLab logo and a login prompt.

![[gitlab_sign_in.png]]

- The only reliable way to read the instance version number is navigating the `/help` page as an authenticated user (when unauthenticated, you won't see the version on that page). 
- If you can register an account, log in and check `/help`. If you can't, and there's no other version tell (suchas a date on the page, the first public commit), stick to hunting for secrets rather than firing exploits blindly.

>[!tip]+
>You can attempt to infer the instance version by inspecting static asset paths (`/assets/webpack/...`), commit timestamps on public repositories, or years in copyright notices.

- Serious known vulnerabilities that affect specific GitLab versions include:

| Version                                                | Description                                          |
| ------------------------------------------------------ | ---------------------------------------------------- |
| [`12.9.0`](https://www.exploit-db.com/exploits/48431)  | Arbitrary File Read; `06.05.2020`.                   |
| [`11.4.7`](https://www.exploit-db.com/exploits/49257)  | Remote Code Execution (Authenticated); `14.12.2020`. |
| [`13.10.3`](https://www.exploit-db.com/exploits/49821) | User Enumeration; `03.05.2021`.                      |
| [`13.9.3`](https://www.exploit-db.com/exploits/49944)  | Remote Code Execution (Authenticated); `03.06.2021`. |
| [`13.10.2`](https://www.exploit-db.com/exploits/49951) | Remote Code Execution (Authenticated); `04.06.2021`. |
- GitLab has over [553 CVEs](https://www.cvedetails.com/vulnerability-list/vendor_id-13074/Gitlab.html), several of which lead to remote code execution.

## Enumerating projects and users

- Browse to `/explore` to list public projects. Even public projects (which may have been misconfigured as such) can reveal sensitive configuration files, hard-coded credentials, or details about the internal infrastructure.

![[gitlab_explore.png]]

- Check whether self-registration is enabled at `/users/sign_up`. If the instance doesn't require administrator approval, create an account to view internal repositories.

- Even if can't register an account, the registration form itself may allow you to enumerate valid users based on application responses:
	- A taken username returns `Username is already taken`.
	- A taken email returns `1 error prohibited this user from being saved: Email has already been taken`.

![[gitlab_sign_up.png]]

- After registering and logging in, revisit `/explore` to view all internal projects.
- Download the source of available projects and review them for vulnerabilities, hidden endpoints, or leaked credentials.

>[!note] See [`How I made $15k in bug bounties from GitHub secret leaks — Tales of a Postgraduate Nothing`](https://tillsongalloway.com/finding-sensitive-information-on-github/index.html).

## Enumerating usernames with a script

- GitLab doesn't treat username or project enumeration as a vulnerability in its [HackerOne program](https://hackerone.com/gitlab?type=team). But you can still enumerate usernames to build target lists for password spraying.
- For example, you can enumerate usernames in GitLab Community Edition `13.10.3` using a [known exploit](https://www.exploit-db.com/exploits/49821) (a Python 3 port is available at [`dpgg101/GitLabUserEnum`](https://github.com/dpgg101/GitLabUserEnum)):

```bash
./gitlab_userenum.sh --url http://<target_ip_address>:<port>/ --userlist users.txt
```

- You can use the discovered usernames to conduct a password spraying attack using common default passwords (such as `Welcome1` or `passwd123`) or credentials from public breaches ([`DeHashed`](https://dehashed.com/)).
- Default account lockout thresholds:
	- **Prior to version `16.6`**: GitLab defaults to 10 failed attempts and an automatic account unlock after 10 minutes.  
	- **Starting in version `16.6`**: GitLab exposes the `max_login_attempts` and `failed_login_attempts_unlock_period_in_minutes` settings in the admin UI; if left untouched, the same defaults apply.

## References and further reading

- [`Bitbucket vs GitHub vs GitLab — StackShare`](https://stackshare.io/stackups/bitbucket-vs-github-vs-gitlab)
- [`GitLabUserEnum — GitHub`](https://github.com/dpgg101/GitLabUserEnum)
- [`GitLab CE 13.10.2 authenticated RCE — HackerOne`](https://hackerone.com/reports/1154542)
- [`GitLab CE 13.10.2 RCE exploit — Exploit-DB`](https://www.exploit-db.com/exploits/49951)
- [`Finding sensitive information on GitHub — tillsongalloway.com`](https://tillsongalloway.com/finding-sensitive-information-on-github/index.html)
- [`GitLab vulnerability list — CVE Details`](https://www.cvedetails.com/vulnerability-list/vendor_id-13074/Gitlab.html)
- [`Organize work with projects — GitLab Docs`](https://docs.gitlab.com/user/project/organize_work_with_projects/)
- [`Project and group visibility — GitLab Docs`](https://docs.gitlab.com/user/public_access/)
