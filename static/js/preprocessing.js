document.addEventListener('DOMContentLoaded', () => {
  let page=1,totalPages=1;
  const $=id=>document.getElementById(id);
  function render(data) {
    const s=data.stats;
    [['ppTotal',s.total_transactions],['ppHeroes',s.unique_heroes],['ppWins',s.win_count],['ppLoses',s.lose_count],['ppComplete',s.complete_five_heroes],['ppUnmapped',s.unmapped_hero_ids]].forEach(([id,value])=>$(id).textContent=Number(value).toLocaleString());
    const steps=$('processSteps'); steps.replaceChildren(); data.steps.forEach(text=>{const li=document.createElement('li');li.textContent=text;steps.append(li);});
    const body=$('transactionsBody');body.replaceChildren();
    if (!data.rows.length) {const r=body.insertRow();const c=r.insertCell();c.colSpan=6;c.className='empty-state';c.textContent='Không có transaction.';}
    data.rows.forEach(item=>{
      const row=body.insertRow();[item.index,item.game_id,item.team_id].forEach(value=>{const td=row.insertCell();td.textContent=String(value);});
      const heroes=row.insertCell();heroes.className='hero-list';item.heroes.forEach((name,index)=>{const badge=document.createElement('span');badge.className='hero-chip';badge.textContent=name;heroes.append(badge);if(index<item.heroes.length-1) heroes.append(document.createTextNode(' '));});
      const count=row.insertCell();count.textContent=String(item.hero_count);
      const result=row.insertCell();result.textContent=item.result;result.className=item.result==='WIN'?'result-win':'result-lose';
    });
    page=data.page;totalPages=data.total_pages;$('ppPageInfo').textContent=`${s.total_transactions.toLocaleString()} transactions · trang ${page}/${totalPages}`;
    $('ppPrev').disabled=page<=1;$('ppNext').disabled=page>=totalPages;$('preprocessContent').classList.remove('d-none');
  }
  async function load() {
    $('preprocessLoading').classList.remove('d-none');$('preprocessError').classList.add('d-none');
    try {const res=await fetch(`/api/preprocessing?page=${page}&per_page=${$('ppPageSize').value}`);const data=await res.json();if(!res.ok)throw new Error(data.error||'Không thể tải dữ liệu.');render(data);}
    catch(error){$('preprocessError').textContent=error.message;$('preprocessError').classList.remove('d-none');}
    finally{$('preprocessLoading').classList.add('d-none');}
  }
  $('refreshData').addEventListener('click',()=>{page=1;load();});$('ppPageSize').addEventListener('change',()=>{page=1;load();});
  $('ppPrev').addEventListener('click',()=>{if(page>1){page--;load();}});$('ppNext').addEventListener('click',()=>{if(page<totalPages){page++;load();}});load();
});
