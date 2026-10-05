import asyncio,json,random,time
from datetime import datetime
import websockets
from process_config import RIM,ANODIZING,QC,STATIONS
from process_model import required_current_a,oxide_growth_um,predicted_final_thickness,current_density,power_kw
HOST,PORT="localhost",8765
class Twin:
 def __init__(self): self.reset()
 def reset(self):
  self.batch_id=datetime.now().strftime("ANO-%y%m%d-%H%M%S");self.station_index=0;self.status="IDLE";self.started_at=None;self.elapsed_s=0;self.thickness_um=0;self.temperature_c=25;self.current_a=0;self.voltage_v=0
  self.level_pct=ANODIZING["level_target_pct"];self.flow_lpm=ANODIZING["flow_target_lpm"];self.pump_on=False;self.agitation_on=False;self.heater_on=False;self.cooling_on=False;self.rectifier_on=False
  self.disturbance="none";self.color_method="dye";self.dye_color="black";self.rim_color="silver";self.rim_color_phase="raw";self.qc=None;self.alarms=[];self.warnings=[];self.events=["Digital twin initialized."];self.last=time.monotonic()
 def station(self):
  a,b,c,d,e,f=STATIONS[self.station_index]
  if b=="Coloring": c="Organic Dye" if self.color_method=="dye" else "Acidic Metal-Salt Electrolyte"
  return {"index":self.station_index,"code":a,"name":b,"bath":c,"minutes":d,"target_temp":e,"color":f}
 def log(self,x): self.events.append("["+datetime.now().strftime("%H:%M:%S")+"] "+x);self.events=self.events[-40:]
 def set_station(self,i):
  if self.status!="RUNNING" and 0<=i<len(STATIONS): self.station_index=i;self.elapsed_s=0;self.alarms=[];self.warnings=[];self.qc=None;self.log("Selected station: "+STATIONS[i][1])
 def set_disturbance(self,d):
  if d in {"none","temp_high","low_level","low_flow","current_high","current_low","sensor_drift"}:
   self.disturbance=d;self.log("Disturbance cleared." if d=="none" else "Disturbance injected: "+d)
 def start(self):
  if self.status!="RUNNING": self.status="RUNNING";self.started_at=time.monotonic()-self.elapsed_s;self.log("Started "+self.station()["name"])
 def stop(self):
  self.update()
  if self.status=="RUNNING": self.status="STOPPED";self.pump_on=self.agitation_on=self.rectifier_on=False;self.log("Stopped by operator")
 def update(self):
  now=time.monotonic();dt=max(0,now-self.last);self.last=now
  if self.status!="RUNNING": return
  s=self.station();total=s["minutes"]*60;self.elapsed_s=min(now-self.started_at,total)
  target=s["target_temp"]+(7 if self.disturbance=="temp_high" and s["name"]=="DC Anodizing" else 0)
  self.temperature_c+=(target-self.temperature_c)*min(dt/(.8 if target>self.temperature_c else 2),1)
  run=s["name"] in ("DC Anodizing","Coloring","Sealing");self.pump_on=run;self.agitation_on=s["name"] in ("DC Anodizing","Chemical Polishing","Coloring","Sealing");self.heater_on=self.status=="RUNNING" and s["target_temp"]>self.temperature_c+.5;self.cooling_on=self.status=="RUNNING" and s["name"]=="DC Anodizing" and self.temperature_c>ANODIZING["bath_temp_target_c"]+.5;self.rectifier_on=self.status=="RUNNING" and s["name"]=="DC Anodizing"
  level_target=ANODIZING["level_target_pct"]-(12 if self.disturbance=="low_level" and s["name"]=="DC Anodizing" else 0);self.level_pct+=(level_target-self.level_pct)*.06
  flow_target=ANODIZING["flow_target_lpm"] if self.pump_on else 0
  if self.disturbance=="low_flow" and self.pump_on: flow_target*=.55
  self.flow_lpm+=(flow_target-self.flow_lpm)*.08
  # Visual workpiece state: raw aluminium starts silver, anodizing creates an oxide surface,
  # and the coloring station progressively changes the virtual rim to the selected dye color.
  if s["name"] in ("Loading","Degreasing","Water Wash 1","Chemical Polishing","Water Wash 2","Neutralization","Water Wash 3"):
   self.rim_color="silver"; self.rim_color_phase="silver / uncoated"
  elif s["name"]=="DC Anodizing":
   self.rim_color="oxide"; self.rim_color_phase="anodized / clear oxide"
   target_current=required_current_a();target_current*=1.12 if self.disturbance=="current_high" else .82 if self.disturbance=="current_low" else 1
   self.current_a=max(0,target_current*min(self.elapsed_s/12,1)+random.uniform(-.5,.5));self.voltage_v=max(0,ANODIZING["voltage_v"]+random.uniform(-.25,.25))
   if self.disturbance=="sensor_drift": self.temperature_c+=2.5
   self.thickness_um=min(ANODIZING["max_thickness_um"]+5,self.thickness_um+oxide_growth_um(self.current_a,dt))
  elif s["name"]=="Coloring":
   # Organic dye is intentionally visualized as a silver-to-black transition during the coloring cycle.
   p=self.elapsed_s/max(1,total)
   if self.color_method=="dye":
    self.rim_color_phase=f"dyeing — {p*100:.0f}%"
    self.rim_color="black" if p>=0.88 else ("dark-gray" if p>=0.55 else "silver")
   else:
    self.rim_color_phase=f"electrocolor — {p*100:.0f}%"
    self.rim_color="dark-gray" if p>=0.88 else ("gray" if p>=0.55 else "silver")
   self.current_a=max(0,3+random.uniform(-.3,.3));self.voltage_v=max(0,8+random.uniform(-.3,.3))
  elif s["name"] in ("Water Wash 4","Water Wash 5","Sealing","Hot Water Wash","Unloading","QC Inspection"):
   self.rim_color="black" if self.color_method=="dye" else "dark-gray"
   self.rim_color_phase="finished colored coating"
   self.current_a=max(0,2+random.uniform(-.3,.3));self.voltage_v=max(0,10+random.uniform(-.3,.3))
  else:
   self.current_a=max(0,2+random.uniform(-.3,.3));self.voltage_v=max(0,10+random.uniform(-.3,.3))
  self.evaluate()
  if self.elapsed_s>=total: self.complete()
 def evaluate(self):
  self.alarms=[];self.warnings=[]
  if self.station()["name"]!="DC Anodizing": return
  if self.temperature_c>ANODIZING["bath_temp_max_c"]: self.alarms.append("HIGH BATH TEMPERATURE")
  elif self.temperature_c>ANODIZING["bath_temp_max_c"]-2: self.warnings.append("Bath temperature approaching high limit")
  if self.level_pct<ANODIZING["level_min_pct"]: self.alarms.append("LOW ELECTROLYTE LEVEL")
  if self.flow_lpm<ANODIZING["flow_min_lpm"]: self.alarms.append("LOW PUMP / CIRCULATION FLOW")
  cd=current_density(self.current_a)
  if cd>ANODIZING["current_density_a_dm2"]*1.08:self.alarms.append("HIGH CURRENT DENSITY")
  elif cd<ANODIZING["current_density_a_dm2"]*.92:self.warnings.append("Current density below nominal")
  remaining=max(0,self.station()["minutes"]*60-self.elapsed_s);pred=predicted_final_thickness(self.thickness_um,max(self.current_a,required_current_a()),remaining)
  if pred>ANODIZING["max_thickness_um"]:self.alarms.append("PREDICTED OVER-THICKNESS")
  if pred<ANODIZING["min_thickness_um"] and remaining<120:self.warnings.append("PREDICTED UNDER-THICKNESS")
 def complete(self):
  name=self.station()["name"];self.log("Completed "+name)
  if name=="QC Inspection": self.run_qc();self.status="QC HOLD";return
  if self.station_index<len(STATIONS)-1:self.station_index+=1;self.elapsed_s=0;self.status="IDLE"
 def run_qc(self):
  thickness=max(0,self.thickness_um+random.uniform(-.45,.45));gloss=random.uniform(72,90);de=random.uniform(.8,3.8);seal=len(self.alarms)==0
  tp=QC["thickness_min_um"]<=thickness<=QC["thickness_max_um"];gp=QC["gloss_min_gu"]<=gloss<=QC["gloss_max_gu"];cp=de<=QC["delta_e_max"];overall=tp and gp and cp and seal
  self.qc={"thickness_um":round(thickness,2),"thickness_spec":f'{QC["thickness_min_um"]}–{QC["thickness_max_um"]} µm',"thickness_pass":tp,"gloss_gu":round(gloss,1),"gloss_spec":f'>= {QC["gloss_min_gu"]} GU',"gloss_pass":gp,"delta_e":round(de,2),"delta_e_spec":f'<= {QC["delta_e_max"]}',"color_pass":cp,"sealing":"PASS" if seal else "FAIL","sealing_pass":seal,"overall":"PASS" if overall else "FAIL"}
  self.log(f"QC {self.qc['overall']}: thickness {thickness:.2f} µm, gloss {gloss:.1f} GU, ΔE {de:.2f}")
 def state(self):
  self.update();s=self.station();remaining=max(0,s["minutes"]*60-self.elapsed_s);pred=self.thickness_um
  if s["name"]=="DC Anodizing":pred=predicted_final_thickness(self.thickness_um,max(self.current_a,required_current_a()),remaining)
  return {"batch":{"id":self.batch_id,"material":RIM["material"],"rim_size":RIM["size"],"area_in2":RIM["surface_area_in2"],"color_method":self.color_method,"dye_color":self.dye_color,"target_thickness_um":ANODIZING["target_thickness_um"]},"status":self.status,"station":s,"stations":[{"code":x[0],"name":x[1],"minutes":x[3]} for x in STATIONS],"elapsed_s":self.elapsed_s,"remaining_s":remaining,"progress":min(100,self.elapsed_s/(s["minutes"]*60)*100),"telemetry":{"temperature_c":self.temperature_c,"current_a":self.current_a,"voltage_v":self.voltage_v,"power_kw":power_kw(self.voltage_v,self.current_a),"current_density_a_dm2":current_density(self.current_a),"thickness_um":self.thickness_um,"predicted_final_um":pred,"level_pct":self.level_pct,"flow_lpm":self.flow_lpm},"equipment":{"pump_on":self.pump_on,"agitation_on":self.agitation_on,"heater_on":self.heater_on,"cooling_on":self.cooling_on,"rectifier_on":self.rectifier_on},"disturbance":self.disturbance,"rim_visual":{"color":self.rim_color,"phase":self.rim_color_phase},"alarms":list(dict.fromkeys(self.alarms)),"warnings":list(dict.fromkeys(self.warnings)),"qc":self.qc,"events":self.events[-30:]}
twin=Twin();clients=set()
async def handler(ws):
 clients.add(ws)
 try:
  await ws.send(json.dumps(twin.state()))
  async for raw in ws:
   c=json.loads(raw);a=c.get("cmd")
   if a=="start":twin.start()
   elif a=="stop":twin.stop()
   elif a=="reset":twin.reset()
   elif a=="select_station":twin.set_station(int(c.get("index",0)))
   elif a=="set_color_method" and twin.status!="RUNNING" and c.get("method") in ("dye","electro"):twin.color_method=c["method"]
   elif a in ("set_disturbance","clear_disturbance"):twin.set_disturbance(c.get("disturbance","none") if a=="set_disturbance" else "none")
   await ws.send(json.dumps(twin.state()))
 finally: clients.discard(ws)
async def broadcast():
 while True:
  twin.update()
  if clients:
   p=json.dumps(twin.state());await asyncio.gather(*(x.send(p) for x in list(clients)),return_exceptions=True)
  await asyncio.sleep(.5)
async def main():
 print("D.I.D Anodizing Digital Twin V3: ws://localhost:8765")
 async with websockets.serve(handler,HOST,PORT): await broadcast()
if __name__=="__main__":asyncio.run(main())
