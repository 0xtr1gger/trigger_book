---
created: 2026-10-05
updated: 2026-10-05
---
> An **expression** is any construct that produces a value in a Terraform configuration: a literal, a reference, an operator, a conditional, a `for` expression, a function call, or a string template. Expressions appear on the right-hand side of every argument.

- Terraform has no user-defined functions, loops, or statements. All computation is performed with expressions and the built-in function library, which keeps configurations declarative and evaluable without side effects.
- Expressions are evaluated as part of the dependency graph. An expression that references a value unknown until apply is itself unknown during planning.

## Types and values

| Type | Literal syntax | Notes |
| ---- | -------------- | ----- |
| `string` | `"hello"`, heredoc | Unicode text. Only double quotes delimit strings. |
| `number` | `15`, `6.283`, `1e3` | Arbitrary-precision numbers; no separate integer type. |
| `bool` | `true`, `false` | |
| `list` / `tuple` | `["a", "b"]` | Square-bracket literals produce tuples, converted to lists where a list is expected. |
| `map` / `object` | `{ name = "web", port = 443 }` | Brace literals produce objects. Keys can be written with `=` or `:`. |
| `set` | none | Created only by conversion, for example `toset([...])`. Unordered, unique elements. |
| `null` | `null` | The absence of a value. Assigning `null` to an argument is equivalent to omitting it. |

