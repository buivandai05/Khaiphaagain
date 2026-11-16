document.addEventListener('DOMContentLoaded',()=>{
  const $=id=>document.getElementById(id);let rules=[],page=1;const size=15;
  const params=()=>({min_support:$('arSup').value,min_confidence:$('arConf').value,min_lift:$('arLift').value});
  const pct=v=>`${(Number(v)*100).toFixed(2)}%`;
  function metricCard(rule){if(!rule)return 'Không có luật đạt ngưỡng đã chọn.';return `${rule.antecedent_label} → ${rule.consequent_label} · Confidence ${pct(rule.confidence)} · Lift ${Number(rule.lift).toFixed(3)}`;}
  function draw(){const q=$('arSearch').value.trim().toLocaleLowerCase(),filter=$('arResultFilter').value,key=$('arSort').value;
    const rows=rules.filter(x=>`${x.antecedent_label} ${x.consequent_label}`.toLocaleLowerCase().includes(q)&&(filter==='all'||(filter==='other'?x.result===null:x.result===filter))).sort((a,b)=>b[key]-a[key]);
    const pages=Math.max(1,Math.ceil(rows.length/size));page=Math.min(page,pages);const body=$('arBody');body.replaceChildren();
    if(!rows.length){const tr=body.insertRow(),td=tr.insertCell();td.colSpan=6;td.className='empty-state';td.textContent='Không có luật phù hợp.';}
    rows.slice((page-1)*size,page*size).forEach(item=>{const tr=body.insertRow();[item.algorithm,item.antecedent_label,item.consequent_label,pct(item.support),pct(item.confidence),Number(item.lift).toFixed(3)].forEach(v=>{const td=tr.insertCell();td.textContent=v;});tr.cells[2].className=item.result==='WIN'?'result-win':item.result==='LOSE'?'result-lose':'';tr.tabIndex=0;tr.addEventListener('click',()=>explain(item));});
    $('arPageInfo').textContent=`${rows.length} luật · trang ${page}/${pages}`;$('arPrev').disabled=page<=1;$('arNext').disabled=page>=pages;
  }
  function explain(x){const el=$('ruleExplanation');el.classList.remove('d-none');if(x.result){el.textContent=`Trong transaction có ${x.antecedent_label}, ${pct(x.confidence)} ghi nhận ${x.result}. Confidence của luật cao gấp ${Number(x.lift).toFixed(3)} lần Support chung của vế sau. Đây là liên hệ thống kê, không chứng minh nguyên nhân.`;}else{el.textContent=`${x.antecedent_label} xuất hiện cùng ${x.consequent_label} trong ${pct(x.support)} transaction. Confidence là ${pct(x.confidence)} và Lift là ${Number(x.lift).toFixed(3)}. Đây là mô tả thống kê, không chứng minh quan hệ nhân quả.`;}}
  $('loadRules').addEventListener('click',async()=>{const p=params();if(Number(p.min_support)<0||Number(p.min_support)>1||Number(p.min_confidence)<0||Number(p.min_confidence)>1||Number(p.min_lift)<0||Object.values(p).some(v=>v===''||!Number.isFinite(Number(v)))){$('arError').textContent='Support và Confidence phải trong khoảng 0–1; Lift phải từ 0 trở lên.';$('arError').classList.remove('d-none');return;}
    $('arError').classList.add('d-none');$('arLoading').classList.remove('d-none');$('loadRules').disabled=true;
    try{const res=await fetch('/api/association-rules',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify(p)});const data=await res.json();if(!res.ok)throw new Error(data.error||'Không thể tải luật.');
      $('arApCount').textContent=data.apriori_rules_count.toLocaleString();$('arFpCount').textContent=data.fpgrowth_rules_count.toLocaleString();$('arWinCount').textContent=data.win_rules_count.toLocaleString();$('arLoseCount').textContent=data.lose_rules_count.toLocaleString();$('topConfidence').textContent=metricCard(data.highest_confidence);$('topLift').textContent=metricCard(data.highest_lift);rules=data.rules;page=1;draw();$('arResults').classList.remove('d-none');
    }catch(e){$('arError').textContent=e.message;$('arError').classList.remove('d-none');}finally{$('loadRules').disabled=false;$('arLoading').classList.add('d-none');}});
  ['arSearch','arResultFilter','arSort'].forEach(id=>$(id).addEventListener(id==='arSearch'?'input':'change',()=>{page=1;draw();}));$('arPrev').addEventListener('click',()=>{page--;draw();});$('arNext').addEventListener('click',()=>{page++;draw();});
});
