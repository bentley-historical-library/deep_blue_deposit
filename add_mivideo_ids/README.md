# Add MiVideo IDs

Updates the items in a [Simple Archive Format](https://wiki.duraspace.org/display/DSDOC5x/Importing+and+Exporting+Items+via+Simple+Archive+Format) directory so that they properly display embedded videos from MiVideo, e.g., in this [Thomas A. Roach interview](https://deepblue.lib.umich.edu/handle/2027.42/134316).

The script will prompt the user for a Deposit ID, then look for the appropriate directory in the Bentley's and MLibrary's shared DeepBlue space. It will then prompt the user for the path (dragging and dropping onto or using the "Copy as path" option and pasting into the Command Prompt should work) to a CSV generated from a deposit to MiVideo.

The script expects the CSV to be formatted like so:

| IDENTIFIER.OTHER | MiVideo_IDs |
|------------------|-------------|
| 2014164_0001_0001 | 1_byeethjd |
| 2014164_0001_0002 | 1_4rl3zhbc |
| 2014164_0001_0003 | 1_a0niphtz; 1_mq3g1qrs |

Note that MiVideo ID entries must be separated by a semicolon space (; ).

The script then:
  * checks to make sure items cannot be downloaded in DeepBlue; 
  * checks to make sure right are correct in DeepBlue metadata; 
  * adds videostreams with MiVideo and Player IDs to items in DeepBlue; and 
  * checks to make sure metadata is visible in DeepBlue.
