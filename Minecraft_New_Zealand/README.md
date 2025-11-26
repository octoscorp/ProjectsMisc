# New Zealand in Minecraft

This is a tool intended to allow me to create a map representation of New Zealand in Minecraft. To this end, it must accomplish the following:

[] Identify data from a GeoTIFF file which falls in a certain area
[] Grab the elevation and colour data for an area
[] Collate Minecraft textures combinatorially (for instance, sculk vein over stained glass over a melon) to create pixel arrays for all possible textures
[] Translate elevation data into a height (in blocks) to display in the representation
[] Transform colour data for an area into a 16x16 of "pixels" to match Minecraft textures
[] Compare the transformed colour data to possible textures in order to find the closest

## Resolution

Based on Mt. Cook/Aoraki having a height of 3724 metres and a preferred representation max height of ~100 blocks, the vertical resolution initially chosen is **40 metres to one block** in the representation.

Picking a horizontal resolution can be more challenging, as identifying the total width of New Zealand is also challenging (seriously - try looking up the total width of NZ, if you'd like to go down a rabbit hole). Since the Easternmost and Westernmost points are at different latitudes, identifying the longitudinal distance between them would require more maths than I'm in the mood for. As such, I'm cheating by picking two datasets using the same projection (NZ Transverse Mercator) to avoid needing to think about this. Instead, I can convert by number of pixels.

## Textures
Minecraft block textures are 16 by 16 pixels. This means that real-world colour data for one block's worth in the representation must be transformed into 16 by 16 "pixels" to compare against. 

### Transforming
The source of real-world data I am using has a 10m resolution, meaning that one block in the representation is 200 by 200 data points in the data. While an approach with some overlap could be entirely valid, this would favour the colour in the middle slightly (as data on the edges would be represented on only one "pixel", instead of multiple). Thus, a system of alternating 13 and 12 data points into one pixel is used.

### Combinations
Some textures have gaps (for example, sculk vein) that allow the block underneath to be seen. Others have transparency, but apply a colour to what is seen through them (for example, green stained glass). This allows for a lot of combinations of blocks to get a specific top-down texture, so the following limitations are applied to decrease the combinations that are possible:

- No more than 3 blocks will be used to create a top-down texture.
- No part of the resulting top-down texture may be transparent (so glass can be used, but not solely glass).

To accomplish this, patterns of valid ordering are specified:

- Solid block
- Solid block -> Glass
- Solid block -> Glass -> Partial block
- Solid block -> Partial block
- Solid block -> Partial block -> Glass

# Licensing and Attribution
The outcome of this project is licensed under the Creative Commons Attribution-NonCommercial-ShareAlike 4.0 International license (CC BY-NC-SA 4.0), more detail on which can be found at https://creativecommons.org/licenses/by-nc-sa/4.0/ or in the [LICENSE](../LICENSE) file.
Attribution and licenses for data used can be found in the [attribution](../attribution) directory.