# vidsrc-to-resolver
Resolves m3u8 url for common sources found on https://vidsrc.to/

### Supports
- vidplay.site (https://vidplay.site/)
- filemoon (https://filemoon.sx/)

### Pre-requisites
- [mpv](https://mpv.io/)
- [python3](https://www.python.org/)

### Installation
Download the repo
```git install https://github.com/Ciarands/vidsrc-to-resolver.git```

Move into repo folder
```cd vidsrc-to-resolver```

Download dependencies
```pip install requirements.txt```

Run the file
```python3 vidsrc.py```

### ~~Video~~
*coming soon...*

**[29-12-2023]** I am currently working on an AST parser based solution, with a custom obfuscator.io string reconstructor (no slow dependencies like synchrony or webcrack), which will extract the vidsrc.to keys at runtime (fast 💪).

I have a fair bit of work to do yet, but heres a sneak peek at the unoptimized first iteration on my slow laptop.

https://github.com/Ciarands/vidsrc-to-resolver/assets/74070993/ba277257-a043-4ede-b273-92bcc6ca7663

Will release soon™️, stay posted!

### TODO
- [ ] Finish AST parser string reconstructor 
- [ ] Add QoL features like autoplay 

### Note
This is purely intended as proof of concept, the distribution of program is intended for educational purposes ONLY. 

### Contact
discord - `ciaran_ds`
