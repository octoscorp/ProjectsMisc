# CTF Tools

This is a collection of tools I've found myself in need of to complete CTFs. I assume many of them effectively duplicate functionality found on Kali Linux or similar, but I've found them to be useful in my context.

See also [CTF guide](guide.md) for notes on CTF practices, and [License](LICENSE.md) for conditions of use.

The `payloads` directory includes payloads that are typically used in file upload contexts. Currently, this is:
* `ctf_remote_shell.php`. When uploaded to a php site which does not sanitise input, making GET requests to the uploaded file URL with `?cmd=<command>` allows remote shell. Hard to test on work internet lol.
