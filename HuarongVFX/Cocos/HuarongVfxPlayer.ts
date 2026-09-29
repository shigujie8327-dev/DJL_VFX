/** Cocos Creator 3.8 VFX-only template. Battle Core remains authoritative. */
import { _decorator, Component, Node, JsonAsset, Sprite, SpriteFrame, UITransform, UIOpacity, resources, Vec3 } from 'cc';
const { ccclass, property } = _decorator;
type Cue={asset:string;start:number;duration:number;anchor:string;w:number;h:number;x:number;y:number;alpha:number;scaleFrom:number;scaleTo:number;dx:number;dy:number;envelope:string;loop?:boolean;tag?:string;revealTo?:number;mirrorX?:boolean};
type Asset={id:string;file:string;layer:string};
type Entry={cues:Cue[];stopTags?:string[]};
type Live={cue:Cue;age:number;node:Node;opacity:UIOpacity;anchor:Node;parent:UITransform};
const clamp=(x:number)=>Math.max(0,Math.min(1,x));

@ccclass('HuarongVfxPlayer')
export class HuarongVfxPlayer extends Component {
 @property(JsonAsset) manifest:JsonAsset|null=null;
 @property(JsonAsset) eventLibrary:JsonAsset|null=null;
 @property({type:[Node]}) anchors:Node[]=[];
 @property({type:[Node]}) layers:Node[]=[];
 private frames=new Map<string,SpriteFrame>();
 private assets=new Map<string,Asset>();
 private entries:Record<string,Entry>={};
 private active:Live[]=[];
 private dingshenActive=false;
 private farPassive=false;
 private ready=false;

 async prepare():Promise<void>{
  if(!this.manifest||!this.eventLibrary)throw Error('Bind manifest.json and vfx-events.json');
  this.entries=this.eventLibrary.json.events;
  const list:Asset[]=this.manifest.json.assets;
  await Promise.all(list.map(async a=>{
   this.assets.set(a.id,a);
   const resourcePath=a.file.replace(/\.png$/,'')+'/spriteFrame';
   const frame=await new Promise<SpriteFrame>((resolve,reject)=>resources.load(resourcePath,SpriteFrame,(err,f)=>err?reject(err):resolve(f)));
   this.frames.set(a.id,frame);
  }));
  for(const entry of Object.values(this.entries))for(const cue of entry.cues){
   if(!this.anchors.some(n=>n.name===cue.anchor))throw Error('Missing anchor '+cue.anchor);
   const layer=this.assets.get(cue.asset)?.layer;
   if(!this.layers.some(n=>n.name===layer&&n.getComponent(UITransform)))throw Error('Missing UI layer '+layer);
  }
  this.ready=true;
 }

 emit(event:string):void{
  if(!this.ready)throw Error('await prepare() before emit');
  const entry=this.entries[event];if(!entry)throw Error('Unknown Huarong VFX event '+event);
  for(const tag of entry.stopTags||[])this.stopTag(tag);
  for(const cue of entry.cues){
   const asset=this.assets.get(cue.asset)!;
   const parent=this.layers.find(n=>n.name===asset.layer)!;
   const anchor=this.anchors.find(n=>n.name===cue.anchor)!;
   const node=new Node(cue.asset);node.layer=parent.layer;node.setParent(parent);
   const t=node.addComponent(UITransform);t.setContentSize(cue.w,cue.h);
   const s=node.addComponent(Sprite);s.sizeMode=Sprite.SizeMode.CUSTOM;s.spriteFrame=this.frames.get(cue.asset)!;
   if(cue.revealTo!==undefined){s.type=Sprite.Type.FILLED;s.fillType=Sprite.FillType.HORIZONTAL;s.fillStart=0;s.fillRange=0;}
   const opacity=node.addComponent(UIOpacity);opacity.opacity=0;
   this.active.push({cue:{...cue},age:-cue.start,node,opacity,anchor,parent:parent.getComponent(UITransform)!});
  }
 }

 resolveRetreatDistance(success:boolean):void{this.emit(success?'Tuishenjian.DistanceSuccess':'Tuishenjian.DistanceBlocked');}
 applyDingshen():void{this.dingshenActive=true;this.emit('Dingshenjian.Apply');}
 pulseDingshenCost():void{if(this.dingshenActive)this.emit('Dingshenjian.CostPulse');}
 expireDingshen():void{if(!this.dingshenActive)return;this.dingshenActive=false;this.emit('Dingshenjian.End');}
 setFarPassive(active:boolean):void{if(active===this.farPassive)return;this.farPassive=active;this.emit(active?'Xiaoliguang.Activate':'Xiaoliguang.Deactivate');}

 stopTag(tag:string):void{this.active=this.active.filter(v=>{if(v.cue.tag!==tag)return true;v.node.destroy();return false;});}
 update(dt:number):void{
  this.active=this.active.filter(v=>{
   const c=v.cue;v.age+=dt;if(v.age<0)return true;
   if(!v.node.isValid||!v.anchor.isValid){if(v.node.isValid)v.node.destroy();return false;}
   if(!c.loop&&v.age>=c.duration){v.node.destroy();return false;}
   const p=clamp(v.age/c.duration),e=p*p*(3-2*p);
   const env=c.loop?clamp(v.age/.08):c.envelope==='transfer'?Math.min(1,p*12,(1-p)*12):c.envelope==='hold'?Math.min(1,p*12,(1-p)*12):Math.min(1,p*8)*Math.pow(1-p,.55);
   v.opacity.opacity=Math.round(255*c.alpha*env);
   const pos=v.parent.convertToNodeSpaceAR(v.anchor.worldPosition,new Vec3());
   v.node.setPosition(pos.x+c.x+c.dx*e,pos.y-c.y-c.dy*e,0);
   const scale=c.scaleFrom+(c.scaleTo-c.scaleFrom)*e;v.node.setScale(c.mirrorX?-scale:scale,scale,1);
   if(c.revealTo!==undefined)v.node.getComponent(Sprite)!.fillRange=c.revealTo*e;
   return true;
  });
 }
 resetBattle():void{for(const v of this.active)v.node.destroy();this.active=[];this.dingshenActive=false;this.farPassive=false;}
 onDisable():void{this.resetBattle();}
}
