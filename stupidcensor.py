#!/usr/bin/python3

# Stupid Censor
#
# a REVERSABLE image censoring tool
# to reversably mosiac censor jpeg files
# to temporarily remove image details
# not allowed on most websites like
# nudity and/or censored speech, the 
# original image can be completely restored
# without any quality loss but can be made
# unrecognizable by most automated scanning
# tools or the naked eye
#
# NOT INTENDED for sensitive, private
# or illegal data! can be EASILY reversed
# by professionals or investigators
#
# This is free and unencumbered software
# released into the public domain
# under the unlicense. For more information,
# please refer to <http://unlicense.org>

import argparse, sys;
from struct import unpack, pack_into;

sectiondescriptor = b'stupidcensor\0\0\0\0';

argparser = argparse.ArgumentParser();
argparser.add_argument("inputfile");
argparser.add_argument("-o", "--outfile", dest="outfile", default=None,
                       help="destination filename to write to");
argparser.add_argument("-i", "--inline", dest="inline", action='store_true', default=None,
                       help="overwrites existing file");
argparser.add_argument("-v", "--verbose", dest="debug", action='store_const', default=lambda *n: None, const=print,
                       help="turn out debug output");
# only censors using mosiac pixelation with 8x8 'pixel' sizes for now
#argparser.add_argument("-s", dest="size", action='store_true', default=8, type=int,
#                       help="censored pixel size (multiple of 8)");

args = argparser.parse_args();
debug = args.debug;


# handle start of image
def start_image():
    global data;
    debug("Start image");
    # always only 2 bytes
    sections.append(data[:2]);
    data = data[2:];    


# handle quant_table sections
#   the main way this censoring works is by setting the
#   factors for all but the DCT entries to 0 except for the first, which is a big fat 8x8 pixel
#   this nullifies all of the finer detail data, even though its still actually in the file
#   it SHOULDN'T be rendered at all
def quant_table():
    global data, censored_data;

    # tables can be stored in the same section together or seperately.. so 
    (length,) = unpack(">H", data[2:4]);

    # save just the section tag seperate
    sections.append(data[:4]);
    data = data[4:];

    # save as many tables as are in the section
    length -= 2;
    while(length > 0):
        # if there is previously censored data to restore. restore it
        if(censored_data):
            debug("restoring quant table");
            sections.append(censored_data[:65]);
            censored_data = censored_data[65:];
        else:
            debug("Quant table");
            sections.append(bytearray(data[:65]));
        quant_tables.append(sections[-1]);
        data = data[65:];
        length -= 65;
    if(length != 0):
        print("error: quant section contained unexpected data");
        sys.exit(1);


# handle censor_data section
#   this section header could be used by other apps
#   but if its mine it indicates the image is already
#   censored, so uncensor it
def censor_data():
    global data, censored_data;
    (length, apptype) = unpack(">H16s", data[2:20]);
    if(apptype != sectiondescriptor):
        return irrelevant_section();
    debug("stupidcensor section\n switching to uncensor mode");
    censored_data = data[:2 + length][20:]
    data = data[2 + length:];
    #debug(censored_data);


# handle huffman_table entries
def huffman_table():
    global data, elements, huffman_trees;
    debug("Huffman table");
    (length, header, ) = unpack(">HB", data[2:5]);
    header = (header >> 3) | (header & 0x01); 
    lengths = list(unpack("BBBBBBBBBBBBBBBB", data[5:21]));
    debug(('Y_DC', 'Y_AC', 'C_DC', 'C_AC')[header]);
    debug(lengths);
    elements = list(unpack("B" * sum(lengths), data[21:21 + sum(lengths)]));
    debug(elements);

    # this important function loads the important parts of the
    #   huffman tables into a binary tree mapping to the values
    def make_huff(bits, depth):
        global elements;
        tree = [];
        for i in [0,1]:
            if(lengths[depth]):
                lengths[depth] -= 1;
                debug(bits + str(i), elements[0]);
                tree.append(elements[0]);
                elements = elements[1:];
            elif(len(elements)):
                tree.append(make_huff(bits + str(i), depth + 1));
        return tree;

    # load the huff table!
    hufftree = make_huff('', 0);
    debug(hufftree);
    huffman_trees[header] = hufftree;
    # work in progress - loading huff trees, not using them yet..
    # this WON'T load everything correctly for the EXIF formatted ones which seem to cram all of the tables into the same header
    # it also WON'T load the progressive tables that are defined within scan data yet.. i'll figure that out later
    

    # truncate and return like normal
    sections.append(data[:2 + length]);
    data = data[2 + length:];


# handle the image data
def image_scan():
    global data;
    # there is a seperate section right before the actual image data
    debug("Start scan");
    (length, ) = unpack(">H", data[2:4]);
    sections.append(data[:2 + length]);
    data = data[2 + length:];

    # finally the actual image data
    sections.append(data[:-2]);
    image_data = sections[-1];
    data = data[-2:];


# handle irrelevant sections by skipping them
def irrelevant_section():
    global data;
    debug("Skipping irrelevant section");
    (byte0, byte1, length,) = unpack(">BBH", data[:4]);
    if(byte0 != 0xFF):
        print("invalid jpeg format! - jpeg sections should always start with FF");
        sys.exit(1);
    sections.append(data[:2 + length]);
    data = data[2 + length:];


# handle the end of the image
def end_image():
    global data;
    debug("End image");
    sections.append(data);
    data = [];


sections = [];
quant_tables = [];
image_data = None;
censored_data = None;
huffman_trees = {};
section_handlers = {
    0xFFD8: start_image,
    0xFFDB: quant_table,
    0xFFDA: image_scan,
    0xFFC4: huffman_table,
    0xFFEC: censor_data,
    0xFFD9: end_image,
}


# set a default fileout? and mode?
if(not args.outfile and not args.inline):
    print("Must specify an output file with -o inline overwrite with -i");
    sys.exit(1);

if(args.inline):
    args.outfile = args.inputfile;

# just read the whole damn thing, do it all in memory.. 
with open(args.inputfile, 'rb') as inf:
    data = inf.read();

# parse all of the sections
while(len(data)):
    (section,) = unpack(">H", data[:2]);
    section_handlers.get(section, irrelevant_section)();

# if were NOT restoring censored data, censor now
if(not censored_data):
    # first save the original tables to a stupidcensor section
    firstquantindex = sections.index(quant_tables[0]) - 1;
    censored_data = bytearray(b"\xFF\xEC\0\0" + sectiondescriptor);
    for table in quant_tables:
        censored_data += table;
        debug("censoring quant table");
        for i in range(2, len(table)):
            table[i] = 0;
    censored_data += b"v1";
    pack_into(">H", censored_data, 2, len(censored_data) - 2);
    sections.insert(firstquantindex, censored_data);


# write the file out
with open(args.outfile, 'wb') as outf:
    for section in sections:
        outf.write(section);

