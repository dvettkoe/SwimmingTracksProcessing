# SwimmingTracksProcessing
A custom python-based program for the analysis of swimming cycles of C. elegans. Using Swimming Tracks Processing allows to combine and delete tracks after automated tracking by "wrmTrck"

1. Analyze your videos of swimming C. elegans using the ImageJ Plugins wrMTrck (https://www.phage.dk/plugins/wrmtrck.html)
2. Start "swimming_tracks_processing_v1.4.exe" and open the ImageJ Plugin "STProcessing Macro"
3. Open the folder containing videos analyzed in step 1
4. In the Swimming Track Processing window click "Select track file" and select the track displayed in the left corner of the ImageJ window
5. Analyze the processed video by watching each worm track and if one gets lost and tracked again under another number write both numbers into the "Combine tracks" field and press "Combine"
   5.1 Use the following format: 1,2,17,30
       (No spaces and separate the numbers by comma)
6. Repeat for every worm that gets lost and tracked again
7. Write down any number of artifacts that should not be tracked. Insert them into the field "Delete tracks" and press "Delete"
   HINT: Mistakes can be undone but only by one step! If you make more mistakes after another or detect your mistake later, you need to delete the files generated for the "_processed.xlsx" files of the respective video in the source folder.
9. If done either click "Save&proceed" if more videos should be analyzed or "Save&done" if the last video was analyzed.
10. Find and use the processed XLSX files for further data analysis.
   
