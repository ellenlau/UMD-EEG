function hdf2eeglab(expDir,fileName,outputDir, subjNum, sampleRate, downSampleRate)

%%This script reads in an h5 file created by cnt2h5 and saves it 
%%out to EEGLAB's .set+.fdt format. 

%%About downSampleQ: If you are reading in raw datafiles
%%sampled at 1000Hz and they are long, you may not have enough memory to
%%open the resulting .set file in EEGLAB later. So if you set downSampleQ
%%to 1, the data will be downsampled by a factor of 2. So if you started
%%with 1000Hz sampling rate, the output dataset would have a sampling rate
%%of 500Hz. This may be a good idea because it will cut your file size in
%%half for all the rest of your analysis, speeding computation, and if you
%%are using a standard online lowpass filter of ~70Hz during recording,
%%you aren't gaining any additional information with 1000Hz vs 500Hz. For
%%sampleRate you should still enter the original sampleRate.

%%In any case you need a fair amount of working memory to read in raw datafiles sampled at
%%1000Hz. May work on a laptop but you may need to close out all other
%%applications and restart MATLAB to clear memory first. 

%%IMPORTANT: The way this conversion script works leads to one minor
%%headache. Even though you call EEGLAB within this function, EEGLAB will
%%look to the global workspace for the variable containing the data to
%%load. So if you defined raw_data in the normal way within this function,
%%the data loading step would fail, since running a function does not
%%automatically create variables in your global workspace.

%%To resolve this, you simply need to run the command 'global raw_data' at
%%the command line before running this script. Then operations including
%%raw_data in the current function will update this global variable, and
%%EEGLAB will then be able to see the global variable to load it. 

%%Suggestions for better workarounds are invited!

%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%

    global raw_data;
    
    
    raw_data = hdf5read(strcat(expDir,fileName),'/data');
    triggers = hdf5read(strcat(expDir,fileName),'/triggers'); %%this is two columns, first column = event code, second column = sample in which it occurred

    numChan = size(raw_data,1);
    numSamples = size(raw_data,2);
    numEvents = size(triggers,2);
    
    %%We will create an additional 'channel' where we mark the event codes on the
    %%appropriate samples. Here we initialize it as a vector of zeros
    triggerLong = zeros(numSamples,1);

    %%Now we fill it in with the actual codes stored in 'triggers'
    for t = 1:25 %numEvents
        tCode= triggers(1,t);
        tSample = triggers(2,t);
        triggerLong(tSample) = tCode;
    end

    %%Finally, we add this new 'channel' to the data array 
    %%**(this computation is slow, can it be optimized?)
    raw_data(numChan+1,:) = triggerLong;

    
    %%Now we read the data array into EEGLAB
    [ALLEEG EEG CURRENTSET ALLCOM] = eeglab;
    EEG = pop_importdata('dataformat','array','nbchan',0,'data','raw_data','setname',strcat('S',int2str(subjNum)),'subject',int2str(subjNum),'srate',sampleRate,'pnts',0,'xmin',0);
    EEG = eeg_checkset( EEG );
    [ALLEEG EEG CURRENTSET] = pop_newset(ALLEEG, EEG, 0,'gui','off');

    %%read event information from trigger 'channel', the extra one
    EEG = pop_chanevent(EEG, numChan+1,'edge','leading','edgelen',0);
    EEG = eeg_checkset( EEG );
    [ALLEEG EEG] = eeg_store(ALLEEG, EEG, CURRENTSET);
        
    %%And downsample if desired
    if downSampleRate ~= 0 
        EEG = pop_resample( EEG, downSampleRate);
        [ALLEEG EEG] = eeg_store(ALLEEG, EEG, CURRENTSET);
    end

    
    
    %%save as EEGLAB dataset (a pair of .set and .fdt files)
    EEG = pop_saveset( EEG, 'filename',strcat('S',int2str(subjNum),'.set'),'filepath',strcat(expDir,outputDir));

    
    

    

