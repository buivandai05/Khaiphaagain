document.addEventListener('DOMContentLoaded', () => {
  const root = document.getElementById('miningResults');
  if (!root) return;
  const algorithm = root.dataset.algorithm;
  const pageSize = 15;
  let itemsets = [], rules = [], itemPage = 1, rulePage = 1;
  const $ = id => document.getElementById(id);
  const cell = (row, value, className = '') => {
    const td = row.insertCell(); td.textContent = value; if (className) td.className = className; return td;
  };
  const pct = value => `${(Number(value) * 100).toFixed(2)}%`;
  const params = () => ({min_support: $('minSup').value, min_confidence: $('minConf').value, min_lift: $('minLift').value});
  function validate() {
    const p = params();
    if (p.min_support === '' || Number(p.min_support) < 0 || Number(p.min_support) > 1 ||
        p.min_confidence === '' || Number(p.min_confidence) < 0 || Number(p.min_confidence) > 1 ||
        p.min_lift === '' || Number(p.min_lift) < 0 || Object.values(p).some(v => !Number.isFinite(Number(v)))) {
      $('pageError').textContent = 'Support và Confidence phải trong khoảng 0–1; Lift phải từ 0 trở lên.';
      $('pageError').classList.remove('d-none'); return false;
    }
    $('pageError').classList.add('d-none'); return true;
  }
  function renderItemsets() {
    const size = $('itemsetSize').value;
    const filtered = itemsets.filter(x => size === 'all' || (size === '4' ? x.size >= 4 : x.size === Number(size)));
    const pages = Math.max(1, Math.ceil(filtered.length / pageSize)); itemPage = Math.min(itemPage, pages);
    const body = $('itemsetsBody'); body.replaceChildren();
    if (!filtered.length) { const r = body.insertRow(); const td = r.insertCell(); td.colSpan = 5; td.className='empty-state'; td.textContent='Không có itemset phù hợp bộ lọc.'; }
    filtered.slice((itemPage-1)*pageSize, itemPage*pageSize).forEach((x, index) => {
      const row = body.insertRow(); cell(row, String((itemPage-1)*pageSize+index+1)); cell(row, x.label); cell(row, String(x.size)); cell(row, pct(x.support)); cell(row, String(x.count));
    });
    $('itemsetsPageInfo').textContent = `${filtered.length} itemsets · trang ${itemPage}/${pages}`;
    $('itemsetsPrev').disabled = itemPage <= 1; $('itemsetsNext').disabled = itemPage >= pages;
  }
  function renderRules() {
    const q = $('ruleSearch').value.trim().toLocaleLowerCase(); const result = $('ruleResult').value;
    const key = $('ruleSort').value;
    const filtered = rules.filter(x => {
      const matchesText = `${x.antecedent_label} ${x.consequent_label}`.toLocaleLowerCase().includes(q);
      const matchesResult = result === 'all' || (result === 'other' ? x.result === null : x.result === result);
      return matchesText && matchesResult;
    }).sort((a,b) => Number(b[key])-Number(a[key]));
    const pages = Math.max(1, Math.ceil(filtered.length/pageSize)); rulePage = Math.min(rulePage,pages);
    const body = $('rulesBody'); body.replaceChildren();
    if (!filtered.length) { const r=body.insertRow(); const td=r.insertCell(); td.colSpan=6; td.className='empty-state'; td.textContent='Không có luật phù hợp bộ lọc.'; }
    filtered.slice((rulePage-1)*pageSize,rulePage*pageSize).forEach((x,index) => {
      const row=body.insertRow(); cell(row,String((rulePage-1)*pageSize+index+1)); cell(row,x.antecedent_label); const resultCell=cell(row,x.consequent_label);
      if (x.result) resultCell.className=x.result === 'WIN' ? 'result-win' : 'result-lose';
      cell(row,pct(x.support)); cell(row,pct(x.confidence)); cell(row,Number(x.lift).toFixed(3));
    });
    $('rulesPageInfo').textContent = `${filtered.length} luật · trang ${rulePage}/${pages}`;
    $('rulesPrev').disabled=rulePage<=1; $('rulesNext').disabled=rulePage>=pages;
  }
  $('runMining').addEventListener('click', async () => {
    if (!validate()) return;
    const button=$('runMining'); button.disabled=true; $('pageLoading').classList.remove('d-none');
    try {
      const response=await fetch(`/api/mining/${algorithm}`,{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify(params())});
      const data=await response.json(); if (!response.ok) throw new Error(data.error || 'Không thể khai phá dữ liệu.');
      $('statTime').textContent=`${data.execution_time_sec.toFixed(4)} giây`;
      $('statItemsets').textContent=data.frequent_itemsets_count.toLocaleString();
      $('statRules').textContent=data.total_rules_count.toLocaleString(); $('statWin').textContent=data.win_rules_count.toLocaleString(); $('statLose').textContent=data.lose_rules_count.toLocaleString();
      itemsets=data.itemsets; rules=data.rules; itemPage=1; rulePage=1; root.classList.remove('d-none'); renderItemsets(); renderRules();
    } catch(error) { $('pageError').textContent=error.message; $('pageError').classList.remove('d-none'); }
    finally { button.disabled=false; $('pageLoading').classList.add('d-none'); }
  });
  $('itemsetSize').addEventListener('change',()=>{itemPage=1;renderItemsets();});
  ['ruleSearch','ruleResult','ruleSort'].forEach(id=>$(id).addEventListener(id==='ruleSearch'?'input':'change',()=>{rulePage=1;renderRules();}));
  $('itemsetsPrev').addEventListener('click',()=>{itemPage--;renderItemsets();}); $('itemsetsNext').addEventListener('click',()=>{itemPage++;renderItemsets();});
  $('rulesPrev').addEventListener('click',()=>{rulePage--;renderRules();}); $('rulesNext').addEventListener('click',()=>{rulePage++;renderRules();});
});
