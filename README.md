StupidCensor
===========

a REVERSABLE image censoring tool

to reversably mosiac censor jpeg files

to temporarily remove image details

not allowed on most websites like

nudity and/or censored speech, the 

original image can be completely restored

without any quality loss but shouldn't

be recognizable by most automated scanning

tools or the naked eye

#### How it works

It changes the quant tables to cause 8x8

blocks to render as a single color, basically

its full mosiac pixelation, but it saves the

original quant tables in the jpeg so if you

run the same tool on it again it restores those

tables and the full image is restored!

#### Unfinished

I'm thinking I might also allow for different

pixel sizes, because 8x8 is not very obscuring

for large images, but in order to do that it

will be far more challenging because I'll have

to decompress/recompress all of the image data.

#### Warning

NOT INTENDED for sensitive, private, or
illegal data

The reversable censoring methods are simple, open,

and obvious. It will only deter casual viewers

and automated image scanners used for flagging

content or censorship.

#### Useful applications

Handy for sharing LEGAL pのrnのgrムphソ, 

avoiding copyright issues, and sharing images

that might otherwise violate terms of service.

Allowing you to collaborate on ero-manga translation

projects on platforms that don't otherwise allow

such content.

#### Requirements

Python3 with standard modules

#### Installation

Just move the stupidcensor.py into your path somewhere
and make sure it has run permission.

#### Usage

stupidcensor.py -h for basic options but generally

use:

 stupidcensor.py yourjpgfile -o newjpgfile

this will create a mosiac censored copy of your image

run it again on the new file to reverse it

use the -i option if you want to overwrite the original

check stupidcensor.py -h for more options

#### Unlicense

This is free and unencumbered software

released into the public domain

under the unlicense. For more information,

please refer to <http://unlicense.org>

