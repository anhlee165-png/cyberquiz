const CQ=(()=>{const C=window.CQ_CONFIG||{};const on=!!(C.SUPABASE_URL&&C.SUPABASE_ANON_KEY);
const H={apikey:C.SUPABASE_ANON_KEY,Authorization:"Bearer "+C.SUPABASE_ANON_KEY,"Content-Type":"application/json"};
async function rpc(fn,args){const r=await fetch(C.SUPABASE_URL+"/rest/v1/rpc/"+fn,{method:"POST",headers:H,body:JSON.stringify(args||{})});const t=await r.text();let j;try{j=JSON.parse(t)}catch{j=t}if(!r.ok)throw new Error((j&&j.message)||t);return j}
async function loadQuestions(){if(on){try{const r=await fetch(C.SUPABASE_URL+"/rest/v1/questions?select=*&order=id",{headers:H});if(r.ok){const a=await r.json();if(a.length)return a}}catch(e){}}
 const r=await fetch(new URL("questions.json",document.baseURI.replace(/admin\/.*$/,"")),{cache:"no-store"});return (await r.json()).questions.filter(q=>!q.hidden)}
return{C,on,rpc,loadQuestions}})();
