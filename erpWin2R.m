function erpWin2R(subjList, expDir, erpDir, resultsDir, condList, chan, timePair,sampleRate,baseline,label)

%%This is a pilot version, so make sure to spotcheck that it is giving you
%%the right numbers!

%%Get out a table to be processed in R for doing stats over time-windows
%%Outputs text file with 4 columns: subject, condition, electrode, and mean
%%amplitude for the time-window

%%subjList is a vector with subject numbers

%%expDir is the main directory for your experiment.

%%erpDir is the directory where your .erp files

%%resultsDir is the output directory for the text file

%%condList is a vector with event code numbers

%%chan is a vector of channel numbers whose data will be included in table

%%timePair is a pair of times in ms, e.g. [300 500]

%%sampleRate is in Hz, e.g. 1000

%%baseline is the length of the pre-trigger baseline period in ms, e.g. if
%%you specified an epoch of -100:1000, this would be 100.

%%label is the name of the output file that will be specific to the
%%conditions you are examining, e.g. 'c1c2' or 'lofreq_hifreq' or '2x2'

%%example: 
%%erpWin2R([1:6],'/Users/ellen/Documents/Experiments/DAGGER/','erp/','results/',1:2,1:32,[300 500],1000,100,'test');

scalingFactor = 1000/sampleRate;

samp1 = round(timePair(1)/scalingFactor + baseline/scalingFactor)
samp2 = round(timePair(2)/scalingFactor + baseline/scalingFactor)

dataV = [];
subjV = [];
condV = [];
chanV = [];

for c = condList
    
    data = getERP(subjList,expDir, erpDir, c, chan);

    %%Mean across time-window for channel of interest
    dataM = squeeze(mean(data(:,samp1:samp2,:),2));
    [numChan,numSubj] = size(dataM);
    for s = 1:numSubj
        dataV = [dataV;dataM(:,s)];
        subjV = [subjV;ones(numChan,1)*s];
        condV = [condV;ones(numChan,1)*c];
        chanV = [chanV;chan'];
    end
end
allData = [subjV condV chanV dataV];
size(allData)

outFile = strcat(expDir, resultsDir, 'n',int2str(numSubj),'_',label,'_t',int2str(timePair(1)),'-',int2str(timePair(2)),'.txt')
dlmwrite(outFile,allData,'\t');