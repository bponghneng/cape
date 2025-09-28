---
scraped_url: "https://typer.tiangolo.com/tutorial/"
scraped_date: "2025-09-27"
---

# Typer Tutorial

Learn how to use **Typer** in this step-by-step **Tutorial** - **User Guide**.

It covers everything you need to know from the **simplest scripts** to **complex CLI applications**.

You could consider this a **book**, a **course**, the **official** and recommended way to learn **Typer**. 😎

## Python Types

If you need a refresher about how to use Python type hints, check the first part of [FastAPI's Python types intro](https://fastapi.tiangolo.com/python-types/).

You can also check the [mypy cheat sheet](https://mypy.readthedocs.io/en/latest/cheat_sheet_py3.html).

In short (very short), you can declare a function with parameters like:

```python
from typing import Optional

def type_example(name: str, formal: bool = False, intro: Optional[str] = None):
    pass
```

And your editor (and **Typer**) will know that:

- `name` is of type `str` and is a required parameter.
- `formal` is a `bool` and is by default `False`.
- `intro` is an optional `str`, by default is `None`.

These type hints are what give you autocomplete in your editor and several other features.

**Typer** is based on these type hints.

## About this Tutorial

This tutorial shows you how to use **Typer** with all its features, step by step.

Each section gradually builds on the previous ones, but it's structured to separate topics, so that you can go directly to any specific one to solve your specific CLI needs.

It is also built to work as a future reference so you can come back and see exactly what you need.

## Run the Code

All the code blocks can be copied and used directly (they are tested Python files).

To run any of the examples, copy the code to a file `main.py`, and run it:

```bash
$ python main.py
```

It is **HIGHLY encouraged** that you write or copy the code, edit it and run it locally.

Using it in your editor is what really shows you the benefits of **Typer**, seeing how little code you have to write, all the **inline errors**, **autocompletion**, etc.

And running the examples is what will really help you **understand** what is going on.

You can learn a lot more by **running some examples** and **playing around** with them than by reading all the docs here.

# First Steps

## The Simplest Example

The simplest **Typer** file could look like this:

```python
import typer

def main():
    print("Hello World")

if __name__ == "__main__":
    typer.run(main)
```

Copy that to a file `main.py`.

Test it:

```bash
$ python main.py
Hello World
```

...but this program is still not very useful. Let's extend it.

## What is a CLI Argument

Here we will use the word **CLI argument** to refer to **CLI parameters** passed in some specific order to the CLI application. By default, they are _required_.

If you go to your terminal and type:

```bash
$ ls ./myproject
```

`ls` will show the contents of the directory `./myproject`.

- `ls` is the _program_ (or "command", "CLI app").
- `./myproject` is a _CLI argument_, in this case it refers to the path of a directory.

They are a bit different from **CLI options** that you will see later below.

## Add a CLI Argument

Update the previous example with an argument `name`:

```python
import typer

def main(name: str):
    print(f"Hello {name}")

if __name__ == "__main__":
    typer.run(main)
```

```bash
$ python main.py Camila
Hello Camila
```

> **Tip**: If you need to pass a single value that contains spaces to a _CLI argument_, use quotes (`"`) around it.

## Two CLI Arguments

Now let's say we want to have the name and last name separated.

So, extend that to have 2 arguments, `name` and `lastname`:

```python
import typer

def main(name: str, lastname: str):
    print(f"Hello {name} {lastname}")

if __name__ == "__main__":
    typer.run(main)
```

```bash
$ python main.py Camila Gutiérrez
Hello Camila Gutiérrez
```

> **Tip**: Notice that the order is important. The last name has to go after the first name.

If you called it with:

```bash
$ python main.py Gutiérrez Camila
```

your app wouldn't have a way to know which is the `name` and which the `lastname`. It expects the first _CLI argument_ to be the `name` and the second _CLI argument_ to be the `lastname`.

## What is a CLI Option

Here we will use the word **CLI option** to refer to _CLI parameters_ passed to the CLI application with a specific name. For example, if you go to your terminal and type:

```bash
$ ls --size ./myproject
```

`ls` will show the contents of the directory `./myproject` with their `size`.

- `ls` is the _program_ (or "command", "CLI app").
- `./myproject` is a _CLI argument_.
- `--size` is an optional _CLI option_.

The program knows it has to show the size because it sees `--size`, not because of the order.

A _CLI option_ like `--size` doesn't depend on the order like a _CLI argument_.

So, if you put the `--size` _before_ the _CLI argument_, it still works (in fact, that's the most common way of doing it):

```bash
$ ls --size ./myproject
```

The main visual difference between a _CLI option_ and a _CLI argument_ is that the _CLI option_ has `--` prepended to the name, like in "`--size`".

A _CLI option_ doesn't depend on the order because it has a predefined name (here it's `--size`). This is because the CLI app is looking specifically for a literal `--size` parameter (also known as "flag" or "switch"), with that specific "name" (here the specific name is "`--size`"). The CLI app will check if you typed it or not, it will be actively looking for `--size` even if you didn't type it (to check if it's there or not).

In contrast, the CLI app is not actively looking for the _CLI argument_ with a text "`./myproject`", it has no way to know if you would type `./myproject` or `./my-super-awesome-project` or anything else. It's just waiting to get whatever you give it. The only way to know that you refer to a specific _CLI argument_ is because of the order. The same way that it knows that the first _CLI argument_ was the `name` and the second was the `lastname`, but if you mixed the order, it wouldn't be able to handle it.

Instead, with a _CLI option_, the order doesn't matter.

Also, by default, a _CLI option_ is _optional_ (not _required_).

So, by default:

- A _CLI argument_ is **required**
- A _CLI option_ is **optional**

But the _required_ and _optional_ defaults can be changed.

So, the main and **most important** difference is that:

- _CLI options_ **start with `--`** and don't depend on the order
- _CLI arguments_ depend on the **sequence order**

> **Tip**: In this example above the _CLI option_ `--size` is just a "flag" or "switch" that will contain a boolean value, `True` or `False`, depending on if it was added to the command or not.

This one doesn't receive any values. But _CLI options_ can also receive values like _CLI arguments_. You'll see how later.

## Add one CLI Option

Now add a `--formal` _CLI option_:

```python
import typer

def main(name: str, lastname: str, formal: bool = False):
    if formal:
        print(f"Good day Ms. {name} {lastname}.")
    else:
        print(f"Hello {name} {lastname}")

if __name__ == "__main__":
    typer.run(main)
```

Here `formal` is a `bool` that is `False` by default.

```bash
$ python main.py --help
Usage: main.py [OPTIONS] NAME LASTNAME

Arguments:
  NAME        [required]
  LASTNAME    [required]

Options:
  --formal / --no-formal  [default: no-formal]
  --help                  Show this message and exit.
```

> **Tip**: Notice that it automatically creates a `--formal` and a `--no-formal` because it detected that `formal` is a `bool`.

Now call it normally:

```bash
$ python main.py Camila Gutiérrez --formal
Good day Ms. Camila Gutiérrez.
```

## A CLI Option with a Value

To convert the `lastname` from a _CLI argument_ to a _CLI option_, give it a default value of `""`:

```python
import typer

def main(name: str, lastname: str = "", formal: bool = False):
    if formal:
        print(f"Good day Ms. {name} {lastname}.")
    else:
        print(f"Hello {name} {lastname}")

if __name__ == "__main__":
    typer.run(main)
```

As `lastname` now has a default value of `""` (an empty string) it is no longer required in the function, and **Typer** will now by default make it an optional _CLI option_.

```bash
$ python main.py --help
Usage: main.py [OPTIONS] NAME

Arguments:
  NAME  [required]

Options:
  --lastname TEXT         [default: ]
  --formal / --no-formal  [default: no-formal]
  --help                  Show this message and exit.
```

> **Tip**: Notice the `--lastname`, and notice that it takes a textual value.

A _CLI option_ with a value like `--lastname` (contrary to a _CLI option_ without a value, a `bool` flag, like `--formal` or `--size`) takes as its value whatever is at the _right side_ of the _CLI option_.

```bash
$ python main.py Camila --lastname Gutiérrez
Hello Camila Gutiérrez
```

> **Tip**: Notice that "`Gutiérrez`" is at the right side of `--lastname`. A _CLI option_ with a value takes as its value whatever is at the _right side_.

And as `--lastname` is now a _CLI option_ that doesn't depend on the order, you can pass it before the name:

```bash
$ python main.py --lastname Gutiérrez Camila
Hello Camila Gutiérrez
```

## Document Your CLI App

If you add a docstring to your function it will be used in the help text:

```python
import typer

def main(name: str, lastname: str = "", formal: bool = False):
    """
    Say hi to NAME, optionally with a --lastname.

    If --formal is used, say hi very formally.
    """
    if formal:
        print(f"Good day Ms. {name} {lastname}.")
    else:
        print(f"Hello {name} {lastname}")

if __name__ == "__main__":
    typer.run(main)
```

Now see it with the `--help` option:

```bash
$ python main.py --help
Usage: main.py [OPTIONS] NAME

  Say hi to NAME, optionally with a --lastname.

  If --formal is used, say hi very formally.

Arguments:
  NAME  [required]

Options:
  --lastname TEXT         [default: ]
  --formal / --no-formal  [default: no-formal]
  --help                  Show this message and exit.
```

> **Tip**: There is another place to document the specific _CLI options_ and _CLI arguments_ that will show up next to them in the help text as with `--install-completion` or `--help`, you will learn that later in the tutorial.

## Arguments, Options, Parameters, Optional, Required

Be aware that these terms refer to multiple things depending on the context, and sadly, those "contexts" mix frequently, so it's easy to get confused.

### In Python

In Python, the names of the variables in a function, like `name` and `lastname`:

```python
def main(name: str, lastname: str = ""):
    pass
```

are called "Python function parameters" or "Python function arguments".

> **Technical Details**: There's actually a very small distinction in Python between "parameter" and "argument".

It's quite technical... and somewhat pedantic.

_Parameter_ refers to the variable name in a function _declaration_. Like:

```python
def bring_person(name: str, lastname: str = ""):
    pass
```

_Argument_ refers to the value passed when _calling_ a function. Like:

```python
person = bring_person("Camila", lastname="Gutiérrez")
```

...but you will probably see them used interchangeably in most of the places (including here).

#### Python Default Values

In Python, in a function, a parameter with a _default value_ like `lastname` in:

```python
def main(name: str, lastname: str = ""):
    pass
```

is considered an "optional parameter" (or "optional argument").

The default value can be anything, like `""` or `None`.

And a parameter like `name`, that doesn't have a default value, is considered _required_.

### In CLIs

When talking about command line interface applications, the words **"argument"** and **"parameter"** are commonly used to refer to that data passed to a CLI app, those parameters.

But those words **don't imply** anything about the data being required, needing to be passed in a certain order, nor having a flag like `--lastname`.

The parameters that come with a name like `--lastname` (and optionally a value) are commonly optional, not required. So, when talking about CLIs it's common to call them **optional arguments** or **optional parameters**. Sometimes these _optional parameters_ that start with `--` are also called a **flag** or a **switch**.

In reality, the parameters that require an order can be made _optional_ too. And the ones that come with a flag (like `--lastname`) can be _required_ too.

### In Typer

To try and make it a bit easier, we'll normally use the words "parameter" or "argument" to refer to "Python functions parameters" or "Python functions arguments".

We'll use **_CLI argument_** to refer to those _CLI parameters_ that depend on the specific order. That are **required** by default.

And we'll use **_CLI option_** to refer to those _CLI parameters_ that depend on a name that starts with `--` (like `--lastname`). That are **optional** by default.

We will use **_CLI parameter_** to refer to both, _CLI arguments_ and _CLI options_.

## The `typer` Command

When you install `typer`, by default it adds a `typer` command to your shell.

This `typer` command allows you to run your scripts with ✨ auto completion ✨ in your terminal.

As an alternative to running with Python:

```bash
$ python main.py
```

You can run with the `typer` command:

```bash
$ typer main.py run
```

...and it will give you auto completion in your terminal when you hit `TAB` for all your code.

So you can use it to have auto completion for your own scripts as you continue with the tutorial.

> **Tip**: Your CLI application built with **Typer** won't need the `typer` command to have auto completion once you create a Python package.

But for short scripts and for learning, before creating a Python package, it might be useful.
