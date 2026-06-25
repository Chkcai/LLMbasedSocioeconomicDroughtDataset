%% Load Data
% The value -99 means Nodata for all the variables in this function
S=load("RF_train_data.mat");
%% DEM
dem=S.dem;
dem_a=[];% dem data average
dem_10=[];% dem 10% quantile
dem_25=[];% dem 25% quantile
dem_50=[];% dem 50% quantile
dem_75=[];% dem 75% quantile
dem_90=[];% dem 90% quantile
for i=1:15
    dem_a=[dem_a,S.dem(:,1)];
    dem_10=[dem_10,S.dem(:,2)];
    dem_25=[dem_25,S.dem(:,3)];
    dem_50=[dem_50,S.dem(:,4)];
    dem_75=[dem_75,S.dem(:,5)];
    dem_90=[dem_90,S.dem(:,6)];
end
%% NDVI and NDWI
ndvi=S.ndvi;
ndwi=S.ndwi;
%% Population and GDP
GDP1=S.GDP1;
GDP2=S.GDP2;
GDP3=S.GDP3;
%% Area
area=[];
for i=1:15
    area=[area,S.area];
end
%% SPEI
SPEI12M=S.SPEI12M;
SPEI6M=S.SPEI6M;
SPEI3M=S.SPEI3M;
SPEI1M=S.SPEI1M;
SPEI12A=S.SPEI12A;%SPEI12SA
SPEI6A=S.SPEI6A;%SPEI6SA
SPEI3A=S.SPEI3A;%SPEI3SA
SPEI1A=S.SPEI1A;%SPEI1SA
%% Socio-economic drought
SED=S.SED;%A variable representing whether socioeconomic drought has occurred
% SED=1 means occurence of socioeconomic drought; SED=0 means non-occurence of socioeconomic drought;
clear S
%% Preprocess
[m,n]=size(SPEI1A);
X=[];
Y=[];
for i=1:m
    for j=1:n
        thisData=[dem_a(i,j),dem_10(i,j),dem_25(i,j),dem_50(i,j),dem_75(i,j),...
            dem_90(i,j),ndvi(i,j),ndwi(i,j),GDP1(i,j),GDP2(i,j),...
            GDP3(i,j),area(i,j),SPEI12M(i,j),SPEI6M(i,j),SPEI3M(i,j),...
            SPEI1M(i,j),SPEI12A(i,j),SPEI6A(i,j),SPEI3A(i,j),SPEI1A(i,j)...
            SED(i,j)];
        mask=thisData==-99;
        if sum(mask)==0
            X=[X;thisData(:,1:end-1)];
            Y=[Y;thisData(:,end)];
        end
    end
end
%% Random Forest
t = templateTree('NumVariablesToSample','all',...
    'PredictorSelection','interaction-curvature','Surrogate','on');

cvp = cvpartition(length(Y),KFold=5);
Mdl = fitcensemble(X,Y,'OptimizeHyperparameters','auto','Learners',t, ...
    'HyperparameterOptimizationOptions',...
    struct('AcquisitionFunctionName','expected-improvement-plus','UseParallel',true,CVPartition=cvp));
[PredictRes,scores] = predict(Mdl ,X);% Only original data are evluated for validation
%% Evaluation indicator
% Confusion matrix
n=length(X);
TP=0;
FN=0;
FP=0;
TN=0;
for i=1:n
    if PredictRes(i)==1&&Y(i)==1
        TP(1,1)=TP(1,1)+1;
    elseif PredictRes(i)==1&&Y(i)==0
        FP=FP+1;
    elseif PredictRes(i)==0&&Y(i)==1
        FN=FN+1;
    else
        TN=TN+1;
    end
end
Accuracy=(TP+TN)/(TP+TN+FP+FN);
P=TP/(TP+FP);
Recall=TP/(TP+FN);
F1=2*(P*Recall)/(P+Recall);
% ROC curve
rocObj = rocmetrics(Y,scores,Mdl.ClassNames);
plot(rocObj)
%% Importance of variables
imp = predictorImportance(Mdl);
oobimp=oobPermutedPredictorImportance(Mdl);