---
created: 2026-09-02
updated: 2026-09-02
---
>[!quote]+
> думаешь что секьюр бай дефолт  
> А оно секьюр бай бай

1. Security shift left
2. SAST
	1. The why
	2. What detects
	3. Examples
3. SCA + example
	1. The why
	2. What detects
	3. Examples



## Security shift left

Apparently, this is quite a basic thing. But we often forget about it.

Motivation: Here, in DevOps department, we all know what is automated testing. Why we need it in CI/CD, how catching bugs is important early, that code styling checks are very important because without them, in two years, no one will understand what you've written, and so on.
We all know that.
But what about security checks? 
The impression I've got, is that it silently slips unnoticed. 
And endless bugs appearing in production that can be caught automatically are evidence: this just screams that the pipeline didn't bother to check for an obvious SQL injection.
In a perfect world where security checks and gates were implemented correctly across all infrastructure, bug hunters and penetration testers would have had difficult times. They would only encounter non-obvious bugs like logic flaws, or HTTP request smuggling, or something very entangled and difficult to catch.
Becoming a "hacker" would have been even more difficult than it is now.

But, fortunately for security testers and unfortunately for all others, our world is different. 
Bugs are everywhere. 


---

- In this part, we will talk about security checks that **do not require a running application instance**. By this we usually mean SAST, SCA, secrets scanning, and IaC checks. 

- SAST and other automated security checks do not necessarily run solely in CI/CD pipelines, but this is the first place you'd likely to implement them. 
- You can run automated checks in:
	- In the developer’s IDE, while code is being written.
	- In pre-commit / pre-push hooks.
	- In pull-request or merge-request pipelines.
	- After code is merged into the default branch.
	- During scheduled full-project scans.
	- Before a release or deployment.


## SAST

- Static analysis vs. SAST 
- SAST is specifically focused on **security checks**.
