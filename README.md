# CoachMate

Overview
---
Software for swim coaches with a focus on data tracking across a season. It includes team management, practice planning, and performance analysis.

HyTek Integration
---
[HyTek's TeamManager](https://hytek.active.com/) is the standard team management software used by swim coaches and organizations. Using the `upload` button on the sidebar, you can upload HyTek roster files and meet results. The support filetypes are `.cl2` and `.hy3`.

<img src="examples/upload.png" height="480" alt="Combined Image" />

Set Writing
---
Sets can be written and added to a practice from the `practice` page. The current layout (see below) is a little clunky but it seemed like what was necessary to be able to capture all of the intricacies of writing a set. The goal in the future is to switch to using a single text box that will parse the input into proper set notation, that way coaches can be more freeform with it.

<img src="examples/set_writing.png" width="480" alt="Combined Image" />

Issues
---
* Because HyTek's software is proprietary and they provide no public API for easily reading their database files, uploading files has been known to not parse all of the information correctly, or just error out all together. If this happens, submit an issue and attach the file you were trying to upload, most likely the layout is slightly off and the parsing class needs to be adjusted.


Notes
---
If you have input on a better way to construct sets, reach out and let me know. It's far from perfect (though it's come a long way), and it would be great if it could be more usable.

For that matter, any feedback on ways to make the site better are always appreciated. As fun as it was to make the site, it's really there to be used so any way in which it can be made easier to use should be addressed.
