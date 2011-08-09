function erpEpoch(subjList,expDir, bdfFileName, rawDir, epochDir, begTime, endTime, begBL, endBL)

%%This script takes a set of raw data .set files as input and saves out a
%%set of epoch files--one file for each subject that has the raw data for
%%all events of interest concatenated together. The main reason to save
%%these files out rather than going directly to averaging is that it makes
%%automatic artifact rejection faster and makes it easier to spotcheck it.
%%Also allows you to try different methods of artifact rejection without
%%having to redo the epoching step. 

%%You can also baseline at this step. It is recommended that you do this,
%%using the standard baseline of -100:0 ms. This will save you the trouble
%%of remembering to do this later, and since baselining is a simple shift,
%%you can always re-baseline as many times as you want later if you want
%%to.

%%subjList is a vector of subject numbers. 

%%bdfFileName is the name of a file that defines the codes for the events
%%of interest. Read the wiki or the ERPLAB documentation for info on what
%%format this needs to be in.

%%expDir is the main directory for your experiment. The bdf file needs to
%%be immediately within this directory. You should have subdirectories to
%%store your raw .set files and your output .set epoch files

%%rawDir and epochDir: names of these directories

%%begTime should be beginning of time-window of interest in ms.
%%endTime should be end of time-window of interest in ms. 
%%begBL should be beginning of baseline period in ms.
%%endBL should be end of baseline period in ms.


%%Example:
%%erpEpoch([1 2 3 4 5 6], '/Users/ellen/Documents/Experiments/DAGGER/','test.bdf','raw/','epochs/', -100, 1000, -100, 0)

[ALLEEG EEG CURRENTSET ALLCOM] = eeglab;

[~,n] = size(subjList);
count = 0;

allData = [];

for s = subjList
    count = count + 1;
       
        %%Get data
        EEG = pop_loadset('filename',strcat('S',int2str(s),'.set'),'filepath',strcat(expDir,rawDir));
        %%Create event list
        EEG = pop_creabasiceventlist(EEG, '', {'boundary'}, {-99});
        %%Create bins
        EEG = pop_binlister( EEG, strcat(expDir,bdfFileName), 'no', '', 0, [], [], 0, 0, 0);
        %%Extract bin-based epochs
        EEG = pop_epochbin( EEG , [begTime  endTime],  [begBL  endBL]);
        %%Save EEG set
        [ALLEEG EEG] = eeg_store(ALLEEG, EEG, CURRENTSET);
        EEG = pop_saveset(EEG, 'filename',strcat('S',int2str(s),'_elist_nelist_be'),'filepath',strcat(expDir,epochDir));
        
end



%plot mean at CZ
%figure;plot(-mean(allData(5,:,:),3));

%save subject averages before artifact rejection
%outname = strcat('n',int2str(n),'c',int2str(cond),'lp',int2str(lp),'subjAvg.mat');
%save(outname,'allData');

