pybinMerge
==========

```
Usage: pybinMerge.py [options] file1 file2 [...]

pybinMerge.py will combine a list of files passed to it, in order, and create
a new file with this data. It finds a common subset of bytes between
neighboring files in the list, the length of which can be configured with the
skip option. It also skips a minimum number of bytes at the beginning of each
file, assuming there may be a varying header there that would cause a bad
merge. The number of bytes it skips can be configured with the match option.

Options:
  --version             show program's version number and exit
  -h, --help            show this help message and exit
  -o FILE, --output=FILE
                        write combined output to FILE
  -s NUM, --skip=NUM    skip this many bytes [default: 512]
  -m NUM, --merge=NUM   use this many bytes for a match [default:256]
  ```
