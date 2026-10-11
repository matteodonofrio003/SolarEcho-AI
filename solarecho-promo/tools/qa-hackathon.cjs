const {bundle}=require('@remotion/bundler');
const {selectComposition,renderStill,openBrowser}=require('@remotion/renderer');
const path=require('path');
(async()=>{
 const serveUrl=await bundle({entryPoint:path.resolve('src/index.ts'),enableCaching:true,rspack:true,onProgress:p=>console.log('Bundle',p)});
 const browser=await openBrowser('chrome');
 const composition=await selectComposition({serveUrl,id:'SolarEcho-Hackathon',puppeteerInstance:browser});
 for(const frame of [180,360,750,1020,1170,1280,1460,1750,1920,2160,2310,2530,2840,3110,3400]){
  await renderStill({serveUrl,composition,frame,puppeteerInstance:browser,output:path.resolve('../video_output/analisi/qa',`still-${frame}.png`),logLevel:'warn'});
  console.log('QA frame',frame);
 }
 await browser.close({silent:true});
})().catch(e=>{console.error(e);process.exit(1)});
