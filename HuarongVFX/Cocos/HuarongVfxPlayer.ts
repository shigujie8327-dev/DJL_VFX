/** Cocos Creator 3.8 integration template. See INTEGRATION.md before importing. */
import { _decorator, Component, Node, JsonAsset, Sprite, SpriteFrame, UITransform, UIOpacity, resources, Vec3 } from 'cc';
const { ccclass, property } = _decorator;
type Cue = {asset:string;start:number;duration:number;anchor:string;w:number;h:number;x:number;y:number;alpha:number;scaleFrom:number;scaleTo:number;dx:number;dy:number;rotation:number;spin:number;envelope:string;motion?:'smooth'|'in';rotationEase?:boolean;loop?:boolean;tag?:string;curve?:{control:[number,number];endAnchor:string;endOffset:[number,number]};orientToPath?:boolean;reveal?:boolean;mirrorX?:boolean};
type Asset = {id:string;file:string;layer:string};
type Entry = {cues:Cue[];stopTags?:string[]};
type Live = {cue:Cue;age:number;node:Node;opacity:UIOpacity;anchor:Node;parent:UITransform};
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
 private ready=false;
 /** Call once before starting combat; catches missing textures and bindings early. */
 async prepare():Promise<void>{
  if(!this.manifest||!this.eventLibrary)throw Error('Bind manifest.json and vfx-events.json');
  this.entries=this.eventLibrary.json.events;
  const assets:Asset[]=this.manifest.json.assets;
  await Promise.all(assets.map(async a=>{
   this.assets.set(a.id,a);
   const resourcePath=a.file.replace(/\.png$/,'')+'/spriteFrame';
   const frame=await new Promise<SpriteFrame>((resolve,reject)=>resources.load(resourcePath,SpriteFrame,(err,frame)=>err?reject(err):resolve(frame)));
   this.frames.set(a.id,frame);
  }));
  for(const entry of Object.values(this.entries))for(const cue of entry.cues){
   if(!this.anchors.some(n=>n.name===cue.anchor))throw Error('Missing anchor '+cue.anchor);
   if(cue.curve&&!this.anchors.some(n=>n.name===cue.curve!.endAnchor))throw Error('Missing curve end anchor '+cue.curve.endAnchor);
   const layer=this.assets.get(cue.asset)?.layer;
   if(!this.layers.some(n=>n.name===layer&&n.getComponent(UITransform)))throw Error('Missing UI layer '+layer);
  }
  this.ready=true;
 }
 /** Plays visuals only. Damage, chance rolls, distance and UI remain owned by battle logic. */
 emit(event:string):void{
  if(!this.ready)throw Error('await prepare() before emit');
  const entry=this.entries[event];if(!entry)throw Error('Unknown VFX event '+event);
  for(const tag of entry.stopTags||[])this.stopTag(tag);
  for(const cue of entry.cues){
   const asset=this.assets.get(cue.asset)!;
   const parent=this.layers.find(n=>n.name===asset.layer)!;
   const anchor=this.anchors.find(n=>n.name===cue.anchor)!;
   const node=new Node(cue.asset);node.layer=parent.layer;node.setParent(parent);
   const transform=node.addComponent(UITransform);transform.setContentSize(cue.w,cue.h);
   const sprite=node.addComponent(Sprite);sprite.sizeMode=Sprite.SizeMode.CUSTOM;sprite.spriteFrame=this.frames.get(cue.asset)!;
   if(cue.reveal){sprite.type=Sprite.Type.FILLED;sprite.fillType=Sprite.FillType.HORIZONTAL;sprite.fillStart=0;sprite.fillRange=0;}
   const opacity=node.addComponent(UIOpacity);opacity.opacity=0;
   this.active.push({cue:{...cue},age:-cue.start,node,opacity,anchor,parent:parent.getComponent(UITransform)!});
  }
 }
 /** Call once for each resolved hit, with an index from 1 to 4. */
 hitVolley(index:number):void{
  if(!Number.isInteger(index)||index<1||index>4)throw Error('Volley hit index must be 1..4');
  this.emit(`LianzhuJian.Hit${index}`);
 }
 enterFar():void{this.emit('XiaoLiGuang.EnterFar');}
 leaveFar():void{this.emit('XiaoLiGuang.LeaveFar');}
 stopTag(tag:string):void{
  this.active=this.active.filter(v=>{if(v.cue.tag!==tag)return true;v.node.destroy();return false;});
 }
 update(dt:number):void{
  this.active=this.active.filter(v=>{
   const c=v.cue;v.age+=dt;if(v.age<0)return true;
   if(!v.node.isValid)return false;
   if(!v.anchor.isValid){v.node.destroy();return false;}
   if(!c.loop&&v.age>=c.duration){v.node.destroy();return false;}
   const p=clamp(v.age/c.duration),e=c.motion==='smooth'?p*p*(3-2*p):c.motion==='in'?p*p:1-(1-p)**3;
   const envelope=c.loop?clamp(v.age/.08):c.envelope==='transfer'?Math.min(1,p*20,(1-p)*20):c.envelope==='hold'?Math.min(1,p*15,(1-p)*15):Math.min(1,p*9)*Math.pow(1-p,.65);
   v.opacity.opacity=Math.round(255*c.alpha*envelope);
   const pos=v.parent.convertToNodeSpaceAR(v.anchor.worldPosition,new Vec3());
   // Authoring coordinates are Y-down; Cocos UI is Y-up.
   let x=pos.x+c.x+c.dx*e,y=pos.y-c.y-c.dy*e;
   let angle=-(c.rotation+c.spin*(c.rotationEase?e:p));
   if(c.curve){const endAnchor=this.anchors.find(n=>n.name===c.curve!.endAnchor)!;
    const ep=v.parent.convertToNodeSpaceAR(endAnchor.worldPosition,new Vec3());
    const sx=pos.x+c.x,sy=pos.y-c.y,cx=pos.x+c.curve.control[0],cy=pos.y-c.curve.control[1],ex=ep.x+c.curve.endOffset[0],ey=ep.y-c.curve.endOffset[1],u=1-e;
    x=u*u*sx+2*u*e*cx+e*e*ex;y=u*u*sy+2*u*e*cy+e*e*ey;
    if(c.orientToPath)angle=Math.atan2(2*u*(cy-sy)+2*e*(ey-cy),2*u*(cx-sx)+2*e*(ex-cx))*180/Math.PI;
   }
   nodePosition(v.node,x,y);
   const scale=c.scaleFrom+(c.scaleTo-c.scaleFrom)*e;v.node.setScale(c.mirrorX?-scale:scale,scale,1);v.node.angle=angle;
   if(c.reveal)v.node.getComponent(Sprite)!.fillRange=e;
   return true;
  });
 }
 resetBattle():void{for(const v of this.active)v.node.destroy();this.active=[];}
 onDisable():void{this.resetBattle();}
}
function nodePosition(node:Node,x:number,y:number){node.setPosition(x,y,0);}
