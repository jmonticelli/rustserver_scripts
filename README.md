# Rust Server Scripts

This is a repository that contains some scripts to help facilitate automating Rust server management.
This was written for LGSM running on Debian, but will probably mostly work on other Linux distros.

## Disclaimer

:warning: **This software is offered with ABSOLUTELY NO WARRANTY nor any expectation or guarantee that it will work.**

:bangbang: I am **not responsible** for anything in this repository bringing down your server, or causing loss of data or file corruption, in the event that it causes you harm.
:fire: The nature of this repository is potentially destructive. :fire:

:heavy_check_mark: By using this repository, you understand that you are responsible for your own actions.

## Rust Wipe Utilitiy

The Rust Wipe utility is a python script that wipes a RustServer, assuming your LGSM `rustserver` script is in the executing user's home directory.

This script can be run like so:
```bash
python3 rust_wipe.py                                                \
    --now                                                           \
    --bps                                                           \
    --vanilla                                                       \
    --size 3000                                                     \
    --max-players 50                                                \
    --server-name "My Super Cool Rust Server"                       \
    --location "USA"                                                
```
