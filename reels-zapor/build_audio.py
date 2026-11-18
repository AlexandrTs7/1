import json, subprocess, wave, sys
lines=[l.rstrip('\n').split('\t') for l in open('lines.tsv',encoding='utf-8') if l.strip()]
TEMPO=1.06; LEAD=0.5; GAP_IN=0.32; GAP_SCENE=0.75; TAIL=2.2; SR=22050
parts=[]; t=LEAD; tl=[]; prev=None
for i,(sc,text) in enumerate(lines,1):
    src=f'audio/l{i:02d}t.wav'; dst=f'audio/f{i:02d}.wav'
    subprocess.run(['ffmpeg','-v','error','-y','-i',src,'-af',f'atempo={TEMPO}','-ar',str(SR),'-ac','1',dst],check=True)
    d=float(subprocess.check_output(['ffprobe','-v','error','-show_entries','format=duration','-of','csv=p=0',dst]))
    if prev is not None: t+= GAP_SCENE if sc!=prev else GAP_IN
    tl.append({'scene':int(sc),'text':text,'start':round(t,3),'end':round(t+d,3)}); t+=d; prev=sc
total=t+TAIL
# build with adelay mix
inputs=[];filt=[]
for i,e in enumerate(tl,1):
    inputs+=['-i',f'audio/f{i:02d}.wav']; ms=int(e['start']*1000)
    filt.append(f'[{i-1}]adelay={ms}|{ms}[a{i}]')
mix=''.join(f'[a{i}]' for i in range(1,len(tl)+1))
filt.append(f'{mix}amix=inputs={len(tl)}:normalize=0,apad,atrim=0:{total:.3f},loudnorm=I=-16:TP=-1.5:LRA=11[out]')
subprocess.run(['ffmpeg','-v','error','-y',*inputs,'-filter_complex',';'.join(filt),'-map','[out]','-ar','48000','-ac','2','voice.wav'],check=True)
json.dump({'total':round(total,3),'lines':tl},open('timeline.json','w',encoding='utf-8'),ensure_ascii=False,indent=1)
print('total',round(total,2))
for e in tl: print(e['scene'],e['start'],e['end'],e['text'][:40])
