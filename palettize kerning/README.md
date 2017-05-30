## palettize kerning

To be used with [fontTools](https://github.com/behdad/fonttools).

Reduces the number of different kerning values in the font, similar to a GIF or PNG-8 color palette.

This is lossy but should be nearly imperceptible. max_tweak_relative can be used to set the amount by which the kerning values may deviate from the source. The approach is a bit more refined than simple quantization and usually leads to smaller average deviation.

The aim is to allow for better compression in webfonts and reduce the webfont file size. We achieve around 2%—4% size reduction for our woff/woff2 fonts.
