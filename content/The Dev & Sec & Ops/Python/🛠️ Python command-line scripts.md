---
created: 2026-10-02
updated: 2026-10-02
---
## `sys.argv`

- [`sys.argv`](https://docs.python.org/3/library/sys.html#sys.argv) — The list of command line arguments passed to a Python script.
	- `argv[0]` is the script name.

```python
import sys
print(sys.argv)
```

>[!example]-
> ```bash
> python3 script.py hello world
> ```
> 
> ```bash
> ['script.py', 'hello', 'world']
> ```

- Accessing individual arguments directly:

```python
import sys

if len(sys.argv) < 2:
	print('Usage: script.py <name>')
	sys.exit(1)

name = sys.argv[1]

print(f'Hello, (name)!')
```

- `sys.argv` is fine for very small scripts, but it becomes inconvenient when you need optional arguments, flags, default values, etc.

## `argparse`

>[`argparse`](https://docs.python.org/3/library/argparse.html) is Python's standard-library module for building command-line interfaces (CLIs).

- Minimal example:

```python
import argparse

parser = argparse.ArgumentParser()

parser.add_argument('name')

args = parser.parse_args()

print(f'Hello, {args.name}!')
```

```bash
python3 script.py <name>
```

### `add_argument()`

>[`add_argument()`](https://docs.python.org/3/library/argparse.html#the-add-argument-method) defines how a single command-line argument should be parsed. 

- Add an optional argument:

```python
parser.add_argument('-p', '--port')
```

>[!example]+
> ```python
> parser.add_argument('-p', '--port')
> args = parser.parse_args()
> 
> # access argument value
> port = args.port
> ```

- Add positional arguments:

```python
parser.add_argument('source')
parser.add_argument('destination')
```

>[!example]+
> ```python
> parser.add_argument('source')
> parser.add_argument('destination')
> paraser.parse_args()
> 
> # access argument value
> source = args.source
> source = args.destination
> ```

>[!note] Optional arguments are identified by the `-` prefix; the remaining arguments are assumed to be positional.

#### Destination name

- Normally the option name determines the attribute.

>[!example]+
> ```python
> parser.add_argument('--target')
> ```
> 
> - This creates `args.target`.

- Specify the destination explicitly:

 ```python
 parser.add_argument('--target', dest='hostname')
 ```
#### Default values

- `default` — set a default value:

```python
parser.add_argument('-p', '--port', default=80)
```

#### Type conversion 

- `type` — convert the argument into a Python type:

```python
parser.add_argument('--port', type=int)
```

- Provide a custom conversion function:

```python
def parse_hex(value):
	# ...
	return parsed_value

parser.add_argument('--address', type=parse_hex)
```

#### Boolean arguments

- `store_true`
- `store_false`

#### Required optional arguments

### Choices

#### Multiple values


## Reading files

- Read file line-by-line:

```bash
with open('filename.txt', 'r', encoding='utf-8') as file:
    for line in file:
        print(line.strip())
```

- Grep:

```python
import re

def grep_pattern(pattern, file_path):
    with open(file_path, 'r') as file:
        for line_number, line in enumerate(file, start=1):
            if re.search(pattern, line):
                print(f"Line {line_number}: {line.strip()}")

# example usage
grep_pattern(r"error", "log.txt")   
```
