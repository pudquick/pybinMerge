#!/usr/bin/python

from optparse import OptionParser
import sys

def buffer_read(file_object, chunk_size=1024):
    while True:
        data = file_object.read(chunk_size)
        if not data:
            break
        yield data

def buffer_copy(input_file, output_file):
    for chunk in buffer_read(input_file):
        output_file.write(chunk)

def backwards_merge(infile, newfile, sksize=512, psize=256):
    # Skip to the beginning, and then skip sksize bytes in, on the new file
    newfile.seek(sksize,0)
    # Get a thumbprint of psize bytes from it
    t_print = newfile.read(psize)
    # Skip to the end of our main file
    infile.seek(0,2)
    # Get its length
    endpoint = (infile.tell() + 1L) * -1L
    # Make a generator of reverse byte positions
    backwalk = xrange(-1,endpoint,-1)
    # Find our last byte of the thumbprint
    last_byte = t_print[-1]
    # Loop from the end to beginning of the main file, looking for that byte
    for i in backwalk:
        infile.seek(i,2)
        test_byte = infile.read(1)
        if test_byte == last_byte:
            # possible match here, need to read psize ending on it
            infile.seek(i-psize+1, 2)
            test_print = infile.read(psize)
            if (test_print == t_print):
                # Found a match, begin merging content, as our cursors on both should be equal
                print "STATUS: Found match at byte %s, merging ..." % (infile.tell())
                buffer_copy(newfile,infile)
                print "STATUS: Merge complete"
                return
    print "ERROR: No merge point found using %s skip bytes and %s print bytes" % (sksize, psize)
    sys.exit(1)

def main():
    parser = OptionParser(usage="usage: %prog [options] file1 file2 [...]", version="%prog 1.0")
    parser.add_option("-o", "--output", dest="outfile", type="string",
        help="write combined output to FILE", metavar="FILE", default="output.data")
    parser.add_option("-s", "--skip", dest="skipbytes", type="int",
        help="skip this many bytes [default: 512]", metavar="NUM", default=512)
    parser.add_option("-p", "--print", dest="printbytes", type="int",
        help="use this many bytes for a match [default:256]", metavar="NUM", default=256)
    (options, args) = parser.parse_args()
    if (len(args) < 2):
        return parser.print_help()
    # Create the base from the first file
    try:
        outfile = open(options.outfile, "r+b")
    except:
        outfile = open(options.outfile, "wb")
        outfile.close()
        outfile = open(options.outfile, "r+b")
    srcfile = open(args[0], "rb")
    print "STATUS: Creating base from:", args[0]
    buffer_copy(srcfile, outfile)
    srcfile.close()
    print "STATUS: Beginning comparison of remaining files"
    for nextfile in args[1:]:
        nfile = open(nextfile, "rb")
        print "STATUS: Processing", nextfile, "..."
        # Now start searching, from the end of the outfile, for our thumbprint
        backwards_merge(outfile, nfile, options.skipbytes, options.printbytes)
        nfile.close()
    outfile.close()

if __name__ == "__main__":
    main()