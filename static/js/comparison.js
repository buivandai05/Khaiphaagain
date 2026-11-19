document.addEventListener('DOMContentLoaded', () => {
  const $ = id => document.getElementById(id);
  let charts = [];
  const params = () => ({min_support: $('cmpSup').value, min_confidence: $('cmpConf').value, min_lift: $('cmpLift').value, max_heroes: $('cmpMaxHeroes').value});
  function chart(id, label, a, b) {
    charts.push(new Chart($(id), {type: 'bar', data: {labels: ['Apriori', 'FP-Growth'], datasets: [{label, data: [a, b], backgroundColor: ['#3aafff', '#06d6a0'], borderRadius: 6}]}, options: {responsive: true, maintainAspectRatio: false, plugins: {legend: {display: false}}, scales: {x: {ticks: {color: '#d7e1f3'}, grid: {color: '#263655'}}, y: {beginAtZero: true, ticks: {color: '#d7e1f3'}, grid: {color: '#263655'}}}}}));
  }
  $('runComparison').addEventListener('click', async () => {
    const p = params();
    if (Object.values(p).some(v => v === '' || !Number.isFinite(Number(v))) || Number(p.min_support) < 0 || Number(p.min_support) > 1 || Number(p.min_confidence) < 0 || Number(p.min_confidence) > 1 || Number(p.min_lift) < 0 || !Number.isInteger(Number(p.max_heroes)) || Number(p.max_heroes) < 2 || Number(p.max_heroes) > 5) {
      $('cmpError').textContent = 'Support và Confidence phải từ 0 đến 1; Lift từ 0 trở lên; số tướng từ 2 đến 5.'; $('cmpError').classList.remove('d-none'); return;
    }
    $('cmpError').classList.add('d-none'); $('runComparison').disabled = true; $('cmpLoading').classList.remove('d-none');
    try {
      const response = await fetch('/api/compare', {method: 'POST', headers: {'Content-Type': 'application/json'}, body: JSON.stringify(p)});
      const data = await response.json(); if (!response.ok) throw new Error(data.error || 'Không thể so sánh thuật toán.');
      const a = data.apriori, b = data.fpgrowth, body = $('comparisonBody'); body.replaceChildren();
      [['Thời gian thực thi (giây)', a.execution_time_sec, b.execution_time_sec], ['Frequent itemsets', a.frequent_itemsets_count, b.frequent_itemsets_count], ['Association rules', a.total_rules_count, b.total_rules_count], ['Luật WIN', a.win_rules_count, b.win_rules_count], ['Luật LOSE', a.lose_rules_count, b.lose_rules_count], ['Đội hình 2–5 tướng được khai phá', a.team_compositions_count, b.team_compositions_count], ['Đội hình có itemset WIN', a.winning_team_compositions_count, b.winning_team_compositions_count]].forEach(values => { const row = body.insertRow(); values.forEach(value => { row.insertCell().textContent = String(value); }); });
      $('comparisonNote').textContent = `Cùng ${data.parameters.total_transactions} transaction; Support=${data.parameters.min_support}, Confidence=${data.parameters.min_confidence}, Lift=${data.parameters.min_lift}, tối đa ${data.parameters.max_heroes} tướng. Thời gian là lượt chạy hiện tại.`;
      const overlap = data.composition_overlap, root = $('compositionComparison'); root.replaceChildren();
      [['Có ở cả hai', overlap.common], ['Chỉ Apriori', overlap.apriori_only], ['Chỉ FP-Growth', overlap.fpgrowth_only]].forEach(([title, entries]) => {
        const col = document.createElement('div'); col.className = 'col-lg-4'; const card = document.createElement('div'); card.className = 'card card-custom p-3 h-100'; const heading = document.createElement('h6'); heading.textContent = `${title} (${entries.length})`; card.append(heading);
        const list = document.createElement('ul'); list.className = 'small mb-0'; entries.slice(0, 15).forEach(entry => { const li = document.createElement('li'); li.textContent = entry.label; list.append(li); });
        if (!entries.length) { const empty = document.createElement('p'); empty.className = 'text-secondary small'; empty.textContent = 'Không có tổ hợp.'; card.append(empty); } else card.append(list);
        if (entries.length > 15) { const more = document.createElement('small'); more.className = 'text-secondary'; more.textContent = `Còn ${entries.length - 15} tổ hợp.`; card.append(more); }
        col.append(card); root.append(col);
      });
      charts.forEach(chart => chart.destroy()); charts = [];
      chart('timeChart', 'giây', a.execution_time_sec, b.execution_time_sec); chart('itemsetChart', 'tập', a.frequent_itemsets_count, b.frequent_itemsets_count); chart('ruleChart', 'luật', a.total_rules_count, b.total_rules_count);
      $('comparisonResults').classList.remove('d-none');
    } catch (error) { $('cmpError').textContent = error.message; $('cmpError').classList.remove('d-none'); }
    finally { $('runComparison').disabled = false; $('cmpLoading').classList.add('d-none'); }
  });
});