- Type constraints and automatic conversion are covered in [[Terraform variables and outputs#Input variables]].
- Collection elements are accessed with `list[0]`, `map["key"]`, or `object.attribute`. Accessing a missing index or key is an error; `try()` and `lookup()` provide defaults.

## References to named values

| Reference | Value |
| --------- | ----- |
| `<TYPE>.<NAME>` | A managed resource (an object, or a list or map of objects with `count` or `for_each`). |
| `data.<TYPE>.<NAME>` | A data source. |
| `ephemeral.<TYPE>.<NAME>` | An ephemeral resource. |
| `var.<NAME>` | An input variable. |
| `local.<NAME>` | A local value. |
| `module.<NAME>.<OUTPUT>` | An output of a child module. |
| `count.index` | The index of the current instance in a block with `count`. |
| `each.key`, `each.value` | The key and value of the current instance in a block with `for_each`. |
| `self` | The current resource, inside provisioners, connection blocks, and postconditions. |
| `path.module` | The filesystem path of the module containing the expression. |
| `path.root` | The filesystem path of the root module. |
| `path.cwd` | The working directory from which Terraform was run. |
| `terraform.workspace` | The name of the current CLI workspace. |

- `path.module` should be used for files shipped with a module (`"${path.module}/templates/user-data.sh.tftpl"`), because the module can be called from anywhere. `path.cwd` makes behaviour depend on where the command is run and should be avoided.
- `terraform.workspace` and its uses are discussed in [[Terraform state#Workspaces]].

## Operators

| Category | Operators |
| -------- | --------- |
| Arithmetic | `+`, `-`, `*`, `/`, `%`, unary `-` |
| Equality | `==`, `!=` |
| Comparison | `<`, `<=`, `>`, `>=` |
| Logical | `&&`, `\|\|`, `!` |

- `==` compares both type and value: `5 == "5"` is `false`.
- Do not rely on short-circuit evaluation of logical operators. Older Terraform versions evaluate both operands, so `var.obj != null && var.obj.enabled` fails when `var.obj` is `null`. `try(var.obj.enabled, false)` behaves the same in every version.

## Conditional expressions

```hcl
instance_type = var.environment == "prod" ? "m7g.large" : "t4g.small"
```

- The syntax is `<CONDITION> ? <TRUE_VALUE> : <FALSE_VALUE>`.
- Both result expressions must have the same type, or types convertible to a common type. `var.enabled ? [] : null` is valid; `var.enabled ? "a" : 1` produces a string after conversion and is confusing.
- Combined with `count` or `for_each`, conditionals make resources optional:

```hcl
resource "aws_kms_key" "logs" {
  count               = var.create_kms_key ? 1 : 0
  enable_key_rotation = true
}

locals {
  logs_key_arn = var.create_kms_key ? aws_kms_key.logs[0].arn : var.existing_kms_key_arn
}
```

## For expressions

A `for` expression transforms one collection into another.

```hcl
locals {
  # List → list
  upper_names = [for name in var.names : upper(name)]

  # List → list, filtered
  prod_services = [for svc in var.services : svc.name if svc.environment == "prod"]

  # Map → map
  instance_ips = { for key, inst in aws_instance.web : key => inst.private_ip }

  # List → map with index
  zone_cidrs = { for i, zone in var.zones : zone => cidrsubnet(var.vpc_cidr, 4, i) }

  # Grouping: values with the same key are collected into a list
  services_by_team = { for svc in var.services : svc.team => svc.name... }
}
```

- Square brackets produce a tuple; braces produce an object, with `<KEY> => <VALUE>`.
- With one iteration variable, a list yields elements and a map yields values. With two variables, a list yields index and element, and a map yields key and value.
- The optional `if` clause filters elements.
- In an object `for` expression, duplicate keys are an error unless the value is followed by the grouping operator `...`.
- Iterating over a set or map produces results in a well-defined order: maps and objects by key in lexical order, sets of strings in lexical order.

### Flattening nested structures

A frequent pattern is to flatten a nested structure into a map that `for_each` can consume:

```hcl
variable "networks" {
  type = map(object({
    cidr    = string
    subnets = map(string) # subnet name => CIDR
  }))
}

locals {
  subnets = merge([
    for net_name, net in var.networks : {
      for subnet_name, cidr in net.subnets :
      "${net_name}/${subnet_name}" => {
        network = net_name
        cidr    = cidr
      }
    }
  ]...)
}

resource "aws_subnet" "this" {
  for_each   = local.subnets
  vpc_id     = aws_vpc.this[each.value.network].id
  cidr_block = each.value.cidr
}
```

- The outer `for` produces a list of maps; `merge(...)` with the expansion symbol `...` passes the list elements as separate arguments and combines them into one map. `flatten()` serves the same purpose for lists.

## Splat expressions

```hcl
output "worker_ids" {
  value = aws_instance.worker[*].id
}
```

- `list[*].attr` is shorthand for `[for item in list : item.attr]`.
- Splat applies to lists, sets, and tuples, so it works with resources that use `count`. Resources with `for_each` are maps; use `values(aws_instance.web)[*].id`.
- Applied to a single non-list value, `[*]` converts it to a one-element list, or an empty list if the value is `null`. This is useful for optional nested blocks: `for_each = var.logging_config[*]`.

## Dynamic blocks

`dynamic` blocks generate repeated nested blocks from a collection.

```hcl
variable "ingress_rules" {
  type = list(object({
    description = string
    port        = number
    cidrs       = list(string)
  }))
}

resource "aws_security_group" "web" {
  name   = "web"
  vpc_id = var.vpc_id

  dynamic "ingress" {
    for_each = var.ingress_rules
    iterator = rule
    content {
      description = rule.value.description
      from_port   = rule.value.port
      to_port     = rule.value.port
      protocol    = "tcp"
      cidr_blocks = rule.value.cidrs
    }
  }
}
```

- The label of the `dynamic` block is the name of the nested block to generate.
- `for_each` accepts any collection. The `iterator` argument names the iteration variable (by default, the block label); it exposes `.key` and `.value`.
- `content` defines the body of each generated block. `dynamic` blocks can be nested.
- A conditional nested block is generated with a zero-or-one element collection:

```hcl
dynamic "logging" {
  for_each = var.access_log_bucket == null ? [] : [var.access_log_bucket]
  content {
    target_bucket = logging.value
    target_prefix = "access/"
  }
}
```

- Dynamic blocks can generate only nested blocks of the resource schema. They cannot generate arguments, meta-argument blocks (`lifecycle`, `provisioner`), or top-level blocks.
- Overuse makes configurations hard to read. When a module's interface is a long list of arbitrary blocks, consider whether separate resources (for example, standalone security group rule resources) would be clearer.

## String templates

### Interpolation

```hcl
name = "${var.project}-${var.environment}-web"
```

- `${ ... }` evaluates an expression and inserts its string representation.
- A string consisting only of one interpolation (`"${var.name}"`) is equivalent to the bare expression (`var.name`); `terraform fmt` does not change it, but the bare form is idiomatic.

### Directives

`%{ ... }` sequences add conditionals and iteration to templates:

```hcl
locals {
  greeting = "Hello, %{ if var.name != "" }${var.name}%{ else }unnamed user%{ endif }!"
}
```

```hcl
locals {
  hosts_file = <<-EOT
    %{ for name, ip in var.hosts ~}
    ${ip} ${name}
    %{ endfor ~}
  EOT
}
```

- The strip marker `~` removes the whitespace (including the newline) adjacent to a directive, which keeps the rendered output free of blank lines.

### Heredoc strings

```hcl
user_data = <<-EOT
  #!/bin/bash
  set -euo pipefail
  echo "ENVIRONMENT=${var.environment}" > /etc/app.env
EOT
```

- `<<EOT` preserves the text exactly; `<<-EOT` strips the common leading indentation, which allows the heredoc to be indented with the surrounding code. The delimiter word is arbitrary.

### Escaping

- `$${` produces a literal `${`, and `%%{` a literal `%{`. This is needed when generating shell scripts or other templates that use the same syntax.
- Backslash escapes are supported in quoted strings: `\n`, `\t`, `\"`, `\\`, `\uNNNN`. Heredocs do not interpret backslash escapes.
- HCL has no single-quoted strings. `'text'` is a syntax error rather than a non-interpolating string.

### Template files

- `templatefile(path, vars)` renders a separate file with the same template syntax. Only the variables passed in the map are available; the template cannot access the rest of the configuration.

```hcl
resource "aws_instance" "app" {
  # ...
  user_data = templatefile("${path.module}/templates/user-data.sh.tftpl", {
    environment = var.environment
    packages    = var.packages
  })
}
```

```bash
#!/bin/bash
# templates/user-data.sh.tftpl
echo "ENVIRONMENT=${environment}" > /etc/app.env
%{ for pkg in packages ~}
apt-get install -y ${pkg}
%{ endfor ~}
```

- The `.tftpl` extension is the recommended convention for template files.

## Built-in functions

- Functions are called with `<NAME>(<ARGUMENT>, ...)`. Terraform has no user-defined functions; the full catalogue is in the [function reference](https://developer.hashicorp.com/terraform/language/functions).
- The examples below use the `terraform console` notation, where `>` is the prompt (see [[#Terraform console]]).

### Numeric functions

```text
> max(10, 9, 8)
10
> min(10, 9, 8)
8
> abs(-12.5)
12.5
> ceil(4.1)
5
> floor(4.9)
4
> log(8, 2)
3
> pow(2, 10)
1024
> parseint("ff", 16)
255
```

### String functions

```text
> lower("HELLO WORLD")
"hello world"
> upper("hello world")
"HELLO WORLD"
> title("hello world")
"Hello World"
> format("%s-%03d", "web", 7)
"web-007"
> join(",", ["a", "b", "c"])
"a,b,c"
> split(",", "a,b,c")
tolist(["a", "b", "c"])
> replace("eu-central-1", "-", "_")
"eu_central_1"
> substr("terraform", 0, 5)
"terra"
> trimspace("  padded  ")
"padded"
> startswith("arn:aws:iam::123456789012:role/admin", "arn:aws:iam::")
true
> regex("^(\\d+)\\.(\\d+)", "1.13.0")
["1", "13"]
```

- `regex` fails when there is no match; `regexall` returns an empty list instead, and `can(regex(...))` tests a pattern.

### Collection functions

```text
> length(["a", "b", "c"])
3
> concat(["a"], ["b", "c"])
["a", "b", "c"]
> distinct(["a", "b", "a", "c", "b"])
tolist(["a", "b", "c"])
> flatten([["a"], ["b", ["c"]]])
["a", "b", "c"]
> contains([1, 2, 3, 4, 5], 2)
true
> merge({ a = 1, b = 2 }, { b = 3, c = 4 })
{ a = 1, b = 3, c = 4 }
> lookup({ a = 1 }, "b", 0)
0
> keys({ b = 2, a = 1 })
["a", "b"]
> zipmap(["web", "db"], [80, 5432])
{ db = 5432, web = 80 }
> element(["a", "b", "c"], 4)
"b"
> slice(["a", "b", "c", "d"], 1, 3)
["b", "c"]
> coalesce("", "fallback")
"fallback"
> one([])
null
> range(3)
tolist([0, 1, 2])
> setproduct(["dev", "prod"], ["eu", "us"])
tolist([["dev", "eu"], ["dev", "us"], ["prod", "eu"], ["prod", "us"]])
> alltrue([true, false])
false
```

- `merge` resolves conflicting keys in favour of the last argument.
- `element` wraps around: index 4 in a three-element list selects index `4 % 3 = 1`.
- `one` returns the only element of a zero- or one-element collection, or `null`, which makes it the idiomatic accessor for conditional `count` resources: `one(aws_kms_key.logs[*].arn)`.

### Encoding functions

```text
> base64encode("string")
"c3RyaW5n"
> base64decode("c3RyaW5n")
"string"
> jsonencode({ name = "web", ports = [80, 443] })
"{\"name\":\"web\",\"ports\":[80,443]}"
> jsondecode("{\"enabled\": true}")
{ enabled = true }
> yamlencode({ replicas = 3 })
"\"replicas\": 3\n"
> urlencode("Hello World!")
"Hello+World%21"
> csvdecode("name,port\nweb,80\n")
tolist([{ name = "web", port = "80" }])
```

- `jsonencode` is the reliable way to produce JSON documents such as IAM policies or container definitions, because it handles quoting and escaping.
- `base64gzip` compresses and encodes (for large `user_data`); `textencodebase64` encodes in a specific character set, such as UTF-16LE for PowerShell `-EncodedCommand`.

### Filesystem functions

```text
> dirname("foo/bar/baz.txt")
"foo/bar"
> basename("foo/bar/baz.txt")
"baz.txt"
> abspath(path.root)
"/home/dev/infra/live/prod"
> pathexpand("~/.ssh/id_ed25519.pub")
"/home/dev/.ssh/id_ed25519.pub"
> fileexists("${path.module}/files/motd")
true
> fileset(path.module, "files/*.conf")
toset(["files/app.conf", "files/nginx.conf"])
```

- `file(path)` returns a file's contents as a string; `filebase64(path)` returns it base64-encoded (for binary files); `templatefile(path, vars)` renders a template.
- Filesystem functions read files at plan time, on the machine running Terraform. They cannot read files created by resources during the same apply.

### Date and time functions

```text
> formatdate("DD MMM YYYY hh:mm ZZZ", "2021-10-05T21:20:34Z")
"05 Oct 2021 21:20 UTC"
> timeadd("2026-01-01T00:00:00Z", "720h")
"2026-01-31T00:00:00Z"
> timecmp("2026-01-01T00:00:00Z", "2025-12-31T23:59:59Z")
1
```

- `timestamp()` returns the current time in RFC 3339 format. It returns a different value on every run, so using it in a resource argument causes a change in every plan. `plantimestamp()` (Terraform 1.5 and later) returns the time the plan was created and remains constant between plan and apply.
- For stable time-based values, use the `time_static` or `time_rotating` resources of the `hashicorp/time` provider.

### Hash and cryptographic functions

```text
> md5("hello world")
"5eb63bbbe01eeed093cb22bb8f5acdc3"
> sha256("hello world")
"b94d27b9934d3e08a52e52d7da7dabfac484efe37a5380ee9088f7ace2efcde9"
```

- `uuidv5(namespace, name)` derives a deterministic UUID from a namespace and a name, so it is stable across runs.

- `filemd5`, `filesha1`, `filesha256`, and `filesha512` hash file contents. They are commonly used to trigger replacement or upload when a file changes (`content_md5`, `source_hash`).
- `bcrypt()` and `uuid()` return a different value on every run because they include random data; using them in resource arguments produces a permanent diff.
- `rsadecrypt(ciphertext, private_key)` decrypts RSA-encrypted data, for example the Windows administrator password data returned by EC2.
- These functions are not a substitute for secret management: their inputs and outputs end up in state like any other value.

### IP network functions

```text
> cidrnetmask("10.0.0.0/24")
"255.255.255.0"
> cidrhost("10.0.1.0/24", 5)
"10.0.1.5"
> cidrsubnet("10.0.0.0/16", 8, 2)
"10.0.2.0/24"
> cidrsubnets("10.0.0.0/16", 4, 4, 8)
tolist(["10.0.0.0/20", "10.0.16.0/20", "10.0.32.0/24"])
```

- `cidrsubnet(prefix, newbits, netnum)` extends the prefix length by `newbits` and returns subnet number `netnum`.
- `cidrsubnets` allocates consecutive non-overlapping subnets of different sizes, which avoids manual address planning errors.

### Type conversion functions

```text
> tostring(123)
"123"
> tonumber("42")
42
> tobool("true")
true
> toset(["b", "a", "b"])
toset(["a", "b"])
> tolist(toset(["b", "a"]))
tolist(["a", "b"])
> tomap({ a = "1", b = "2" })
tomap({ a = "1", b = "2" })
> try(tonumber("abc"), 0)
0
> can(regex("^ami-", "ami-0abc"))
true
```

- `try(expr, fallback, ...)` returns the first argument that evaluates without error. It handles missing attributes and failed conversions, not unknown values.
- `can(expr)` returns whether the expression evaluates without error, and is used mainly in validation conditions.
- `sensitive(value)` marks a value as sensitive; `nonsensitive(value)` removes the marking.
- `ephemeralasnull(value)` (Terraform 1.10 and later) replaces ephemeral values in a structure with `null`, so that the non-ephemeral parts can be used in persisted contexts.
- `type(value)` is available only in `terraform console` and prints the type of a value.

## Provider-defined functions

Since Terraform 1.8, providers can ship their own functions, called with the `provider::<PROVIDER>::<FUNCTION>` syntax.

```hcl
terraform {
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 6.0"
    }
  }
}

locals {
  role_arn   = "arn:aws:iam::123456789012:role/deploy"
  account_id = provider::aws::arn_parse(local.role_arn).account_id
}
```

- The provider must be declared in `required_providers` of the module that calls the function. Provider functions do not require a configured `provider` block.
- Available functions are listed in each provider's documentation in the Terraform Registry.

## Terraform console

`terraform console` opens an interactive evaluator with access to the configuration's variables, locals, and the current state. It is the fastest way to test expressions and functions.

- Start an interactive session in an initialised working directory:

```bash
terraform console
```

- Evaluate a single expression non-interactively:

```bash
echo 'cidrsubnets("10.0.0.0/16", 4, 4, 8)' | terraform console
```

- Pass variables to the evaluation context:

```bash
terraform console -var-file=environments/prod.tfvars
```

- Inside the console, resource attributes from state can be inspected (`aws_vpc.main.cidr_block`), which helps when writing outputs and `for` expressions against real data. Console sessions read state, so they need the same backend access as a plan.

## References

- [Expressions](https://developer.hashicorp.com/terraform/language/expressions)
- [Built-in functions](https://developer.hashicorp.com/terraform/language/functions)
- [Dynamic blocks](https://developer.hashicorp.com/terraform/language/expressions/dynamic-blocks)
- [Strings and templates](https://developer.hashicorp.com/terraform/language/expressions/strings)
