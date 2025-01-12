function [] = xferlock(nn)
global clpos fldist repdist stateradio1 stateradio2 flag
%initialize hardware
%
%ssscom4=serial('COM4','Terminator','CR/LF');%serial-1
%fopen(ssscom4);%serial-2
%
ao=analogoutput('dtol',0);
addchannel(ao,0,'Out000');
addchannel(ao,1,'Out001');
putsample(ao,[0 0]);
ai=analoginput('dtol',0);
ai.inputtype='Differential';
addchannel(ai,0,'Chan000');
addchannel(ai,1,'Chan001');
addchannel(ai,2,'Chan002');
addchannel(ai,3,'Chan003');
ai.TriggerType='HwDigital';
ai.TriggerCondition='RisingEdge';
ai.SamplesPerTrigger=1875;ai.SampleRate=37500;
%
%clpos=24;
%fldist=0.12
%repdist=-2.9;
%
n=1;
flag=1;
laser3ctrl=0;
laser4ctrl=0;
reffldist=0;
recaptureflag=0;
%tracermatrix2=zeros(nn,9);%tracer-1
outputserialtemp=0;
outputserialpressure=0;
%tracermatrix3=zeros(nn,7);
%tracermatrix4=zeros(nn,6);
%offset=[];
%laser3v=[];
figure;hndlplt=gca;
%%%
while(n<=nn) & (flag==1)
%putsample(ao,[0 0]);
%
%
%
start(ai);
wait(ai,1);
[d,t]=getdata(ai);
%
%
%
%nonlin. correction
b=5;
a=1-b*0.05;
cl = 1000*(a*t + b*t.^2);
%prescaling
d(:,2)=10*d(:,2);
d(:,3)=5*d(:,3);
d(:,4)=40*d(:,4);%50
%peak detection
%
%%%
%
d2=d(:,2);
k2=find(d2<-3);%%%-3
nr=numel(k2);
if nr==0
disp('no signal');
else
k2=[k2(1)-1;k2;2000];
end
%%%%%%
clm=[];
krow=[];
for mm=2:nr+2
if nr==0
disp('no signal');
elseif (k2(mm)-k2(mm-1) < 10)
krow=[krow k2(mm)];
elseif (k2(mm-1)>50) && (k2(mm-1) < 1825)
%find line center
clm=[clm sum(cl(krow).*(d2(krow)).^6)/sum((d2(krow)).^6)];
krow=k2(mm);
else
krow=k2(mm);
end
end
%%%%%%
peakpos=clm;
disp(peakpos);
if numel(peakpos) > 1
diffm=[peakpos,0]-[0,peakpos];
diffm(1)=[];diffm(numel(diffm))=[];
disp(diffm);
disp(std(diffm));
else
disp('n/a');
end
%datetagstr=datestr(now,'yyyymmddHHMMSS');datetag=str2double(datetagstr);tracermatrix2(n,1)=datetag;%tracer-2
%tracermatrix2(n,4:3+numel(peakpos))=peakpos;%tracer-3
%
%%%
%
%%%%%%%%%%%%
%
%%%
%
d3=d(:,3);
k3=find(d3<-3);%%%-5
nr3=numel(k3);
if nr3==0
disp('no signal');
else
k3=[k3(1)-1;k3;2000];
end
%%%%%%
clm3=[];
krow3=[];
for mm=2:nr3+2
if nr3==0
disp('no signal');
elseif (k3(mm)-k3(mm-1) < 10)
krow3=[krow3 k3(mm)];
elseif (k3(mm-1)>50) && (k3(mm-1) < 1825)
%find line center
clm3=[clm3 sum(cl(krow3).*(d3(krow3)).^6)/sum((d3(krow3)).^6)];
krow3=k3(mm);
else
krow3=k3(mm);
end
end
%%%%%%
peakpos3=clm3;
disp(peakpos3);
if numel(peakpos3) > 1
diffm3=[peakpos3,0]-[0,peakpos3];
diffm3(1)=[];diffm3(numel(diffm3))=[];
disp(diffm3);
disp(std(diffm3));
else
disp('n/a');
end
%tracermatrix3(n,1:numel(peakpos3))=peakpos3;
%
%%%
%
d4=d(:,4);
k4=find(d4<-3);%%%-3
nr4=numel(k4);
if nr4==0
disp('no signal');
else
k4=[k4(1)-1;k4;2000];
end
%%%%%%
clm4=[];
krow4=[];
for mm=2:nr4+2
if nr4==0
disp('no signal');
elseif (k4(mm)-k4(mm-1) < 10)
krow4=[krow4 k4(mm)];
elseif (k4(mm-1)>50) && (k4(mm-1) < 1825)
%find line center
clm4=[clm4 sum(cl(krow4).*(d4(krow4)).^6)/sum((d4(krow4)).^6)];
krow4=k4(mm);
else
krow4=k4(mm);
end
end
%%%%%%
plot(hndlplt,cl,d,clm,-4*ones(1,numel(clm)),'+k',clm3,-4.5*ones(1,numel(clm3)),'+k',clm4,-5*ones(1,numel(clm4)),'+k');
axis(hndlplt,[0 50 -5.5 0.5]);%%%[0 50 -5 0.5]
%hold on;
%plot(hndlplt,clm,-4*ones(1,numel(clm)),'+');
%plot(hndlplt,clm3,-4.5*ones(1,numel(clm3)),'+');
%plot(hndlplt,clm4,-5*ones(1,numel(clm4)),'+');
%hold off;
peakpos4=clm4;
disp(peakpos4);
if numel(peakpos4) > 1
diffm4=[peakpos4,0]-[0,peakpos4];
diffm4(1)=[];diffm4(numel(diffm4))=[];
disp(diffm4);
disp(std(diffm4));
else
disp('n/a');
end
%tracermatrix4(n,1:numel(peakpos4))=peakpos4;
%
%%%
%fluorescence monitor (added 4/16/2015):
d1mean=mean(d(:,1));
if stateradio1==1 && d1mean<0.05 && recaptureflag==0
reffldist=fldist;
fldist=reffldist-0.3;
recaptureflag=1;
beep;
end
switch recaptureflag
case 0
case 1
beep;
if d1mean>0.05
fldist=reffldist;
recaptureflag=2;
end
if stateradio1==0
fldist=reffldist;
recaptureflag=0;
end
case 2
if d1mean>0.5 || stateradio1==0
recaptureflag=0;
end
end
%%%%%%%%%%%%
%
%adjust lasers
%Fl-Laser
%[minval,clmrefind]=min(abs(clm-clpos));
%[min3val,clm3refind]=min(abs(clm3-(clpos+fldist)));
%offset3ref=clm3(clm3refind)-clm(clmrefind)
%offset=[offset offset3ref];
%if offset3ref>fldist
%laser3ctrl=laser3ctrl+0.001;
%elseif offset3ref<fldist
%laser3ctrl=laser3ctrl-0.001;
%end
%laser3v=[laser3v laser3ctrl];
%if abs(laser3ctrl)<1.5
%putsample(ao,[laser3ctrl laser4ctrl]);
%end
%laser3ctrl%
%%%
[minval,clmrefind]=min(abs(clm-clpos));
[min3val,clm3refind]=min(abs(clm3-(clpos+fldist)));
offset3ref=clm3(clm3refind)-clm(clmrefind)
err3=offset3ref-fldist;
laser3ctrl=laser3ctrl+0.1*err3%ctrl SHG: +0.1*, ECDL: -0.3*
if stateradio1==0
laser3ctrl=0;%
end
if abs(laser3ctrl)<1.5 & abs(laser4ctrl)<1.5
putsample(ao,[laser3ctrl laser4ctrl]);
else
beep;
end
%%%
%
%Rep-Laser
[minval,clmrefind]=min(abs(clm-clpos));
[min4val,clm4refind]=min(abs(clm4-(clm(clmrefind)+repdist)));% (3/21/2014) clpos -> clm(clmrefind)
offset4ref=clm4(clm4refind)-clm(clmrefind)
err=offset4ref-repdist;
%%%%%%%%%% (2/13/2014) added isempty-test
if isempty(err)
beep;
else
laser4ctrl=laser4ctrl-0.15*err
end
%%%%%%%%%%
if stateradio2==0
laser4ctrl=0;%
end
if abs(laser4ctrl)<1.5 & abs(laser3ctrl)<1.5
putsample(ao,[laser3ctrl laser4ctrl]);
else
beep;
end
%
%serial-3-5 start
%if n>500010 & mod(n,2)==1%was 10
%%n is odd
%fprintf(ssscom4,'%s','a');
%elseif n>500010 & mod(n,2)==0%was 10
%%n is even
%outputserialtemp=fscanf(ssscom4,'%e');
%outputserialpressure=fscanf(ssscom4,'%e');
%end
%tracermatrix2(n,2)=outputserialtemp;
%tracermatrix2(n,3)=outputserialpressure;
%outputserialpressure
%
%serial-3-5 stop
%
n=n+1;
end
%%%
%assignin('base', 'tracermatrix2', tracermatrix2);
%assignin('base', 'tracermatrix3', tracermatrix3);
%assignin('base', 'tracermatrix4', tracermatrix4);
%assignin('base', 'offset', offset);
%assignin('base', 'laser3v', laser3v);
%figure;plot(tracermatrix2);
%putsample(ao,[0 0]);
datetagstr00=datestr(now,'yyyymmddHHMMSS');
%save(['c:\xferlockfiles\xfer',datetagstr00],'tracermatrix2');%tracer-4
%
%fclose(ssscom4);%serial-6
%delete(ssscom4);%serial-7
%clear ssscom4%serial-8
%
putsample(ao,[0 0]);
delete(ao)
clear ao
delete(ai)
clear ai
clear tracermatrix2
