# Vidsrc.to Resolver/CLI
*A simple cli for fetching content from vidsrc.to by resolving m3u8's from common sources used by the site.*

### Info
*While I plan on maintaining this for the foreseeable future, please note that I do intend to eventually archive this and merge all the work here into a package consisting of all other sources I have previously worked on.*

*Consider this a usable public dev build, I wont be pushing any breaking changes.*

### TODO
- [ ] ~~Finish AST parser string reconstructor~~
- [ ] Add QoL features like autoplay 
- [x] Add basic search functionality
- [ ] Add download functionality
- [ ] Allow users to customise certain output, such as the tmdb response string(s)
- [ ] Add more configurability (allow users to pass their own subtitles url/file, ect)
- [ ] Add settings file and allow users to save their prefrences e.g default-subtitles
- [ ] Save user media data + watch time

---

### Supports
- vidplay.site (https://vidplay.site/)
- filemoon (https://filemoon.sx/)

---

### Pre-requisites
- mpv-player (https://mpv.io/)
- python3 (https://www.python.org/)

---

### Installation
Download the repo

```git clone https://github.com/Ciarands/vidsrc-to-resolver.git```

Move into repo folder

```cd vidsrc-to-resolver```

Download dependencies

```pip install -r requirements.txt```

Run the file

```python3 vidsrc.py```

---

### Usage

```python3 vidsrc.py --help```

---

**[29-12-2023]** AST Parser / Obfuscator.io string reconstructor

I am currently working on an AST parser based solution, with a custom obfuscator.io string reconstructor (no slow dependencies like synchrony or webcrack), which will extract the vidsrc.to keys at runtime (fast 💪).
I have a fair bit of work to do yet, but heres a sneak peek at the unoptimized first iteration on my slow laptop.

Will release soon™️, stay posted!

https://github.com/Ciarands/vidsrc-to-resolver/assets/74070993/ba277257-a043-4ede-b273-92bcc6ca7663

### Video [31/12/2023]

https://github.com/Ciarands/vidsrc-to-resolver/assets/74070993/2dcf8e1d-0011-4241-8c67-afcb5faca7e1

---

### Note
This is purely intended as proof of concept, the distribution of program is intended for educational purposes ONLY. 

### Contact
discord - `ciaran_ds`
