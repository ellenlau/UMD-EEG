function data = getERP(subjList,expDir, erpDir, cond,chan)

%%this just extracts all the subject averages for a given condition into a
%%channel x sample x subject matrix. 

%%You can choose the channels you want in vector format, and the 

eeglab

subjCount = 0;
for s = subjList
    subjCount = subjCount + 1;
    filename = strcat('s',int2str(s),'.erp')    
    ERP = pop_loaderp({ filename }, strcat(expDir, erpDir));
    subjData = ERP.bindata(chan,:,cond);
    data(:,:,subjCount) = subjData;
end

