const $=id=>document.getElementById(id);let lastJob=null;let lastAlertedKey='';let lastShownNonBlocking=[];const dismissedProviders=new Set();
function n(v){return Number(v||0).toLocaleString()}
function toast(message){$('toast').textContent=message;$('toast').classList.remove('hidden');setTimeout(()=>$('toast').classList.add('hidden'),3500)}
function errorText(detail,fallback){if(!detail)return fallback;if(Array.isArray(detail))return detail.map(e=>(e&&e.msg)?e.msg:JSON.stringify(e)).join('; ');if(typeof detail==='object')return detail.msg||JSON.stringify(detail);return String(detail)}
async function json(url,options){const response=await fetch(url,options);const data=await response.json().catch(()=>({}));if(!response.ok)throw new Error(errorText(data.detail,`Request failed (${response.status})`));return data}
function statusClass(value){if(value==='RUNNING'||value==='QUEUED')return'running';if(value==='COMPLETE')return'complete';if(value==='SHORTAGE'||value==='NEEDS_KEY')return'warning';if(value==='FAILED')return'failed';return'idle'}

// Every provider the pipeline calls (apify/groq/tavily) is checked on every poll, not
// just the one a running job happens to crash into. A provider with zero ACTIVE keys
// shows up here regardless of whether a job is even running.
function openKeyModal(providers,blockingProvider){
  const heading=blockingProvider?`${blockingProvider} is out of usable keys`:`${providers.join(', ')} need${providers.length===1?'s':''} attention`;
  const body=blockingProvider
    ? `Every ${blockingProvider} key is exhausted or invalid, so the run is paused. All committed data is safe.`
    : `These providers have no active key right now. The run keeps going on whatever still works, but calls to ${providers.join('/')} will fail until you add one.`;
  $('key-eyebrow').textContent=blockingProvider?'⚠ RUN PAUSED':'⚠ API KEY NEEDED';
  $('key-heading').textContent=heading;
  $('key-body').textContent=body+' Pick the provider and paste one or more replacement keys (comma or newline separated) - saved to the key pool and to env-keys/.env.';
  const select=$('key-provider-select');
  select.value=blockingProvider||providers[0];
  $('key-modal').classList.remove('hidden');
  $('key-input').focus();
}

function render(data){const m=data.metrics,j=data.job;lastJob=j;$('target').value=j?.target_golden||$('target').value;$('m-researched').textContent=n(m.researched_people);$('m-validated').textContent=n(m.validated_people);$('m-golden').textContent=n(m.golden_people);$('m-remaining').textContent=n(m.remaining);$('m-accounts').textContent=n(m.accounts_pass);$('m-evidence').textContent=n(m.evidence);$('q-review').textContent=n(m.review_people);$('q-rejected').textContent=n(m.rejected_people);$('q-duplicates').textContent=`${n(m.duplicate_people)} / ${n(m.duplicate_candidates)}`;$('q-universe').textContent=n(m.universe);$('progress-label').textContent=`${n(m.new_golden)} of ${n(m.target)} new Golden people`;$('progress-pct').textContent=`${m.progress_pct}%`;$('progress-bar').style.width=`${m.progress_pct}%`;const state=j?.status||'IDLE';$('job-status').textContent=state;$('job-status').className=`status ${statusClass(state)}`;$('stage-label').textContent=j?`Current stage: ${j.current_stage||state} · Run ${j.job_id}${j.mode==='PEOPLE_ONLY'?' · people only':''}`:'No active job.';$('export-link').classList.toggle('disabled',!j?.workbook_path);
  const providerList=$('provider-list');providerList.innerHTML='';const needy=data.providers_needing_keys||[];for(const provider of ['tavily','groq','apify']){const states=data.providers[provider]||[];const active=states.find(x=>x.state==='ACTIVE')?.count||0;const exhausted=states.filter(x=>x.state!=='ACTIVE').reduce((a,x)=>a+x.count,0);const row=document.createElement('div');if(needy.includes(provider))row.classList.add('provider-needy');row.innerHTML=`<span class="provider-name">${provider}</span><span class="provider-state">${active} active${exhausted?` · ${exhausted} unavailable`:''}${needy.includes(provider)?' · needs a key':''}</span>`;providerList.appendChild(row)}
  const events=$('events');events.innerHTML=data.events.length?'':'<div class="empty">Start a run to see stage output.</div>';for(const event of data.events){const row=document.createElement('div');row.className=`event ${event.level.toLowerCase()}`;const time=new Date(event.created_at).toLocaleTimeString([],{hour:'2-digit',minute:'2-digit',second:'2-digit'});row.innerHTML=`<time>${time}</time><span class="stage">${event.stage||''}</span><span class="message"></span>`;row.querySelector('.message').textContent=event.message;events.appendChild(row)}events.scrollTop=events.scrollHeight;

  const blocking=state==='NEEDS_KEY'?j.required_provider:null;
  const toShow=blocking?[blocking]:needy.filter(p=>!dismissedProviders.has(p));
  lastShownNonBlocking=blocking?[]:toShow;
  const alertKey=blocking?`blocking:${blocking}`:(toShow.length?`proactive:${toShow.join(',')}`:'');
  if(toShow.length){
    if(alertKey!==lastAlertedKey){
      toast(blocking?`⚠ ${blocking} is failing - every key is exhausted or invalid. Add new keys to continue.`
                    :`⚠ ${toShow.join(', ')} ${toShow.length===1?'has':'have'} no active key.`);
      lastAlertedKey=alertKey;
    }
    openKeyModal(blocking?[blocking]:toShow,blocking);
  } else {
    lastAlertedKey='';
  }
}
async function refresh(){try{render(await json('/api/status'))}catch(e){toast(e.message)}}
$('run-form').addEventListener('submit',async e=>{e.preventDefault();try{const mode=$('people-only').checked?'PEOPLE_ONLY':'FULL';const result=await json('/api/jobs',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({target:Number($('target').value),mode})});toast(`Started ${result.job_id}${mode==='PEOPLE_ONLY'?' (people only)':''}`);await refresh()}catch(error){toast(error.message)}});
$('add-keys-btn').addEventListener('click',()=>{const needy=(lastJob&&lastJob.status==='NEEDS_KEY')?[lastJob.required_provider]:['apify','groq','tavily'];openKeyModal(needy,lastJob&&lastJob.status==='NEEDS_KEY'?lastJob.required_provider:null)});
$('key-form').addEventListener('submit',async e=>{e.preventDefault();$('key-error').textContent='';const provider=$('key-provider-select').value;try{const result=await json('/api/keys',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({provider,keys:$('key-input').value,job_id:lastJob?.job_id})});$('key-input').value='';$('key-modal').classList.add('hidden');dismissedProviders.delete(provider);const envNote=result.persisted_to_env?' Saved to env-keys/.env too.':'';toast(result.resumed?`${result.count} key(s) saved. Run resumed.${envNote}`:`${result.count} key(s) saved.${envNote}`);await refresh()}catch(error){$('key-error').textContent=error.message}});
$('cancel-key').addEventListener('click',()=>{
  // Closing a proactive (non-blocking) alert dismisses those providers until the
  // needy set changes again. Closing a blocking NEEDS_KEY pause only hides it for
  // this poll - the run is genuinely stuck, so it reappears on the next refresh
  // rather than silently staying hidden forever.
  for(const p of lastShownNonBlocking)dismissedProviders.add(p);
  $('key-modal').classList.add('hidden');
});
$('refresh').addEventListener('click',refresh);refresh();setInterval(refresh,3000);
