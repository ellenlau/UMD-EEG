function erpAR(subjList, expDir, epochDir, arDir, peakToPeakThresh, peakToPeakChan, veogThresh, veogChan, heogThresh, heogChan)

%%This script does artifact rejection and saves out a summary file and an
%%epoch file with the artifacts marked. You should check every summary file
%%manually to make sure it looks reasonable, and you should really also
%%load every subject's art-rej epoch file and just scroll through a few
%%epochs manually to make sure that blinks are being excluded and that
%%non-blinks aren't. This isn't really that onerous if you think how bad it
%%would be to do the entire thing by hand ; )

%%Artifacts aren't actually rejected, they are marked. But if you do the
%%default averaging in ERPLAB, marked epochs will not be included in the
%%average

%%Currently rejects three types of artifacts
%%1. Generally crazy deviations on any channel with peakToPeakThresh
%%2. Blinks with a step function on VEOG
%%3. Eye movements with a step function on HEOG

%%You set the thresholds. A possible set based on ERPLAB manual:
%%100 for peakToPeak, 40 for VEOG, 25 for HEOG. You may want to change them
%%on a subject-by-subject basis. If you do, just make sure that you SAVE
%%these parameters somewhere!!

%%Currently hardcoded are other parameters like the size of the moving
%%window. Feel free to change those. If you don't want to use the entire
%%epoch for artifact rejection, you can change the EEG.xmin and EEG.xmax
%%parameters to the beginning and ending time points that you want

for s = subjList
    
    %%Load epoch file
    [ALLEEG EEG CURRENTSET ALLCOM] = eeglab;
    EEG = pop_loadset('filename',strcat('S',int2str(s),'_elist_nelist_be.set'),'filepath',strcat(expDir, epochDir));
    [ALLEEG, EEG, CURRENTSET] = eeg_store( ALLEEG, EEG, 0 );
    
    %%Peak to peak artifact rejection on all channels
    EEG = pop_artmwppth( EEG, [EEG.xmin*1000  EEG.xmax*1000], peakToPeakThresh, 200, 50,  peakToPeakChan, [ 1 2]);
    [ALLEEG EEG CURRENTSET] = pop_newset(ALLEEG, EEG, 1,'gui','off'); 
    pop_summary_rejectfields(EEG)

    EEG = pop_artstep( EEG, [EEG.xmin*1000  EEG.xmax*1000], veogThresh, 200, 10,  veogChan, [ 1 3]);
    [ALLEEG EEG CURRENTSET] = pop_newset(ALLEEG, EEG, 2,'gui','off'); 

    EEG = pop_artstep( EEG, [EEG.xmin*1000  EEG.xmax*1000], heogThresh, 400, 10,  heogChan, [ 1 4]);
    [ALLEEG EEG CURRENTSET] = pop_newset(ALLEEG, EEG, 3,'gui','off'); 

    pop_summary_AR_eeg_detection(EEG, strcat(expDir, arDir, 'AR_summary_S',int2str(s),'_elist_nelist_be_ar_ar_ar.txt'));

    EEG = pop_sincroartifacts(EEG, 3);
    [ALLEEG EEG CURRENTSET] = pop_newset(ALLEEG, EEG, 4,'gui','off'); 

    EEG = eeg_checkset( EEG );
    EEG = pop_saveset( EEG, 'filename',strcat('S',int2str(s),'_elist_nelist_be_ar_ar_ar.set'),'filepath',strcat(expDir, arDir));
    [ALLEEG EEG] = eeg_store(ALLEEG, EEG, CURRENTSET);
    

end